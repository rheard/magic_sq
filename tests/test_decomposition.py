from unittest import TestCase

from sympy import primerange

from magic_sq import decompose_number, decompose_prime


class TestPrimeDecomposition(TestCase):
    """Tests for decompose_prime"""

    def test_primes_below_1000(self):
        """Verify small primes"""

        for i in primerange(1000):
            if i % 4 != 1:  # Primes that are not 1 mod 4 will produce an error (see source for decompose_prime)
                continue

            with self.subTest(p=i):
                x, y = decompose_prime(i)
                self.assertEqual(i, x**2 + y**2)

    def test_high_range(self):
        """Verify large primes"""

        for i in primerange(2**31 + 1, 2**31 + 1001):
            if i % 4 != 1:
                continue

            with self.subTest(p=i):
                x, y = decompose_prime(i)
                self.assertEqual(i, x**2 + y**2)


class TestNumberDecomposition(TestCase):
    """Tests for decompose_number"""

    def test_numbers_below_1000(self):
        """Verify small numbers"""

        for i in range(1000):
            with self.subTest(n=i):
                for x, y in decompose_number(i):
                    self.assertEqual(i, x**2 + y**2)

    def test_outside_range(self):
        """Verify large numbers"""

        for i in range(2**31 + 1, 2**31 + 1001):
            with self.subTest(n=i):
                for x, y in decompose_number(i):
                    self.assertEqual(i, x**2 + y**2)
