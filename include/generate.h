#pragma once
#include <Python.h>

class PrimeRange
{
private:
    uintmax_t a;
    uintmax_t b;

public:
    PrimeRange(uintmax_t a, uintmax_t b);

    PrimeRange(uintmax_t b);

    uintmax_t next();
};
