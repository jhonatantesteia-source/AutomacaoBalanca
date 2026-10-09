import unittest

from src.config import parse_callmebot_destinatarios


class TestParseCallmebotDestinatarios(unittest.TestCase):
    def test_lista_vazia(self):
        self.assertEqual(parse_callmebot_destinatarios(""), [])

    def test_varios_destinatarios(self):
        self.assertEqual(
            parse_callmebot_destinatarios("5511999999999:abc, 5511888888888:def"),
            [
                {"telefone": "5511999999999", "apikey": "abc"},
                {"telefone": "5511888888888", "apikey": "def"},
            ],
        )

    def test_configuracao_invalida(self):
        with self.assertRaises(ValueError):
            parse_callmebot_destinatarios("telefone-sem-chave")


if __name__ == "__main__":
    unittest.main()
