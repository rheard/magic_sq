#include <stdio.h>
#include <stdlib.h>
#include <Python.h>
#include <tuple>
#include <vector>
#include <intrin.h>
#include <numeric>
#include <complex>
#include <unordered_set>
#include <bitset>
#include <iostream>

#include "../include/roots.h"
#include "../include/factoring.h"
#include "../include/utils.h"

using namespace std;

struct pair_hash
{
    template <class T1, class T2>
    std::size_t operator () (std::pair<T1, T2> const& pair) const
    {
        std::size_t h1 = std::hash<T1>()(pair.first);
        std::size_t h2 = std::hash<T2>()(pair.second);

        return h1 ^ h2;
    }
};

typedef unordered_set<pair<uintmax_t, uintmax_t>, pair_hash> solset;


static void euclids_algorithm(uintmax_t a, uintmax_t b, uintmax_t c, pair<uintmax_t, uintmax_t>& output) {
    uintmax_t first = NULL;

    while (a != 1) {
        uintmax_t r = a % b;
        a = b;
        b = r;
        if (r > c) {
            continue;
        }
        if (r == 0) {
            break;
        }
        if (first != NULL) {
            output = { r, first };
            return;
        }
        first = r;
    }
    output = { 0, 0 };
}


static void decompose_prime(uintmax_t p, pair<uintmax_t, uintmax_t>& output) {
    uintmax_t p_sqrt = isqrt(p);

    PyObject* one = PyLong_FromUnsignedLongLong(1);
    PyObject* two = PyLong_FromUnsignedLongLong(2);
    PyObject* four = PyLong_FromUnsignedLongLong(4);
    PyObject* p_obj = PyLong_FromUnsignedLongLong(p);
    PyObject* p_sub_one = PyLong_FromUnsignedLongLong(p - 1);
    PyObject* test_exp = PyNumber_FloorDivide(p_sub_one, two);
    PyObject* exp = PyNumber_FloorDivide(p_sub_one, four);

    Py_DECREF(two);
    Py_DECREF(four);

    PyObject* temp;
    for (PyObject* a = PyLong_FromUnsignedLongLong(1); PyObject_RichCompareBool(a, p_obj, Py_LT) > 0; temp = PyNumber_Add(a, one), Py_DECREF(a), a = temp) {
        
        PyObject* test_val = PyNumber_Power(a, test_exp, p_obj);
        bool test_res = PyObject_RichCompareBool(test_val, p_sub_one, Py_NE);
        Py_DECREF(test_val);
        if (test_res) {
            output = { 0, 0 };
            continue;
        }

        PyObject* b_obj = PyNumber_Power(a, exp, p_obj);
        uintmax_t b = PyLong_AsUnsignedLongLong(b_obj);
        Py_DECREF(b_obj);
        euclids_algorithm(p, b, p_sqrt, output);
        uintmax_t r1 = output.first;
        uintmax_t r2 = output.second;
        if (r1 == 0 || r2 == 0) {
            output = { 0, 0 };
            continue;
        }
        break;
    }

    Py_DECREF(one);
    Py_DECREF(p_obj);
    Py_DECREF(p_sub_one);
    Py_DECREF(test_exp);
    Py_DECREF(exp);
}


static PyObject* method_decompose_prime(PyObject* self, PyObject* args) {
    uintmax_t p = 0;

    /* Parse arguments */
    if (!PyArg_ParseTuple(args, "K", &p)) {
        return NULL;
    }

    pair<uintmax_t, uintmax_t> r;
    decompose_prime(p, r);
    uintmax_t r1 = r.first;
    uintmax_t r2 = r.second;

    if (r1 == 0 || r2 == 0) {
        PyErr_SetString(PyExc_ValueError, "Could not decompose");
        return 0;
    }

    PyObject* tup = PyTuple_New(2);
    PyTuple_SetItem(tup, 0, PyLong_FromUnsignedLongLong(r1));
    PyTuple_SetItem(tup, 1, PyLong_FromUnsignedLongLong(r2));
    return tup;
}



static void decompose_number(uintmax_t n, solset& output, uintmax_t check_count = 0) {
    /// <summary>
    /// Decompose any number into all the possible x**2 + y**2 solutions
    /// </summary>
    /// <param name="n">The number to decompose</param>
    /// <param name="output">The output solset containing all unique pairs of solutions</param>
    /// <param name="check_count">If provided, and it is predicted that a number will have fewer than this many solutions, that number is skippedand an empty list is returned instead</param>
    
    // Step 1: Factor n. This is the most time consuming step, especially on larger numbers
    factormap factors;
    factorint(n, factors);

    if (factors.size() == 1) {
        auto f = factors.begin();
        if (f->second == 1) {
            auto p = f->first;
            if ((check_count && check_count > 1)  // There will only be 1 solution. If check_count is greater than that, do nothing
                    || (p % 4 != 1)) {  // Primes == 1 mod 4 have no solutions
                output.clear();
                return;
            }

            // n is a prime number with only 1 factor. Return its simple decomposition...
            pair<uintmax_t, uintmax_t> ret;
            decompose_prime(p, ret);
            output.insert(ret);
            return;
        }
    }

    factormap p_1;
    factormap p_3;
    for (const pair<uintmax_t, uintmax_t>& f : factors) {
        uintmax_t p = f.first;
        uintmax_t k = f.second;
        if (p % 4 == 1)
            p_1[p] = k;
        else if (p % 4 == 3) {
            if (k % 2 == 1) {
                output.clear();
                return;
            }

            p_3[p] = k;
        }
    }

    if (!p_1.size()) {
        output.clear();
        return;
    }

    if (check_count && check_count > accumulate(p_1.begin(), p_1.end(), (uintmax_t)1, [](const uintmax_t previous, const pair<uintmax_t, uintmax_t>& p){ return previous * (p.second + 1); })) {
        output.clear();
        return;
    }

    uintmax_t two_power = factors[2];
    complex <intmax_t> twos_base(1, -1);
    complex <intmax_t> p_3_coefficients = 1;
    for (uintmax_t j = 0; j < two_power; j++)
        p_3_coefficients *= twos_base;
    for (const pair<uintmax_t, uintmax_t>& f : p_3) {
        auto p = f.first;
        auto k = f.second;
        complex <intmax_t> base(0, -(intmax_t)p);
        complex <intmax_t> new_base = 1;
        // base = pow(base, max(k / 2, (uintmax_t)1));
        for (uintmax_t j = 0; j < max(k / 2, (uintmax_t)1); j++) new_base *= base;
        p_3_coefficients *= new_base;
    }

    unordered_map<uintmax_t, tuple<complex<intmax_t>, complex<intmax_t>>> p_decompositions;
    uintmax_t first_p = 0, p_1_exp = 0;
    for (const pair<uintmax_t, uintmax_t>& f : p_1) {
        if (!first_p) first_p = f.first;
        pair<uintmax_t, uintmax_t> output;
        decompose_prime(f.first, output);
        p_decompositions[f.first] = { 
            { (intmax_t)output.first, (intmax_t)output.second },
            { (intmax_t)output.first, -(intmax_t)output.second }
        };

        // Also do this work while we're here
        p_1_exp += f.second;
    }
    p_1[first_p]--; p_1_exp--;  // Subtract 1 for the base item (and from the total sum)
    complex<intmax_t> base_item = get<0>(p_decompositions[first_p]);
    base_item *= p_3_coefficients;
    uintmax_t choices = 0;  // This differs from the py version in that we just use an int for combinatorics

    do {
        complex<intmax_t> total = base_item;
        uintmax_t cur_choices = choices;
        for (const pair<uintmax_t, uintmax_t>& f : p_1) {
            for (uintmax_t i = 0; i < f.second; i++) {
                uintmax_t plus_or_minus = cur_choices & 1;
                switch (plus_or_minus) {
                case 0: total *= get<0>(p_decompositions[f.first]); break;
                case 1: total *= get<1>(p_decompositions[f.first]); break;
                }
                cur_choices >>= 1;
            }
        }
        uintmax_t v1 = abs(total.real());
        uintmax_t v2 = abs(total.imag());
        if (v1 == v2) continue;  // Skip symmetrical solutions
        if (v1 == 0 || v2 == 0) continue;  // Skip solutions containing 0
        if (v1 > v2) {  // Sort
            uintmax_t temp = v1;
            v1 = v2;
            v2 = temp;
        }
        output.insert({ v1, v2 });
    } while (++choices <= (1 << p_1_exp) - 1);
}


static PyObject* method_decompose_number(PyObject* self, PyObject* args) {
    /// <summary>
    /// Translates the solset output of decompose_number into a Python set<tuple<int, int>>
    /// </summary>
    uintmax_t n, check_count = 0;

    // TODO: Make check_count a kwarg without significantly slowing this down
    if (!PyArg_ParseTuple(args, "K|K", &n, &check_count)) {
        return NULL;
    }

    // Do the work:
    solset r;
    decompose_number(n, r, check_count);

    // This code is fairly straight forward: Create a set, and for each answer create a tuple and add to the set
    PyObject* answers = PySet_New(NULL);
    for (const pair<uintmax_t, uintmax_t>& f : r) {
        PyObject* sol = PyTuple_New(2);
        PyTuple_SET_ITEM(sol, 0, PyLong_FromUnsignedLongLong(f.first));
        PyTuple_SET_ITEM(sol, 1, PyLong_FromUnsignedLongLong(f.second));
        PySet_Add(answers, sol);
    }

    return answers;
}


static PyMethodDef DecomposingMethods[] = {
    {"decompose_number", method_decompose_number, METH_VARARGS, "C method to decompose a number into x**2 + y**2"},
    {"decompose_prime", method_decompose_prime, METH_VARARGS, "C method to decompose a prime into x**2 + y**2 (for testing purposes, focus on decompose_number)"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef decomposingmodule = {
    PyModuleDef_HEAD_INIT,
    "decomposing",
    "C helper methods for decomposing numbers into a**2 + b**2 pairs",
    -1,
    DecomposingMethods
};


PyMODINIT_FUNC PyInit_decomposing(void) {
    return PyModule_Create(&decomposingmodule);
}
