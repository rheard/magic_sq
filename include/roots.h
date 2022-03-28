#pragma once

#include <Python.h>
#include <tuple>

using namespace std;

void integer_nthroot(uintmax_t y, uintmax_t n, tuple<uintmax_t, bool>& output);

uintmax_t isqrt(uintmax_t n);
