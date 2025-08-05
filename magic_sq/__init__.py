import math

from functools import lru_cache

from itertools import combinations, product

from sympy.ntheory import factorint


def euclids_algorithm(a, b, c):
    """Runs Euclid's algorithm and yields remainders"""
    first = None
    while a != 1:
        r = a % b
        a, b = b, r
        if r > c:
            continue
        if not r:
            return None
        if first is not None:
            return r, first
        first = r


@lru_cache
def decompose_prime(p):
    """
    Decompose a prime number into a**2 + b**2

    There will be at most 1 solution for primes, but only if the prime is equal 1 mod 4 according
        to Fermat's theorem on sums of two squares.

    This is based on the algorithm described by Stan Wagon (1990),
        based on work by Serret and Hermite (1848), and Cornacchia (1908)

    Returns:
        tuple<int, int>: a and b
    """
    if p % 4 != 1:
        raise ValueError(f'Could not decompose {p!r}')

    p_sqrt = math.isqrt(p)
    for a in range(1, p):  # a must be co-prime to p
        if pow(a, (p - 1) // 2, p) == p - 1:
            # Found a quadratic non-residue of p! (a)
            #   Now run the Euclidean algorithm with a and p
            res = euclids_algorithm(p, pow(a, (p - 1) // 4, p), p_sqrt)
            if res:
                return res


def decompose_number(n, check_count=None, limited_checks=False):
    """
    Decompose any number into all the possible x**2 + y**2 solutions

    There may be many solutions. 

    Args:
        n (int, dict): The number to decompose. Can be an integer which will be factored,
            or the already factored number.
        check_count (int): If provided, and it is predicted that a number will have fewer than this many solutions,
            that number is skipped and an empty list is returned instead.
        limited_checks (bool): Only run limited checks. Should only be used with prepared input
            or false positive will appear.

    Returns:
        list<tuple<int, int>>: All unique solutions (x, y)
    """

    # Step 1: Factor n. This is the most time consuming step, especially on larger numbers. Avoid if possible
    if isinstance(n, dict):
        factors = n
    else:
        factors = factorint(n)

    # Look for shortcuts
    if len(factors) == 1 and sum(factors.values()) == 1:
        p = next(iter(factors))
        if check_count and check_count > 1:
            return set()  # There will only be 1 solution. If check_count is greater than that, do nothing
        if p % 4 != 1:
            return set()  # Primes == 1 mod 4 have no solutions

        # n is a prime number with only 1 factor. Return its simple decomposition...
        return {decompose_prime(p)}

    # Divide the factors into the ones equivalent to 1 mod 4, and 3 mod 4:
    p_1, p_3 = dict(), dict()
    for p, k in factors.items():
        p_mod_4 = p % 4
        if p_mod_4 == 1:
            p_1[p] = k
        elif p_mod_4 == 3:
            p_3[p] = k

    if not limited_checks and any(k % 2 == 1 for k in p_3.values()):
        # There is a prime == 3 mod 4 and at least one has an odd exponent, so no results
        return set()

    if not p_1:
        # There aren't any primes = 1 mod 4, in which case, escape to no results
        return set()

    if check_count and math.prod(f + 1 for f in p_1.values()) < check_count:
        # Provided a check_count and the expected number of results is less than that
        #   expected number = (f_1 + 1) * (f_2 + 1) * ...
        #   where f is an exponent of a prime = 1 mod 4 in the factorization
        return set()

    two_power = factors.get(2, 0)  # 2 is a special case. Get that exponent
    factors = p_1  # Convenience. These are the only factors we care about going forward...

    # Handle the primes == 3 mod 4: For each one p^k, take -p*j ** max(k // 2, 1), 
    #   then multiply that all together
    p_3_coefficients = math.prod(complex(imag=-p)**max(k // 2, 1) for p, k in p_3.items())

    p_decompositions = {p: decompose_prime(p) for p in factors}
    # Here we create the a+bj and a-bj pairs...
    p_decompositions = {p: (complex(*d), complex(d[0], -d[1])) for p, d in p_decompositions.items()}
    # p_decompositions = {p: complex(*d) for p, d in p_decompositions.items()}
    first_p = next(iter(factors))
    factors[first_p] -= 1  # subtract 1 for the base item

    p_3_coefficients *= (1-1j)**two_power  # Add the 2's power special case to the p_3_coefficients for later...
    base_item = p_decompositions[first_p][0]  # Base item only needs the positive value (a+bj) and doesn't need to vary
    base_item *= p_3_coefficients  # Add the previously calculated p_3 coefficients (including the 2's power)
    found = set()
    for choices in product([0, 1], repeat=sum(factors.values())):  # This will run ONCE if repeat=0
        # Initial total for this loop with the base item
        total = base_item
        choice_i = 0
        for p, k in factors.items():
            # Get a choice for each factor, on whether to use (a+bj) or (a-bj) here...
            for _ in range(k):
                plus_or_minus = choices[choice_i]
                total *= p_decompositions[p][plus_or_minus]
                choice_i += 1
        # The following float -> int conversions worry me...
        # TODO: Convert to gmpy2 or mpmath? Which use extended precision complex numbers
        sol = tuple(sorted((int(abs(total.real)), int(abs(total.imag)))))
        if sol[0] == sol[1]:
            continue  # Skip symmetrical solutions with repeat numbers (a**2 + a**2)
        if any(x == 0 for x in sol):
            continue  # Skip solutions containing 0
        found.add(sol)
    return found


def test(i, show_puzzles=False, limited_checks=False):
    """Test all values of a**2 + b**2 = i"""
    solutions = decompose_number(i, 4, limited_checks)

    if isinstance(i, dict) and solutions:
        i = math.prod(k**v for k, v in i.items())

    for (a1, a2), (b1, b2), (c1, c2), (d1, d2) in combinations(solutions, 4):
        # FOR NOW I'm going to act as if the center was symmetrical.
        #   We can check more symmetry later when we start check the left/right columns
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
