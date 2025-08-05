from unittest import TestCase

from sympy import primerange

from magic_sq import decompose_number, decompose_prime


class TestPrimeDecomposition(TestCase):

    def test_primes_below_1000(self):
        for i in primerange(1000):
            if i % 4 != 1:
                continue

            with self.subTest(p=i):
                x, y = decompose_prime(i)
                self.assertEqual(i, x**2 + y**2)

    def test_high_range(self):
        for i in primerange(2**63 + 1, 2**63 + 1001):
            if i % 4 != 1:
                continue

            with self.subTest(p=i):
                x, y = decompose_prime(i)
                self.assertEqual(i, x**2 + y**2)


class TestNumberDecomposition(TestCase):

    def test_primes_below_1000(self):
        for i in range(1000):
            with self.subTest(n=i):
                for x, y in decompose_number(i):
                    self.assertEqual(i, x**2 + y**2)

    def test_outside_range(self):
        for i in range(2**63 + 1, 2**63 + 1001):
            with self.subTest(n=i):
                for x, y in decompose_number(i):
                    self.assertEqual(i, x**2 + y**2)
