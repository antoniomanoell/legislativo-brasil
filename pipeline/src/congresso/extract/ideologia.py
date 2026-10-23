"""Estimativas da BLS (Zucco & Power), no Harvard Dataverse, licença CC0 (SOURCES.md).

As tabelas publicadas de Bolognesi et al. não estão no dataset (que só traz microdados) e por isso
ficam transcritas em data/manual/bolognesi_2022.csv.
"""

from pathlib import Path

from congresso.extract.http import baixar
from congresso.paths import BRUTOS

# Arquivo `bls9_estimates_partiespresidents_long` (id 7186804) do dataset doi:10.7910/DVN/6KVTUV.
URL_BLS = "https://dataverse.harvard.edu/api/access/datafile/7186804?format=original"


def bls(*, atualizar: bool = False) -> Path:
    return baixar(URL_BLS, BRUTOS / "ideologia" / "bls9_estimates_long.csv", atualizar=atualizar)
