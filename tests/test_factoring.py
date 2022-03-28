import unittest

from math import prod

from sympy.ntheory import factorint as py_factorint, primerange

from _factoring import factorint as cpp_factorint


class FactorIntTest(unittest.TestCase):
    """Test the C++ version of factorint"""

    def test_numbers_under_1000(self):
        for i in range(0, 1000):
            with self.subTest(n=i):
                self.assertDictEqual(py_factorint(i), cpp_factorint(i))

    def test_outside_range(self):
        factors = list(primerange(2**15 + 1, 2**15 + 20))
        i = prod(factors)
        self.assertDictEqual(py_factorint(i), cpp_factorint(i))
