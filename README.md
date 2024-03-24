This is a library to tackle the magic square of squares problem, which infamously led to the Parker Square.

## Overview

This project aims to find a magic square of squares, specifically a bimagic square of order 3.
 The goal is to identify a 3x3 square where each row, column, and both main diagonals sum to the same value `k`, 
 and each cell contains a square number.

### Problem Model

The magic square of squares we are looking for can be represented as:

```markdown
  +-----+-----+-----+
  | a^2 | b^2 | c^2 |
  +-----+-----+-----+
  | d^2 | e^2 | f^2 |
  +-----+-----+-----+
  | g^2 | h^2 | i^2 |
  +-----+-----+-----+
```

To start to understand this, first lets build a list of equations that are used in this problem:

```
(Rows)
a^2 + b^2 + c^2 = k
d^2 + e^2 + f^2 = k
g^2 + h^2 + i^2 = k

(Columns)
a^2 + d^2 + g^2 = k
b^2 + e^2 + h^2 = k
c^2 + f^2 + i^2 = k

(Diagonals)
a^2 + e^2 + i^2 = k
c^2 + e^2 + g^2 = k
```

Additionally we will say that complex/imaginary numbers are defined by using `j` such as `a+bj`. 
    This is Python notation.

### Solution Approach

Looking at this I first noted that you could set `a^2 + b^2 + c^2 = a^2 + d^2 + g^2` (or some rotation), 
    and remove `a^2` from both sides to get `b^2 + c^2 = d^2 + g^2`

In other words there are a lot of symmetries that can be used to produce these equalities of sums of square numbers.
    A way to shortcut this problem could be finding co-equal pairs of numbers that satisfy this equality. 

It quickly stood out that the best way to join them up would be to join them in the middle using `e` 
    since that is the most important variable in the equations above, 
    instead of trying to join the solutions along an edge.

So: If I could find 4 sums of squares that are all unique and equal to some value `k` (more on this below), 
    they can be arranged in the problem around the center as so:

```markdown
4 co-equal pairs: (a1, a2), (b1, b2), (c1, c2), (d1, d2)

a1^2 b1^2 c1^2
d1^2 e^2  d2^2
c2^2 b2^2 a2^2
```

There are some swappings to handle all rotations, but doing this method will guarantee the following 4 directions
    are already co-equal:

```markdown
a1^2 + e^2 + a2^2 (diagonal)
c1^2 + e^2 + c2^2 (diagonal)
b1^2 + e^2 + b2^2 (center)
d1^2 + e^2 + d2^2 (middle)
```

Futher, we can compute `e` using the top row by doing `e = sqrt((a1^2 + b1^2 + c1^2) - (d1^2 + d2^2))`
    This will also ensure that the top row's value (`a^2 + b^2 + c^2`) will match the above 4 values too.

Thus by following this method we can easily generate solutions that are guaranteed 
    to be correct in 5 out of 8 directions.

The next step is simply to verify the remaining 3 directions for any potential solutions. They are:

```markdown
a^2 + d^2 + g^2 (left column)
c^2 + f^2 + i^2 (right column)
g^2 + h^2 + i^2 (bottom row)
```

I have only added a check for the bottom row however, and to date, 
    no potential solutions have made it passed that point...

### Finding co-equal sums of squares

Hopefully now you can see how I've broken this problem down into finding at least 4 co-equal sums of squares, 
    so that they can be arranged as described above.

This is actually a fairly interesting problem and I was able to find a deterministic algorithm to do this.
    The first step is to factor a number which will be the sum of the squares. Since factoring is not efficient 
    this is the slowest step of this process.

An algorithm was proposed by Stan Wagon (1990), based on work by Serret and Hermite (1848), and Cornacchia (1908),
    which uses Euclid's algorithm to decompose prime numbers of the form `p = 4k - 1` (or prime `p = 1 mod 4`).

For composite numbers the process is much longer involving complex numbers. Throughout here I will be using the example
    of 65. 65 factors into 5 * 13. Note that each exponent `f` is 1.

An upper bound for the number of solutions can be calculated by multiplying the exponents together such as 
    `(f_1 + 1) * (f_2 + 1) * ...`. This allows us to estimate that 65 will have at most (1 + 1) * (1 + 1) = 4 solutions,
    and is eligible for the magic square of square problem.

There are some checks to pass such as if the factoring contains any primes which are 3 mod 4, 
    and those primes have an odd exponent, there are no solutions. 

65 does not have any primes which are 3 mod 4, and it does not have a 2's component.

If it did have a 2's component `2^k`, we would start by defining a complex base which is `(1-1j) ^ k`. 
    For now our complex base will be `(1-1j)^0` which reduces to just `1`.

Additionally for each prime which is 3 mod 4: 
    For each one `p^k`, take `-p*j ^ max(k // 2, 1)`. That is for the prime `p^k`, 
    `-p` defines the complex part, which is then raised to `max(k // 2, 1)`, where `//` is integer division (floor).
    Each of these is then multiplied with the complex base. 
    Since 65 has no primes which are 3 mod 4, the complex base remains the multiplicative identity `1`.

For the remaining primes which are 1 mod 4, decompose them using the above method with 
    Euclid's algorithm proposed by Stan Wagon (1990). Each one `p^k = x^2 + y^2` will then produce 2 complex numbers:
    `x+yj` and `x-yj`. Each of these is then multiplied by the complex base, producing a tree of possible solutions.
    HOWEVER: The first prime which is 1 mod 4 does NOT produce 2 complex numbers.

This is quite confusing. Lets see how this works for 65. Firstly we decompose each prime which is 1 mod 4:
```markdown
5 = 1^2 + 2^2
13 = 2^2 + 3^2
```

1. Starting with 5, we get the single complex number `1+2j` (because 5 is the first prime which is 1 mod 4)
2. Multiplying that by the existing solution space (the complex base `1`) and the new solution space is `1+2j`.
3. Now with 13, we get the complex numbers `2+3j` and `2-3j`.
4. Multiplying these across the solution space,
```markdown
1+2j * 2+3j = -4 + 7j
1+2j * 2-3j = 8 + 1j
```

This gives our 2 solutions for 65: `4^2 + 7^2` and `8^2 + 1^2`. Incredible!!

Again, for the magic square of squares problem we need at least 4 solutions, 
    and solutions using the number 1 don't count.
