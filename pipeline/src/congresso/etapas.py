"""Etapas do pipeline, na ordem em que rodam. Cada uma lê de data/raw (baixando se preciso),
grava em data/processed e escreve suas conferências em reports/."""

from datetime import date

import polars as pl

from congresso.extract import camara, tse
from congresso.extract import ideologia as fontes_ideologia
from congresso.load.site import publicar as gravar_site
from congresso.load.site import publicar_governos
from congresso.paths import MANUAIS, PROCESSADOS, PUBLICADOS, RELATORIOS
from congresso.transform import governos as gov
from congresso.transform import ideologia as ideo
from congresso.transform.eleitos import ler_1990, ler_consulta_cand, ler_vagas
from congresso.transform.fotos import foto, ler_eventos
from congresso.transform.partidos import atribuir_partido, atribuir_partido_camara
from congresso.validate.eleitos import conferir_limites, conferir_referencia, conferir_vagas


class FalhaDeValidacao(Exception):
    """Uma conferência obrigatória falhou: o pipeline para e nada é publicado."""


def eleitos(*, atualizar: bool = False) -> None:
    """Deputados federais eleitos de 1990 a 2026 (TSE, situação atual)."""
    partes, vagas = [], []
    for ano in tse.ANOS:
        zip_cand = tse.candidatos(ano, atualizar=atualizar)
        partes.append(ler_1990(zip_cand) if ano == 1990 else ler_consulta_cand(zip_cand, ano))
        vagas.append(ler_vagas(tse.vagas(ano, atualizar=atualizar), ano))
    tabela = pl.concat(partes)

    # O arquivo de vagas de 1994 não traz deputado federal (o TSE avisa que 1994–1998 estão
    # incompletos): nesses anos, só total (LC 78/1993) e limites por UF (CF, art. 45).
    vagas = [v for v in vagas if v.height]
    sem_vagas = sorted(set(tse.ANOS) - {v["ano"][0] for v in vagas})
    problemas = conferir_vagas(tabela, pl.concat(vagas))
    for ano in sem_vagas:
        print(f"  aviso: {ano} sem vagas de deputado federal no TSE; conferido só total e limites")
        problemas += conferir_limites(tabela, ano, total=513)
    if problemas:
        raise FalhaDeValidacao("Eleitos não batem com as vagas do TSE:\n" + "\n".join(problemas))

    mapa = pl.read_csv(
        MANUAIS / "partidos_tse.csv", schema_overrides={"ano": pl.Int16, "nr_partido": pl.String}
    )
    try:
        tabela = atribuir_partido(tabela, mapa)
    except ValueError as erro:
        raise FalhaDeValidacao(str(erro)) from erro
    PROCESSADOS.mkdir(parents=True, exist_ok=True)
    tabela.write_parquet(PROCESSADOS / "eleitos.parquet")

    referencia = pl.read_csv(
        MANUAIS / "bancadas_referencia.csv", schema_overrides={"ano": pl.Int16}
    )
    divergencias = conferir_referencia(tabela, referencia)
    RELATORIOS.mkdir(parents=True, exist_ok=True)
    divergencias.write_csv(RELATORIOS / "eleitos_x_apendice_a.csv")
    fora = divergencias.filter("fora_da_tolerancia")
    print(f"eleitos: {tabela.height} linhas; {divergencias.height} divergências com o Apêndice A")
    for r in fora.iter_rows(named=True):
        print(
            f"  ALERTA {r['ano']} {r['sigla_partido']}: TSE {r['tse']}, "
            f"Apêndice A {r['referencia']} (investigar)"
        )


# Eleição que formou cada legislatura com histórico datado.
ELEICAO_DA_LEGISLATURA = {52: 2002, 53: 2006, 54: 2010, 55: 2014, 56: 2018, 57: 2022}
PRIMEIRA_FOTO, TOTAL_CADEIRAS = 2003, 513


def fotos(*, atualizar: bool = False) -> None:
    """Deputados em exercício em 1º/fev de cada ano, de 2003 até o ano corrente (Câmara)."""
    ids: set[int] = set()
    for leg in camara.LEGISLATURAS_COM_HISTORICO:
        caminho = camara.deputados_da_legislatura(leg, atualizar=atualizar)
        ids |= {d["id"] for d in pl.read_json(caminho).iter_rows(named=True)}
    eventos = ler_eventos(camara.historicos(sorted(ids), atualizar=atualizar))

    ultimo_ano = max(eventos["data_hora"]).year
    dias = [date(a, 2, 1) for a in range(PRIMEIRA_FOTO, ultimo_ano + 1)]
    tabela = pl.concat([foto(eventos, d) for d in dias])
    try:
        tabela = atribuir_partido_camara(tabela, pl.read_csv(MANUAIS / "partidos_camara.csv"))
    except ValueError as erro:
        raise FalhaDeValidacao(str(erro)) from erro

    # Conferências (PROJECT.md, 10.1): ninguém duas vezes na mesma foto; nenhuma UF acima das vagas.
    if tabela.select("data", "id_deputado").is_duplicated().any():
        raise FalhaDeValidacao("Deputado repetido numa foto")
    vagas = pl.concat(
        [
            ler_vagas(tse.vagas(ano, atualizar=atualizar), ano).with_columns(
                pl.lit(leg).alias("legislatura")
            )
            for leg, ano in ELEICAO_DA_LEGISLATURA.items()
        ]
    ).drop("ano")
    por_uf = (
        tabela.group_by("data", "legislatura", "uf")
        .len("em_exercicio")
        .join(vagas, on=["legislatura", "uf"], how="left")
    )
    acima = por_uf.filter(pl.col("em_exercicio") > pl.col("vagas"))
    if acima.height:
        raise FalhaDeValidacao(f"UF com mais deputados em exercício que vagas: {acima.rows()}")

    PROCESSADOS.mkdir(parents=True, exist_ok=True)
    tabela.write_parquet(PROCESSADOS / "fotos.parquet")
    resumo = (
        por_uf.group_by("data")
        .agg(pl.col("em_exercicio").sum(), pl.col("vagas").sum().alias("cadeiras"))
        .with_columns((pl.col("cadeiras") - pl.col("em_exercicio")).alias("sem_exercicio"))
        .sort("data")
    )
    resumo.write_csv(RELATORIOS / "fotos_cadeiras.csv")
    print(f"fotos: {len(dias)} datas ({dias[0]} a {dias[-1]}); {tabela.height} linhas")
    for r in resumo.filter(pl.col("sem_exercicio") > 0).iter_rows(named=True):
        print(
            f"  {r['data']}: {r['em_exercicio']} em exercício, {r['sem_exercicio']} cadeiras vagas"
        )


# Legislatura de cada eleição (a eleição de ano A forma a legislatura que começa em A + 1).
LEGISLATURA_DA_ELEICAO = {1990 + 4 * i: 49 + i for i in range(10)}


def ideologia(*, atualizar: bool = False) -> None:
    """Pontuação ideológica por partido e legislatura (BLS 49ª–56ª; Bolognesi 2022 57ª–58ª)."""
    siglas = pl.read_csv(
        MANUAIS / "ideologia_siglas.csv", schema_overrides={"ano_medicao": pl.Int16}
    )
    tabela = pl.concat(
        [
            ideo.de_bls(pl.read_csv(fontes_ideologia.bls(atualizar=atualizar)), siglas),
            ideo.de_bolognesi(pl.read_csv(MANUAIS / "bolognesi_2022.csv"), siglas),
        ]
    ).sort("legislatura", "partido_id")
    problemas = ideo.conferir(tabela)
    if problemas:
        raise FalhaDeValidacao("Ideologia:\n" + "\n".join(problemas))
    tabela.write_parquet(PROCESSADOS / "ideologia.parquet")

    # Cobertura: % das cadeiras (eleitos e fotos) cujo partido não tem pontuação na legislatura.
    eleitos = pl.read_parquet(PROCESSADOS / "eleitos.parquet").select(
        pl.col("ano").cast(pl.String).alias("visao"),
        pl.col("ano").replace_strict(LEGISLATURA_DA_ELEICAO).cast(pl.Int16).alias("legislatura"),
        "partido_id",
    )
    fotos_ = pl.read_parquet(PROCESSADOS / "fotos.parquet").select(
        pl.col("data").cast(pl.String).alias("visao"),
        pl.col("legislatura").cast(pl.Int16),
        "partido_id",
    )
    cobertura = (
        pl.concat([eleitos, fotos_])
        .join(
            tabela.select("legislatura", "partido_id", "pontuacao"),
            on=["legislatura", "partido_id"],
            how="left",
        )
        .group_by("visao", "legislatura")
        .agg(
            pl.len().alias("cadeiras"),
            pl.col("pontuacao").is_null().sum().alias("nao_classificadas"),
        )
        .with_columns(
            (100 * pl.col("nao_classificadas") / pl.col("cadeiras")).round(1).alias("pct")
        )
        .sort("visao")
    )
    cobertura.write_csv(RELATORIOS / "ideologia_cobertura.csv")
    print(f"ideologia: {tabela.height} pontuações; cadeiras não classificadas por visão:")
    for r in cobertura.iter_rows(named=True):
        print(
            f"  {r['visao']} ({r['legislatura']}ª): "
            f"{r['nao_classificadas']} de {r['cadeiras']} ({r['pct']}%)"
        )


def publicar(*, atualizar: bool = False) -> None:
    """JSON para o site em web/public/data, a partir das tabelas processadas e curadas."""
    catalogo = gravar_site(
        eleitos=pl.read_parquet(PROCESSADOS / "eleitos.parquet"),
        fotos=pl.read_parquet(PROCESSADOS / "fotos.parquet"),
        ideologia=pl.read_parquet(PROCESSADOS / "ideologia.parquet"),
        partidos=pl.read_csv(MANUAIS / "partidos.csv"),
        renomeacoes=pl.read_csv(MANUAIS / "renomeacoes.csv"),
        linhagens=pl.read_csv(MANUAIS / "linhagens.csv"),
        destino=PUBLICADOS,
    )
    if (PROCESSADOS / "base_governo.parquet").exists():
        gabinetes = gov.ler_gabinetes(pl.read_csv(MANUAIS / "gabinetes_ipea.csv"))
        fim = FIM_IPEA
        if (MANUAIS / "gabinetes_pos2020.csv").exists():
            extra = pl.read_csv(MANUAIS / "gabinetes_pos2020.csv")
            gabinetes = pl.concat([gabinetes, gov.ler_gabinetes(extra)]).sort("inicio")
            fim = date.fromisoformat(str(extra["cobertura_ate"].max()))
        publicar_governos(
            governos=pl.read_csv(MANUAIS / "governos.csv", try_parse_dates=True),
            gabinetes=gabinetes,
            base=pl.read_parquet(PROCESSADOS / "base_governo.parquet"),
            inicio_gabinetes=pl.read_csv(RELATORIOS / "base_inicio_gabinetes.csv"),
            fim_cobertura=fim.isoformat(),
            destino=PUBLICADOS,
        )
    tamanho = sum(p.stat().st_size for p in PUBLICADOS.rglob("*.json"))
    print(
        f"publicar: {len(catalogo['momentos'])} momentos; {tamanho / 1024:.0f} KB em {PUBLICADOS}"
    )


# A Nota Técnica 53 cobre "o período de março de 1985 a dezembro de 2020". Depois disso, só com a
# curadoria própria (data/manual/gabinetes_pos2020.csv); sem ela, a base fica sem dados.
FIM_IPEA = date(2020, 12, 31)


def governos(*, atualizar: bool = False) -> None:
    """Base formal de governo (partidos com ministério) em cada foto de 1º/fev e no início de
    cada gabinete desde 2003, com as cadeiras desses partidos."""
    gabinetes = gov.ler_gabinetes(pl.read_csv(MANUAIS / "gabinetes_ipea.csv"))
    fim_cobertura = FIM_IPEA
    pos2020 = MANUAIS / "gabinetes_pos2020.csv"
    if pos2020.exists():
        extra = pl.read_csv(pos2020)
        gabinetes = pl.concat([gabinetes, gov.ler_gabinetes(extra)]).sort("inicio")
        fim_cobertura = date.fromisoformat(str(extra["cobertura_ate"].max()))
    governos_tab = pl.read_csv(MANUAIS / "governos.csv", try_parse_dates=True)

    def governo_em(dia: date) -> str | None:
        g = governos_tab.filter((pl.col("inicio") <= dia) & (pl.col("fim") >= dia))
        return g["governo_id"][0] if g.height else None

    fotos_ = pl.read_parquet(PROCESSADOS / "fotos.parquet")
    linhas = []
    for (dia,), grupo in fotos_.sort("data").group_by("data", maintain_order=True):
        if dia > fim_cobertura:
            b = {"data": dia, "gabinete": None, "partidos": [], "cadeiras_base": None}
            b["ocupadas"] = grupo.height
        else:
            try:
                b = gov.base_formal(grupo, gabinetes, dia)
            except ValueError as erro:
                raise FalhaDeValidacao(str(erro)) from erro
        linhas.append({**b, "governo_id": governo_em(dia), "momento": dia.isoformat()})
    base = pl.DataFrame(linhas)
    base.write_parquet(PROCESSADOS / "base_governo.parquet")

    # Composição no início de cada gabinete desde 2003 (o histórico datado da Câmara começa na
    # posse de 01/02/2003), para conferir com os percentuais citados pelo IPEA (§7.5).
    eventos = ler_eventos(camara.PASTA / "historico")
    mapa = pl.read_csv(MANUAIS / "partidos_camara.csv")
    conferencia = []
    for g in gabinetes.filter(pl.col("inicio") >= date(2003, 1, 1)).iter_rows(named=True):
        if g["inicio"] > fim_cobertura:
            continue
        # Gabinete que começa em janeiro de ano de posse da Câmara (1º/fev): a comparação é com a
        # legislatura que vai trabalhar com ele, não com a que está saindo.
        dia = g["inicio"]
        if dia.month == 1 and dia.year in {2003, 2007, 2011, 2015, 2019, 2023}:
            dia = date(dia.year, 2, 1)
        compo = atribuir_partido_camara(foto(eventos, dia), mapa)
        na_base = compo.filter(pl.col("partido_id").is_in(g["partidos"])).height
        conferencia.append(
            {
                "gabinete": g["gabinete"],
                "data_calculo": dia,
                "so_mes": g["so_mes"],
                "partidos": ";".join(g["partidos"]),
                "cadeiras_base": na_base,
                "em_exercicio": compo.height,
                "pct_base": round(100 * na_base / 513, 1),
            }
        )
    pl.DataFrame(conferencia).write_csv(RELATORIOS / "base_inicio_gabinetes.csv")
    print(
        f"governos: base em {base.filter(pl.col('gabinete').is_not_null()).height} fotos "
        f"(até {fim_cobertura}); {len(conferencia)} gabinetes conferidos desde 2003"
    )
