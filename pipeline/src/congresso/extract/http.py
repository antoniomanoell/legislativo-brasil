"""Download com cache local em data/raw: só baixa de novo se o arquivo não existir ou se pedido."""

import time
from pathlib import Path

import httpx

CABECALHOS = {
    "User-Agent": "congresso-em-numeros/0.1 (pipeline de dados; github.com/antoniomanoell)"
}
TENTATIVAS = 3


def baixar(url: str, destino: Path, *, atualizar: bool = False) -> Path:
    """Baixa `url` para `destino` (escrita atômica) e devolve o caminho."""
    if destino.exists() and not atualizar:
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_name(destino.name + ".parcial")
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            with httpx.stream(
                "GET", url, headers=CABECALHOS, timeout=120, follow_redirects=True
            ) as r:
                r.raise_for_status()
                with parcial.open("wb") as f:
                    for bloco in r.iter_bytes():
                        f.write(bloco)
            parcial.replace(destino)
            return destino
        except httpx.HTTPError:
            if tentativa == TENTATIVAS:
                raise
            time.sleep(5 * tentativa)
    return destino
