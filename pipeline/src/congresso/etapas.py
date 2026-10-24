"""Etapas do pipeline, na ordem em que rodam. Cada uma lê de data/raw (baixando se preciso),
grava em data/processed e escreve suas conferências em reports/."""

import json
from datetime import date

import polars as pl

from congresso.extract import camara, camara_votacoes, tse
from congresso.extract import ideologia as fontes_ideologia
from congresso.extract import senado as fonte_senado
from congresso.load.site import publicar as gravar_site
from congresso.load.site import publicar_2027, publicar_governos
from congresso.load.site import publicar_senado as gravar_senado
from congresso.load.votacoes_site import publicar_impeachments, publicar_indicadores
from congresso.load.votacoes_site import publicar_votacoes as gravar_votacoes
from congresso.paths import MANUAIS, PROCESSADOS, PUBLICADOS, RELATORIOS
from congresso.transform import congresso_2027 as c27
from congresso.transform import governos as gov
from congresso.transform import ideologia as ideo
from congresso.transform import materias
from congresso.transform import senado as sen
from congresso.transform import votacoes as vot
from congresso.transform.eleitos import ler_1990, ler_consulta_cand, ler_vagas
from congresso.transform.fotos import foto, intervalos_de_exercicio, legislatura_em, ler_eventos
from congresso.transform.partidos import atribuir_partido, atribuir_partido_camara
from congresso.ufs import UFS_27
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


def votacoes(*, atualizar: bool = False) -> None:
    """Votações nominais de plenário desde 2001: votos com partido, presença, governismo, coesão."""

    ultimo = date.today().year
    caminhos = camara_votacoes.todos(ultimo, atualizar=atualizar)
    lista_v, lista_votos = [], []
    for ano in range(camara_votacoes.PRIMEIRO_ANO, ultimo + 1):
        v, vt = vot.ler_ano(
            caminhos[("votacoes", ano)],
            caminhos[("votacoesVotos", ano)],
            caminhos[("votacoesProposicoes", ano)],
            caminhos.get(("votacoesOrientacoes", ano)),
        )
        lista_v.append(v)
        lista_votos.append(vt)
    tab_v = pl.concat(lista_v, how="diagonal_relaxed")
    tab_votos = pl.concat(lista_votos, how="diagonal_relaxed").with_columns(
        pl.col("data").str.to_date()
    )
    if tab_v["id"].is_duplicated().any():
        raise FalhaDeValidacao("Votação repetida entre os arquivos anuais")

    try:
        tab_votos = atribuir_partido_camara(tab_votos, pl.read_csv(MANUAIS / "partidos_camara.csv"))
    except ValueError as erro:
        raise FalhaDeValidacao(str(erro)) from erro
    tab_votos = tab_votos.with_columns(
        pl.col("data").dt.year().alias("ano"),
        pl.col("data")
        .map_elements(legislatura_em_data, return_dtype=pl.Int16)
        .alias("legislatura"),
    )
    tab_v.write_parquet(PROCESSADOS / "votacoes.parquet")
    tab_votos.write_parquet(PROCESSADOS / "votos.parquet")

    eventos = ler_eventos(camara.PASTA / "historico")
    pres = vot.presenca(tab_votos, tab_v, intervalos_de_exercicio(eventos))
    pres.write_parquet(PROCESSADOS / "presenca.parquet")
    lacunas = pres.filter(~pl.col("pelo_historico")).join(
        tab_votos.select("id_votacao", "id_deputado", "nome", "data"),
        on=["id_votacao", "id_deputado"],
    )
    lacunas.group_by("id_deputado", "nome").agg(
        pl.len().alias("votos_sem_exercicio_no_historico"),
        pl.col("data").min().alias("primeiro"),
        pl.col("data").max().alias("ultimo"),
    ).sort("votos_sem_exercicio_no_historico", descending=True).write_csv(
        RELATORIOS / "votos_fora_do_historico.csv"
    )

    # §7.2: partido registrado no voto × partido no histórico de filiação naquele momento.
    hist = eventos.select(
        "id_deputado", "data_hora", pl.col("sigla_partido").alias("sigla_historico")
    ).sort("data_hora")
    comparacao = (
        tab_votos.filter(pl.col("data") >= date(2003, 2, 1))
        .with_columns(pl.col("data_hora_voto").str.to_datetime(strict=False).alias("quando"))
        .drop_nulls("quando")
        .sort("quando")
        .join_asof(
            hist, left_on="quando", right_on="data_hora", by="id_deputado", check_sortedness=False
        )
    )
    divergentes = comparacao.filter(
        pl.col("sigla_historico").is_not_null()
        & (pl.col("sigla_historico") != pl.col("sigla_partido"))
    )
    divergentes.group_by("id_deputado", "nome", "sigla_partido", "sigla_historico").agg(
        pl.len().alias("votos"),
        pl.col("data").min().alias("primeiro"),
        pl.col("data").max().alias("ultimo"),
    ).sort("votos", descending=True).write_csv(RELATORIOS / "divergencias_filiacao.csv")

    gov_ano = vot.governismo(tab_votos, tab_v, ["partido_id", "ano"])
    rice = vot.rice(tab_votos)
    rice.write_parquet(PROCESSADOS / "rice.parquet")
    gov_ano.write_parquet(PROCESSADOS / "governismo_partido_ano.parquet")

    excecoes = pl.read_csv(MANUAIS / "destaques_pec_excecoes.csv", infer_schema=False)
    pecs = vot.destaques_pec(tab_v, excecoes)
    tab_v.filter(pl.col("id").is_in(pecs["id"].implode())).select(
        "id", "data", pl.col("proposicoes").list.join(", "), "descricao_abertura", "descricao"
    ).sort("data").write_csv(RELATORIOS / "destaques_pec.csv")
    tab_v = tab_v.with_columns(pl.col("id").is_in(pecs["id"].implode()).alias("destaque_pec"))
    tab_v.write_parquet(PROCESSADOS / "votacoes.parquet")

    orientadas = tab_v.filter(pl.col("orientacao_governo").is_in(["Sim", "Não"])).height
    print(
        f"votacoes: {tab_v.height} votações nominais de plenário ({orientadas} com orientação "
        f"Sim/Não do Governo); {tab_votos.height} votos; presença em "
        f"{pres.height} pares deputado×votação ({pres['presente'].mean():.1%} presentes); "
        f"{lacunas.height} votos fora do histórico de exercício; "
        f"{divergentes.height} de {comparacao.height} votos com partido diferente do histórico; "
        f"{pecs.height} votações de mérito de PEC em destaque"
    )


def legislatura_em_data(dia: date) -> int:
    """Legislatura de uma data (votos de dez/2001 e 2002 são da 51ª, anterior ao histórico)."""
    return 51 if dia < date(2003, 2, 1) else legislatura_em(dia)


def publicar_votacoes(*, atualizar: bool = False) -> None:
    """Votações (arquivos anuais compactos e índice) e indicadores para o site."""
    votacoes_ = pl.read_parquet(PROCESSADOS / "votacoes.parquet")
    votos = pl.read_parquet(PROCESSADOS / "votos.parquet")
    ids = sorted(
        {m["url"].rsplit("/", 1)[1] for ms in votacoes_["materias"].to_list() for m in ms or []},
        key=int,
    )
    detalhes = materias.detalhes_camara(camara.proposicoes(ids, atualizar=atualizar), ids)
    print(f"publicar_votacoes: detalhes de {len(detalhes)} de {len(ids)} proposições")
    tamanho = gravar_votacoes(votacoes_, votos, PUBLICADOS, detalhes=detalhes)
    try:
        impeachments = publicar_impeachments(MANUAIS, PUBLICADOS)
    except ValueError as erro:
        raise FalhaDeValidacao(str(erro)) from erro
    indice_path = PUBLICADOS / "votacoes" / "indice.json"
    indice = json.loads(indice_path.read_text(encoding="utf-8"))
    indice_path.write_text(
        json.dumps(indice + impeachments, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    publicar_indicadores(
        votos,
        votacoes_,
        pl.read_parquet(PROCESSADOS / "presenca.parquet"),
        pl.read_csv(MANUAIS / "governos.csv", try_parse_dates=True),
        PUBLICADOS,
    )
    ind = (PUBLICADOS / "indicadores.json").stat().st_size
    print(f"publicar_votacoes: {tamanho / 1e6:.1f} MB de votações; indicadores {ind / 1e3:.0f} KB")


# CF, art. 46: renovação alternada de 1/3 (um senador por UF) e 2/3 (dois por UF). Em 1990, AP e RR,
# recém-transformados em estados, elegeram três senadores cada (conferido pelo arquivo de vagas).
SENADORES_POR_UF = {1994: 2, 1998: 1, 2002: 2, 2006: 1, 2010: 2, 2014: 1, 2018: 2, 2022: 1, 2026: 2}


def eleitos_senado(*, atualizar: bool = False) -> None:
    """Senadores eleitos em cada eleição (TSE, situação atual), com partido pela tabela curada."""
    partes = []
    problemas = []
    for ano in tse.ANOS:
        zip_cand = tse.candidatos(ano, atualizar=atualizar)
        e = (
            ler_1990(zip_cand, "SENADOR")
            if ano == 1990
            else ler_consulta_cand(zip_cand, ano, "SENADOR")
        )
        por_uf = dict(e.group_by("uf").len().iter_rows())
        if ano == 1990:
            esperado = dict(
                ler_vagas(tse.vagas(ano), ano, "SENADOR").select("uf", "vagas").iter_rows()
            )
        else:
            esperado = dict.fromkeys(por_uf.keys() | set(UFS_27), SENADORES_POR_UF[ano])
        for uf in sorted(esperado.keys() | por_uf.keys()):
            if por_uf.get(uf, 0) != esperado.get(uf, 0):
                problemas.append(
                    f"{ano} {uf}: {por_uf.get(uf, 0)} senadores, esperado {esperado.get(uf, 0)}"
                )
        partes.append(e)
    if problemas:
        raise FalhaDeValidacao("Senadores eleitos:\n" + "\n".join(problemas))
    tabela = pl.concat(partes)
    mapa = pl.read_csv(
        MANUAIS / "partidos_tse.csv", schema_overrides={"ano": pl.Int16, "nr_partido": pl.String}
    )
    try:
        tabela = atribuir_partido(tabela, mapa)
    except ValueError as erro:
        raise FalhaDeValidacao(str(erro)) from erro
    tabela.write_parquet(PROCESSADOS / "eleitos_senado.parquet")
    print(f"eleitos_senado: {tabela.height} senadores eleitos em {len(tse.ANOS)} eleições")


def fotos_senado(*, atualizar: bool = False) -> None:
    """Senadores em exercício em 1º/fev, só nos anos em que a fonte fecha 81 cadeiras."""
    pasta = fonte_senado.senadores(
        fonte_senado.codigos(fonte_senado.legislaturas(atualizar=atualizar)), atualizar=atualizar
    )
    exercicios, filiacoes = sen.ler_exercicios(pasta), sen.ler_filiacoes(pasta)
    mapa = pl.read_csv(MANUAIS / "partidos_senado.csv", infer_schema=False)
    validas, lacunas = [], []
    for ano in range(1991, date.today().year + 1):
        dia = date(ano, 2, 1)
        foto_ano = sen.em_exercicio(exercicios, dia)
        motivo = sen.conferir(foto_ano)
        if motivo:
            lacunas.append({"data": dia, "motivo": motivo})
            continue
        try:
            com_partido = sen.partido_na_data(foto_ano, filiacoes, mapa, dia)
        except ValueError as erro:
            raise FalhaDeValidacao(str(erro)) from erro
        validas.append(
            com_partido.with_columns(
                pl.lit(dia).alias("data"), pl.lit(legislatura_em_data(dia)).alias("legislatura")
            )
        )
    tabela = pl.concat(validas)
    tabela.write_parquet(PROCESSADOS / "fotos_senado.parquet")
    pl.DataFrame(lacunas).write_csv(RELATORIOS / "fotos_senado_lacunas.csv")
    sem_partido = tabela.filter(pl.col("partido_id") == "nao_informado").height
    print(
        f"fotos_senado: {len(validas)} fotos válidas, {len(lacunas)} anos sem foto; "
        f"{sem_partido} senadores sem filiação datada na data"
    )


def votacoes_senado(*, atualizar: bool = False) -> None:
    """Votações nominais do plenário do Senado: votos com partido, presença, governismo e coesão,
    publicados no mesmo formato compacto da Câmara (prefixo "senado")."""
    pasta = fonte_senado.votacoes(date.today().year, atualizar=atualizar)
    filiacoes = sen.ler_filiacoes(pasta)
    mapa = pl.read_csv(MANUAIS / "partidos_senado.csv", infer_schema=False)
    lista_v, lista_votos = [], []
    for ano in range(1991, date.today().year + 1):
        v, vt = sen.ler_votacoes(pasta, ano)
        lista_v.append(v)
        if vt.height:
            lista_votos.append(vt)
    tab_v = pl.concat(lista_v, how="diagonal_relaxed").unique("id", keep="first")
    tab_votos = pl.concat(lista_votos, how="diagonal_relaxed")
    try:
        tab_votos = sen.partido_nos_votos(tab_votos, filiacoes, mapa)
    except ValueError as erro:
        raise FalhaDeValidacao(str(erro)) from erro
    tab_votos = tab_votos.with_columns(
        pl.col("codigo").cast(pl.Int64).alias("id_deputado"),
        pl.col("data").dt.year().alias("ano"),
        pl.col("data")
        .map_elements(legislatura_em_data, return_dtype=pl.Int16)
        .alias("legislatura"),
        pl.when(pl.col("situacao").is_in(list(sen.PRESIDENTE)))
        .then(pl.lit("Artigo 17"))
        .otherwise(pl.col("voto"))
        .alias("voto"),
    )
    ruins = sen.votacoes_inconsistentes(tab_votos, sen.ler_mandatos(pasta))
    ruins.join(
        tab_v.select("id", "identificacao", "descricao"), left_on="id_votacao", right_on="id"
    ).write_csv(RELATORIOS / "votacoes_senado_excluidas.csv")
    tab_votos = tab_votos.filter(~pl.col("id_votacao").is_in(ruins["id_votacao"].implode()))
    tab_v = tab_v.filter(~pl.col("id").is_in(ruins["id_votacao"].implode()))
    tab_votos.write_parquet(PROCESSADOS / "votos_senado.parquet")

    contagem = tab_votos.group_by("id_votacao").agg(
        *[(pl.col("voto") == x).sum().alias(f"n_{x}") for x in vot.VOTOS_VALIDOS]
    )
    abertas = (
        tab_v.filter(~pl.col("secreta"))
        .join(contagem, left_on="id", right_on="id_votacao", how="inner")
        .with_columns(
            pl.col("data").alias("data_hora"),
            pl.lit(None, pl.String).alias("descricao_abertura"),
            pl.concat_list(pl.col("identificacao")).alias("proposicoes"),
            # Ementa e página da matéria no portal do Senado.
            pl.when(pl.col("codigo_materia").is_not_null())
            .then(
                pl.concat_list(
                    pl.struct(
                        pl.col("identificacao").alias("rotulo"),
                        pl.col("ementa"),
                        (sen.URL_MATERIA + pl.col("codigo_materia")).alias("url"),
                    )
                )
            )
            .alias("materias"),
            # A = aprovada, R = rejeitada; qualquer outro código (ou vazio) fica sem resultado.
            pl.col("resultado")
            .replace_strict({"A": "1", "R": "0"}, default=None)
            .alias("aprovacao"),
            vot.destaque_pec_senado().alias("destaque_pec"),
        )
    )
    votos_publicos = tab_votos.filter(pl.col("voto").is_not_null())
    # Votação aberta sem nenhum voto registrado (só ausências e licenças) não entra.
    sem_voto = abertas.filter(~pl.col("id").is_in(votos_publicos["id_votacao"].unique().implode()))
    abertas = abertas.join(sem_voto.select("id"), on="id", how="anti")
    # Revisão manual da regra de PEC (A5), na mesma lista de exceções da Câmara (ids "SF-").
    excecoes = pl.read_csv(MANUAIS / "destaques_pec_excecoes.csv", infer_schema=False)
    incluir = excecoes.filter(pl.col("acao") == "incluir")["id"].implode()
    excluir = excecoes.filter(pl.col("acao") == "excluir")["id"].implode()
    abertas = abertas.with_columns(
        pl.when(pl.col("id").is_in(incluir))
        .then(True)
        .when(pl.col("id").is_in(excluir))
        .then(False)
        .otherwise(pl.col("destaque_pec"))
        .alias("destaque_pec")
    )
    abertas.write_parquet(PROCESSADOS / "votacoes_senado.parquet")
    codigos = sorted(abertas["codigo_materia"].drop_nulls().unique().to_list(), key=int)
    pasta_materias = fonte_senado.materias(codigos, atualizar=atualizar)
    detalhes = materias.detalhes_senado(pasta_materias, codigos)
    tamanho = gravar_votacoes(
        abertas,
        votos_publicos,
        PUBLICADOS,
        prefixo="senado",
        nome_indice="indice-senado.json",
        detalhes=detalhes,
    )
    presenca = tab_votos.filter(pl.col("esperado")).select(
        "id_votacao", "id_deputado", pl.col("votou").alias("presente")
    )
    publicar_indicadores(
        votos_publicos,
        abertas,
        presenca,
        pl.read_csv(MANUAIS / "governos.csv", try_parse_dates=True),
        PUBLICADOS,
        nome_arquivo="indicadores-senado.json",
    )
    orientadas = abertas.filter(pl.col("orientacao_governo").is_in(["Sim", "Não"])).height
    print(
        f"votacoes_senado: {tab_v.height} votações ({abertas.height} abertas, {orientadas} com "
        f"orientação Sim/Não do Governo); {ruins.height} excluídas por lista incompatível com "
        f"os mandatos; {sem_voto.height} abertas sem voto registrado; "
        f"{votos_publicos.height} votos; {tamanho / 1e6:.1f} MB"
    )


def publicar_senado(*, atualizar: bool = False) -> None:
    """Composição do Senado para o site, com a base formal do governo em cada foto."""
    fotos_ = pl.read_parquet(PROCESSADOS / "fotos_senado.parquet")
    gabinetes = gov.ler_gabinetes(pl.read_csv(MANUAIS / "gabinetes_ipea.csv"))
    fim = FIM_IPEA
    if (MANUAIS / "gabinetes_pos2020.csv").exists():
        extra = pl.read_csv(MANUAIS / "gabinetes_pos2020.csv")
        gabinetes = pl.concat([gabinetes, gov.ler_gabinetes(extra)]).sort("inicio")
        fim = date.fromisoformat(str(extra["cobertura_ate"].max()))
    bases = {}
    for (dia,), grupo in fotos_.group_by("data"):
        if dia > fim:
            continue
        try:
            b = gov.base_formal(grupo, gabinetes, dia)
        except ValueError as erro:
            raise FalhaDeValidacao(str(erro)) from erro
        bases[dia.isoformat()] = {
            "gabinete": b["gabinete"],
            "partidos": b["partidos"],
            "cadeiras_base": b["cadeiras_base"],
        }
    cat = gravar_senado(
        pl.read_parquet(PROCESSADOS / "eleitos_senado.parquet"),
        fotos_,
        pl.read_csv(RELATORIOS / "fotos_senado_lacunas.csv", try_parse_dates=True),
        bases,
        PUBLICADOS,
    )
    print(f"publicar_senado: {len(cat['momentos'])} momentos; {len(cat['lacunas'])} anos sem foto")


def congresso_2027(*, atualizar: bool = False) -> None:
    """Composição prevista a partir de 1º/fev/2027: eleitos de 2026 mais, no Senado, as 27 cadeiras
    com mandato até 2031, com quem as ocupa na data dos dados (DECISIONS 2026-10-24)."""
    dia = date.today()
    pasta = fonte_senado.PASTA
    try:
        cadeiras = c27.cadeiras_ate_2031(pasta, dia)
    except ValueError as erro:
        raise FalhaDeValidacao(str(erro)) from erro
    situacao = c27.governadores_1o_turno(tse.candidatos(2026, atualizar=atualizar), 2026)
    completos = c27.nomes_completos(pasta)
    linhas = []
    for c in cadeiras.iter_rows(named=True):
        nome_completo = completos.get(c["ocupante_codigo"], c["ocupante_nome"])
        sit = situacao.get((c["uf"], c27.normalizar(nome_completo)))
        codigo, nome, nota = c["ocupante_codigo"], c["ocupante_nome"], None
        if c["ocupante_codigo"] != c["titular_codigo"]:
            causa = c["causa_afastamento_titular"] or "causa não registrada"
            nota = (
                f"Ocupa a vaga em definitivo: {c['titular_nome']} deixou o mandato "
                f"({causa.lower()})."
                if c27.afastamento_definitivo(causa)
                else f"Suplente em exercício na vaga de {c['titular_nome']} ({causa.lower()}); "
                "o titular pode reassumir."
            )
        if sit == "ELEITO":
            codigo, nome = c["primeiro_suplente_codigo"], c["primeiro_suplente_nome"]
            nota = f"1º suplente de {c['ocupante_nome']}, eleito governador no 1º turno de 2026."
        elif sit == "2º TURNO":
            nota = (
                f"{c['ocupante_nome']} disputa o 2º turno para governador em 25/10/2026; "
                f"se vencer, assume o 1º suplente, {c['primeiro_suplente_nome']}."
            )
        linhas.append({"codigo": codigo, "nome": nome, "uf": c["uf"], "nota": nota})
    continuam = pl.DataFrame(linhas, schema_overrides={"nota": pl.String})
    # Suplentes que nunca exerceram não estão nas listas de legislatura: baixa as filiações deles.
    fonte_senado.senadores(continuam["codigo"].to_list(), atualizar=atualizar)
    mapa = pl.read_csv(MANUAIS / "partidos_senado.csv", infer_schema=False)
    try:
        continuam = sen.partido_na_data(continuam, sen.ler_filiacoes(pasta), mapa, dia)
    except ValueError as erro:
        raise FalhaDeValidacao(str(erro)) from erro
    # Sem filiação no Senado (suplente que nunca exerceu): o partido fica "não informado", e a nota
    # diz por qual partido foi suplente em 2022 (o partido pode ter mudado ou deixado de existir).
    de_2022 = c27.suplentes_2022(tse.candidatos(2022, atualizar=atualizar))
    notas = []
    for r in continuam.iter_rows(named=True):
        nota = r["nota"]
        if r["partido_id"] == "nao_informado":
            sigla = de_2022.get((r["uf"], c27.normalizar(r["nome"] or "")), "?")
            extra = f"Sem filiação registrada no Senado; em 2022, suplente pelo {sigla}."
            nota = f"{nota} {extra}" if nota else extra
        notas.append(nota)
    continuam = continuam.with_columns(pl.Series("nota", notas, dtype=pl.String))
    eleitos_sen = pl.read_parquet(PROCESSADOS / "eleitos_senado.parquet").filter(
        pl.col("ano") == 2026
    )
    senado = pl.concat(
        [
            eleitos_sen.select(
                pl.coalesce("nome_urna", "nome").alias("nome"),
                "uf",
                pl.col("partido_id").alias("partido"),
                pl.col("sigla_na_eleicao").alias("sigla"),
                pl.lit("eleito_2026").alias("origem"),
                pl.lit(None, pl.String).alias("nota"),
            ),
            continuam.select(
                "nome",
                "uf",
                pl.col("partido_id").alias("partido"),
                pl.when(pl.col("partido_id") == "sem_partido")
                .then(pl.lit("sem partido"))
                .otherwise(pl.col("sigla").fill_null("não informado"))
                .alias("sigla"),
                pl.lit("mandato_ate_2031").alias("origem"),
                "nota",
            ),
        ]
    )
    camara = (
        pl.read_parquet(PROCESSADOS / "eleitos.parquet")
        .filter(pl.col("ano") == 2026)
        .select(
            pl.coalesce("nome_urna", "nome").alias("nome"),
            "uf",
            pl.col("partido_id").alias("partido"),
            pl.col("sigla_na_eleicao").alias("sigla"),
        )
    )
    try:
        publicar_2027(camara, senado, dia, PUBLICADOS)
    except ValueError as erro:
        raise FalhaDeValidacao(str(erro)) from erro
    notas = continuam.filter(pl.col("nota").is_not_null())
    print(f"congresso_2027: Câmara 513, Senado 81 (posição em {dia}); {notas.height} com nota:")
    for r in notas.iter_rows(named=True):
        print(f"  {r['uf']} {r['nome']}: {r['nota']}")
