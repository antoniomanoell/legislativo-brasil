"""Etapas do pipeline, na ordem em que rodam. Cada uma lê de data/raw (baixando se preciso),
grava em data/processed e escreve suas conferências em reports/."""

from datetime import date

import polars as pl

from congresso.extract import camara, tse
from congresso.paths import MANUAIS, PROCESSADOS, RELATORIOS
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
