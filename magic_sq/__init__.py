import math

from itertools import combinations, product

from sympy.ntheory import factorint

from magic_sq.decomposing import decompose_number as cppdecompose_number


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


def decompose_prime(p):
    """
    Decompose a prime number into a**2 + b**2

    There will only be 1 solution for primes.

    This is based on the algorithm described by Stan Wagon (1990),
        based on work by Serret and Hermite (1848), and Cornacchia (1908)

    Returns:
        tuple<int, int>: a and b
    """
    p_sqrt = math.isqrt(p)
    for a in range(1, p):  # a must be co-prime to p
        if pow(a, (p - 1) // 2, p) == p - 1:
            # Found a quadratic non-residue of p! (a)
            #   Now run the Euclidean algorithm with a and p
            res = euclids_algorithm(p, pow(a, (p - 1) // 4, p), p_sqrt)
            if res:
                return res
    raise ValueError(f'Could not decompose {p!r}')


def decompose_number(n, check_count=None):
    """
    Decompose any number into all the possible x**2 + y**2 solutions

    There may be many solutions. 

    Args:
        n (int): The number to decompose.
        check_count (int): If provided, and it is predicted that a number will have fewer than this many solutions,
            that number is skipped and an empty list is returned instead.

    Returns:
        list<tuple<int, int)>>: All unique solutions (x, y)
    """

    # Step 1: Factor n. This is the most time consuming step, especially on larger numbers
    factors = factorint(n)
    
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

    if any(k % 2 == 1 for k in p_3.values()) or not p_1:
        # There is a prime == 3 mod 4 and at least one has an odd exponent, so no results
        #   OR there aren't any primes = 1 mod 4, in which case, escape to no results
        return set()

    if check_count and math.prod(f + 1 for f in p_1.values()) < check_count:
        # Provided a check_count and the expected number of results is less than that
        #   expected number = (f_1 + 1) * (f_2 + 1) * ... where f is an exponent of a prime = 1 mod 4 in the factorization
        return set()

    two_power = factors.get(2, 0)  # 2 is a special case. Get that exponent
    factors = p_1  # Convience. These are the only factors we care about going forward...

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
            continue  # Skip symmetirical solutions with repeat numbers (a**2 + a**2)
        if any(x == 0 for x in sol):
            continue  # Skip solutions containing 0
        found.add(sol)
    return found


def test(i, cpp=True):
    """Test all values of a**2 + b**2 = i"""
    if cpp:
        solutions = cppdecompose_number(i, 4)
    else:
        solutions = decompose_number(i, 4)

    # Now go through all the combinations of the new pair with 3 other co-equal pairs
    for (a1, a2), (b1, b2), (c1, c2), (d1, d2) in combinations(solutions, 4):
        # FOR NOW I'm going to act as if the center was symmetrical. We can check more symmetry later when we start check the left/right columns
        out_d, out_f = d1, d2

        # Try all the different arraigements of these 4 pairs in a square (excluding any symmetries)
        for out_a, out_b, out_c, out_i, out_h, out_g in (
                    (a1, b1, c1, a2, b2, c2),
                    (a2, b1, c1, a1, b2, c2),
                    (a1, b2, c1, a2, b1, c2),
                    (a1, b1, c2, a2, b2, c1),
                ):
            # We're going to compute the central value from the top row
            target_val = out_a**2 + out_b**2 + out_c**2
            out_e_sq = target_val - i  # central value, squared
            if out_e_sq <= 0:
                continue  # e is less than 1 (not valid)
            if (out_g**2 + out_h**2 + out_i**2) != target_val:
                continue  # bottom row mismatch
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
