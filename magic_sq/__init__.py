import math

from itertools import combinations
from twosquares import decompose_number

try:
    from .generate_factors import GenerateFactorings
except ImportError:
    from magic_sq.generate_factors import GenerateFactorings


class GenerateFactoringsMgSqSq(GenerateFactorings):
    """
    A modified version of GenerateFactorings.
        Skips all factorings that will not lead to at least 4 x**2+y**2 combinations,
        and are not relevant to the problem.
    """

    def __init__(self):
        super().__init__()

        self.two_max = 2
        self.P = dict()
        self.Q = dict()

    def next(self):
        base, i, val = super().next()

        if base == 2:
            self.two_max = i
            t = '2'
        elif base % 4 == 1:
            self.P[base] = i
            t = 'P'
        else:
            self.Q[base] = i
            t = 'Q'

        return base, i, val, t

    def _get_numbers(self, two_max, p_factorings_max, q_factorings_max):

        if two_max:
            target_key = 2
            target_key_max = two_max
            for combo in self._get_numbers(0, p_factorings_max, q_factorings_max):
                for e in range(2, target_key_max + 1):
                    yield combo | {target_key: e}

        elif p_factorings_max:
            target_key = max(p_factorings_max)
            target_key_max = p_factorings_max[target_key]
            p_factorings_max = {k: v for k, v in p_factorings_max.items() if k != target_key}

            for combo in self._get_numbers(two_max, p_factorings_max, q_factorings_max):
                for e in range(0, target_key_max + 1):
                    yield combo | {target_key: e}

        elif q_factorings_max:
            target_key = max(q_factorings_max)
            target_key_max = q_factorings_max[target_key]
            q_factorings_max = {k: v for k, v in q_factorings_max.items() if k != target_key}

            for combo in self._get_numbers(two_max, p_factorings_max, q_factorings_max):
                for e in range(0, target_key_max + 1, 2):
                    yield combo | {target_key: e}

        else:
            yield dict()
            return

    def get_numbers(self, target_P, target_Q, cur_base, cur_i):
        # We have the value for our current base, so that is not needed
        for combo in self._get_numbers(self.two_max if cur_base != 2 else 0, target_P, target_Q):
            yield combo | {cur_base: cur_i}

    def get_factorings(self):
        while True:
            cur_base, cur_i, cur_val, t = self.next()

            if t == 'Q' and cur_i % 2 == 1:
                continue

            target_P = self.P if t != 'P' else {k: v for k, v in self.P.items() if k != cur_base}
            target_Q = self.Q if t != 'Q' else {k: v for k, v in self.Q.items() if k != cur_base}
            for combo in self.get_numbers(target_P, target_Q, cur_base, cur_i):
                combo = {k: v for k, v in combo.items() if v != 0}
                if combo:
                    yield combo


def test(i, show_puzzles=False, limited_checks=False):
    """Test all values of a**2 + b**2 = i"""
    solutions = decompose_number(i, 4, limited_checks=limited_checks)

    if isinstance(i, dict) and solutions:
        i = math.prod(k**v for k, v in i.items())

    solutions = [
        s for s in solutions
        if s[0] != s[1]  # Skip symmetrical solutions with repeat numbers (a**2 + a**2)
        and all(x != 0 for x in s)  # Skip solutions containing 0
    ]

    for (a1, a2), (b1, b2), (c1, c2), (d1, d2) in combinations(solutions, 4):
        # TODO: Based on the parameterization of magic squares, I believe we only need to sort these pairs by size
        #   and then fit them to the parameterization based on size of the parameters.
        #   I haven't fully convinced myself thats something I can do tho...
        out_d, out_f = d1, d2
        a1_sq, a2_sq = a1**2, a2**2
        b1_sq, b2_sq = b1**2, b2**2
        c1_sq, c2_sq = c1**2, c2**2

        # Try all the different arrangements of these 4 pairs in a square (excluding any symmetries)
        for (out_a, out_a_sq), (out_b, out_b_sq), (out_c, out_c_sq), (out_i, out_i_sq), (out_h, out_h_sq), (out_g, out_g_sq) in (
                    ((a1, a1_sq), (b1, b1_sq), (c1, c1_sq), (a2, a2_sq), (b2, b2_sq), (c2, c2_sq)),
                    ((a2, a2_sq), (b1, b1_sq), (c1, c1_sq), (a1, a1_sq), (b2, b2_sq), (c2, c2_sq)),
                    ((a1, a1_sq), (b2, b2_sq), (c1, c1_sq), (a2, a2_sq), (b1, b1_sq), (c2, c2_sq)),
                    ((a1, a1_sq), (b1, b1_sq), (c2, c2_sq), (a2, a2_sq), (b2, b2_sq), (c1, c1_sq)),
                ):
            target_val = out_a_sq + out_b_sq + out_c_sq
            if target_val <= i:
                continue  # out_e is less than 1 (not valid)
            if out_g_sq + out_h_sq + out_i_sq != target_val:
                continue  # Bottom row doesn't equal top row

            # Nothing past here runs:
            if show_puzzles:
                print(f'{out_a:<16}**2 {out_b:<16}**2 {out_c:<16}**2')
                print(f'{out_d:<16}**2 {0:<16}**2 {out_f:<16}**2')
                print(f'{out_g:<16}**2 {out_h:<16}**2 {out_i:<16}**2')
                print()

            # region Calculate e
            out_e_sq = target_val - i  # central value, squared
            out_e = math.isqrt(out_e_sq)
            if out_e**2 != out_e_sq:
                continue  # e is not a perfect square
            # endregion

            # TODO: Check diagonols too
            ans = f'{out_a:<16}**2 {out_b:<16}**2 {out_c:<16}**2\n' \
                  f'{out_d:<16}**2 {out_e:<16}**2 {out_f:<16}**2\n' \
                  f'{out_g:<16}**2 {out_h:<16}**2 {out_i:<16}**2\n\n'
            print(f'Found solution at {i}')
            print(ans)
            with open('answer.txt', 'a') as wb:
                wb.write('ANSWER:\n')
                wb.write(ans)
                wb.write('\n')
            return ans
    return None


def multithreaded_test(i):
    """Wrapper for ThreadPool"""
    return test(i, limited_checks=True)
