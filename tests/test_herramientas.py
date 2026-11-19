import unittest
from herramientas import calculadora, ejecutar, subred, convertir_base


class PruebasHerramientas(unittest.TestCase):
    def test_calculadora_rechaza_import(self):
        resultado = calculadora({"expresion": "__import__('os').system('ls')"})
        self.assertTrue(resultado.startswith("ERROR"))

    def test_calculadora_rechaza_exponente_grande(self):
        resultado = calculadora({"expresion": "9**9**9"})
        self.assertTrue(resultado.startswith("ERROR"))

    def test_calculadora_rechaza_expresion_larga(self):
        resultado = calculadora({"expresion": "1+" + "2"*120})
        self.assertTrue(resultado.startswith("ERROR"))

    def test_subred(self):
        resultado = subred({"cidr": "192.168.1.0/26"})
        self.assertIn("hosts utilizables: 62", resultado)
        self.assertIn("255.255.255.192", resultado)

    def test_convertir_base(self):
        resultado = convertir_base({"valor": "255", "base_origen": 10, "base_destino": 2})
        self.assertEqual(resultado, "11111111")

    def test_nunca_lanza(self):
        self.assertTrue(ejecutar("desconocida", {}).startswith("ERROR"))


if __name__ == "__main__":
    unittest.main()
