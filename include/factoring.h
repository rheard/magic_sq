#pragma once

#include <Python.h>
#include <unordered_map>

using namespace std;

typedef unordered_map<uintmax_t, uintmax_t> factormap;

void factorint(uintmax_t n, factormap& factors, uintmax_t limit);
void factorint(uintmax_t n, factormap& factors);
