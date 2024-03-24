from time import time
from unittest import TestCase

from magic_sq import test


class OverallTestMethod(TestCase):
    """Tests for the final end test method"""

    def test_performance(self):
        self.assertTrue(True)  # Just make the test pass. I'm more interested in what is logged

        start_time = time()
        for i in range(100, 10**5):
            test(i)
        end_time = time()

        print(f'Small numbers: {end_time - start_time}')

        start_time = time()
        for i in range(90*10**6, int(90.25*10**6)):
            test(i)
        end_time = time()

        print(f'Large numbers: {end_time - start_time}')
