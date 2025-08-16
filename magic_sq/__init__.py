import math

from itertools import combinations
from twosquares import decompose_number


def test(i, show_puzzles=False, limited_checks=False):
    """Test all values of a**2 + b**2 = i"""
    solutions = decompose_number(i, 4, limited_checks)

    if isinstance(i, dict) and solutions:
        i = math.prod(k**v for k, v in i.items())

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
            # We're going to compute the central value from the top row
            target_val = out_a_sq + out_b_sq + out_c_sq
            if target_val <= i:
                continue  # out_e is less than 1 (not valid)
            if show_puzzles:
                print(f'{out_a:<16}**2 {out_b:<16}**2 {out_c:<16}**2')
                print(f'{out_d:<16}**2 0**2 {out_f:<16}**2')
                print(f'{out_g:<16}**2 {out_h:<16}**2 {out_i:<16}**2')
                print()
                show_puzzles = False
            if out_g_sq + out_h_sq + out_i_sq != target_val:
                continue
            out_e_sq = target_val - i  # central value, squared
            out_e = math.isqrt(out_e_sq)
            if out_e**2 != out_e_sq:
                continue  # e is not a perfect square
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
