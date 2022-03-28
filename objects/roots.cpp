#include <Python.h>
#include <tuple>

#include "../include/utils.h"

using namespace std;

const uintmax_t _1_50 = (uintmax_t)1 << 50;


static uintmax_t isqrt_small(uintmax_t x) {
    if (x == 0) return x;

    if (x < _1_50) return pow(x, 0.5);

    uintmax_t r = (uintmax_t)(pow(x, 0.5) * 1.00000000000001) + 1;

    while (true) {
        uintmax_t y = (r + x / r) >> 1;
        if (y >= r) return r;
        r = y;
    }
}


static void sqrtrem(uintmax_t x, tuple<uintmax_t, uintmax_t>& output) {
    // TODO: Implement isqrt_fast_python and the rest of sqrtrem_python for big integers (greater than 2**600)
    uintmax_t y = isqrt_small(x);
    output = { y, x - y * y };
}


void integer_nthroot(uintmax_t y, uintmax_t n, tuple<uintmax_t, bool>& output) {
    if (y == 0 || y == 1 || n == 1) {
        output = { y, true };
        return;
    }

    if (n == 2) {
        tuple<uintmax_t, uintmax_t> ret;
        sqrtrem(y, ret);
        output = { get<0>(ret), !get<1>(ret) };
        return;
    }

    if (n > y) {
        output = { 1, false };
        return;
    }

    // TODO: Handle overflow errors for large integers
    uintmax_t guess = pow(y, 1.f / n) + 0.5;
    uintmax_t x = guess;

    if (guess > _1_50) {
        uintmax_t xprev = -1;

        for (;;) {
            uintmax_t t = pow(x, n - 1);
            xprev = x;
            x = ((n - 1) * x + y / t) / n;
            if (((x > xprev) ? (x - xprev) : (xprev - x)) < 2) break;
        }
    }

    uintmax_t t = ipow(x, n);
    while (t < y) {
        x++;
        t = ipow(x, n);
    }
    while (t > y) {
        x--;
        t = ipow(x, n);
    }
    output = { x, t == y };
}


uintmax_t isqrt(uintmax_t n) {
    tuple<uintmax_t, bool> output;
    integer_nthroot(n, 2, output);
    return get<0>(output);
}
