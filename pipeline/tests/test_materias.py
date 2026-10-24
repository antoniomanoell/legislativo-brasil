import json

from congresso.transform.materias import detalhes_camara, detalhes_senado


def test_camara_limpa_indexacao_e_guarda_inteiro_teor(tmp_path):
    (tmp_path / "10.json").write_text(
        json.dumps(
            {
                "keywords": "Reforma previdenciária (2019).  _Pol­ícia militar ,pensão.",
                "urlInteiroTeor": "https://exemplo/teor",
            }
        ),
        encoding="utf-8",
    )
    d = detalhes_camara(tmp_path, ["10", "11"])  # 11 não foi baixado: fica de fora
    assert d == {
        "https://www.camara.leg.br/propostas-legislativas/10": {
            "assuntos": "Reforma previdenciária (2019). Polícia militar, pensão",
            "inteiro_teor": "https://exemplo/teor",
        }
    }


def test_senado_temas_e_norma_gerada(tmp_path):
    materia = {
        "DetalheMateria": {
            "Materia": {
                "DadosBasicosMateria": {"IndexacaoMateria": " ESCOLHA ,  NOME ,  CARGO PUBLICO "},
                "Classificacoes": {
                    "Classificacao": {"DescricaoClasseHierarquica": "Organização do Estado"}
                },
                "NormaGerada": {
                    "IdentificacaoNorma": {
                        "DescricaoTipoNorma": "Decreto Legislativo",
                        "NumeroNorma": "00002",
                        "AnoNorma": "2023",
                        "UrlNorma": "http://legis/norma",
                    }
                },
            }
        }
    }
    (tmp_path / "7.json").write_text(json.dumps(materia), encoding="utf-8")
    d = detalhes_senado(tmp_path, ["7"])
    assert d["https://www25.senado.leg.br/web/atividade/materias/-/materia/7"] == {
        "assuntos": "ESCOLHA, NOME, CARGO PUBLICO",
        "temas": ["Organização do Estado"],
        "norma": {"rotulo": "Decreto Legislativo nº 2/2023", "url": "http://legis/norma"},
    }
