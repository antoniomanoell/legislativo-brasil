from congresso.cli import main
from congresso.paths import RAIZ


def test_fase_sem_pipeline():
    assert main(["--fase", "1"]) == 2


def test_raiz_do_repositorio():
    assert (RAIZ / "PROJECT.md").is_file()
