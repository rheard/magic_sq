#pragma once

#include <Python.h>

using namespace std;

uintmax_t __inline trailing(uintmax_t value);

uintmax_t ipow(uintmax_t x, uintmax_t p);
uintmax_t ipow(uintmax_t a, uintmax_t b, uintmax_t m);
long double ipow(long double a, long double b, long double m);

uintmax_t multiplicity(uintmax_t p, uintmax_t n);

uintmax_t gcd(uintmax_t u, uintmax_t v);
intmax_t gcd(intmax_t u, intmax_t v);
