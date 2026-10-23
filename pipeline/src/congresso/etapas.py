"""Etapas do pipeline, na ordem em que rodam. Cada uma lê de data/raw (baixando se preciso),
grava em data/processed e escreve suas conferências em reports/."""

import polars as pl

from congresso.extract import tse
from congresso.paths import MANUAIS, PROCESSADOS, RELATORIOS
from congresso.transform.eleitos import ler_1990, ler_consulta_cand, ler_vagas
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
