#include <stdio.h>
#include <stdlib.h>
#include <Python.h>
#include <tuple>
#include <unordered_map>
#include <iostream>
#include <math.h>
#include <algorithm>
#include <random>

#include "../include/roots.h"
#include "../include/utils.h"
#include "../include/factoring.h"
#include "../include/primetest.h"
#include "../include/generate.h"

using namespace std;


const uintmax_t _2__15 = ipow(2, 15);
const uintmax_t _10__25 = ipow(10, 25);


static void _factorint_small(factormap& factors, uintmax_t n, uintmax_t limit, uintmax_t fail_max, tuple<uintmax_t, uintmax_t>& output) {
    uintmax_t d = 2;
    uintmax_t m = trailing(n);

    if (m) {
        factors[d] = m;
        n >>= m;
    }

    d = 3;
    if (limit < d) {
        if (n > 1)
            factors[n] = 1;

        if (d * d <= n)
            output = { n, d }; 
        else
            output = { n, 0 };

        return;
    }

    m = 0;
    while (n % d == 0) {
        n /= d;
        m += 1;
        if (m == 20) {
            uintmax_t mm = multiplicity(d, n);
            m += mm;
            n /= ipow(d, mm);
            break;
        }
    }

    if (m)
        factors[d] = m;

    uintmax_t maxx = (limit*limit > n) ? 0 : limit*limit;
    uintmax_t dd = (maxx) ? maxx : n;
    d = 5;
    uintmax_t fails = 0;

    while (fails < fail_max) {
        if (d*d > dd) break;

        m = 0;
        while (n % d == 0) {
            n /= d;
            m += 1;
            if (m == 20) {
                uintmax_t mm = multiplicity(d, n);
                m += mm;
                n /= ipow(d, mm);
                break;
            }
        }

        if (m) {
            factors[d] = m;
            dd = (maxx) ? maxx : n;
            fails = 0;
        } else
            fails += 1;

        d += 2;
        if (d*d > dd)
            break;

        m = 0;
        while (n % d == 0) {
            n /= d;
            m += 1;
            if (m == 20) {
                uintmax_t mm = multiplicity(d, n);
                m += mm;
                n /= ipow(d, mm);
                break;
            }
        }

        if (m) {
            factors[d] = m;
            dd = (maxx) ? maxx : n;
            fails = 0;
        } else
            fails += 1;

        d += 4;
    }

    if (d*d <= n)
        output = { n, d };
    else
        output = { n, 0 };
}


static bool perfect_power(uintmax_t n, tuple<uintmax_t, uintmax_t>& output) {
    if (n <= 3) return false;

    long double logn = log2l(n);
    uintmax_t max_possible = logn;
    max_possible += 2;
    bool not_square = ((n % 10) == 2 || (n % 10) == 3 || (n % 10) == 7 || (n % 10) == 8);
    uintmax_t min_possible = 2 + not_square;
    PrimeRange candidates(min_possible, max_possible);
    uintmax_t e;

    while (e = candidates.next()) {
        if (logn / e < 40) {
            long double b = pow(2, logn / e);
            if (abs((uintmax_t)(b + 0.5) - 0.5) > 0.01) continue;
        }

        tuple<uintmax_t, bool> ret;
        integer_nthroot(n, e, ret);
        uintmax_t r = get<0>(ret);
        if (get<1>(ret)) {
            tuple<uintmax_t, uintmax_t> ret2;
            if (perfect_power(r, ret2)) {
                r = get<0>(ret2);
                e *= get<1>(ret2);
            }
            output = { r, e };
            return true;
        }
    }

    return false;
}


static bool _check_termination(factormap& factors, uintmax_t n, uintmax_t limitp1) {
    tuple<uintmax_t, uintmax_t> p;
    if (perfect_power(n, p)) {
        uintmax_t base = get<0>(p);
        uintmax_t exp = get<1>(p);
        uintmax_t limit = (limitp1) ? limitp1 - 1 : limitp1;
        factormap facs;

        factorint(base, facs, limit);
        for (const std::pair<uintmax_t, uintmax_t>& f : facs) {
            factors[f.first] = exp * f.second;
        }

        return true;
    }

    if (isprime(n)) {
        factors[n] = 1;
        return true;
    }

    if (n == 1) return true;

    return false;
}


static void _trial(factormap& factors, uintmax_t n, PrimeRange& candidates, tuple<uintmax_t, bool>& output) {
    uintmax_t nfactors = factors.size();
    uintmax_t d;

    while (d = candidates.next()) {
        if (n % d == 0) {
            uintmax_t m = multiplicity(d, n);
            n /= ipow(d, m);
            factors[d] = m;
        }
    }

    output = { n, factors.size() != nfactors };
}


static void _trial(factormap& factors, uintmax_t n, factormap& candidates, tuple<uintmax_t, bool>& output) {
    uintmax_t nfactors = factors.size();
    uintmax_t d;

    for (const std::pair<uintmax_t, uintmax_t>& f : candidates) {
        d = f.first;
        if (n % d == 0) {
            uintmax_t m = multiplicity(d, n);
            n /= ipow(d, m);
            factors[d] = m;
        }
    }

    output = { n, factors.size() != nfactors };
}


static uintmax_t pollard_pm1(uintmax_t n, uintmax_t B = 10, uintmax_t a = 2, uintmax_t retries = 0, uintmax_t seed = 1234, bool verbose = false) {
    random_device r;
    default_random_engine eng{ (unsigned int)(seed + B) };
    PyObject* temp;
    PyObject* n_obj = PyLong_FromUnsignedLongLong(n);

    for (uintmax_t i = 0; i < retries + 1; i++) {
        PyObject* aM_obj = PyLong_FromUnsignedLongLong(a);
        uintmax_t p;
        PrimeRange pr(2, B + 1);
        while (p = pr.next()) {
            uintmax_t e = log(B) / log(p);
            PyObject* exp_obj = PyLong_FromUnsignedLongLong(ipow(p, e));
            temp = PyNumber_Power(aM_obj, exp_obj, n_obj);
            Py_DECREF(aM_obj);
            Py_DECREF(exp_obj);
            aM_obj = temp;
        }

        uintmax_t aM = PyLong_AsUnsignedLongLong(aM_obj);
        uintmax_t g = gcd(aM - 1, n);

        if (1 < g && g < n) {
            return g;
        }

        uniform_int_distribution<uintmax_t> uni(2, n - 2);
        a = uni(eng);
    }

    return 0;
}


PyObject* F_default(PyObject* x, PyObject* n, PyObject* a) {
    PyObject* two = PyLong_FromUnsignedLongLong(2);
    PyObject* powered = PyNumber_Power(x, two, n);
    PyObject* temp = PyNumber_Add(powered, a);
    PyObject* ret = PyNumber_Remainder(temp, n);
    Py_DECREF(two);
    Py_DECREF(powered);
    Py_DECREF(temp);
    return ret;
}


static uintmax_t pollard_rho(uintmax_t n, uintmax_t s = 2, uintmax_t a = 1, uintmax_t retries = 5, uintmax_t seed = 1234, uintmax_t max_steps = 0, PyObject* F(PyObject*, PyObject*, PyObject*) = nullptr) {
    random_device r;
    default_random_engine eng{ (unsigned int)(seed + retries) };
    PyObject* V = PyLong_FromUnsignedLongLong(s);
    PyObject* n_obj = PyLong_FromUnsignedLongLong(n);
    PyObject* a_obj = PyLong_FromUnsignedLongLong(a);
    uintmax_t ret = 0;
    PyObject* temp;

    for (uintmax_t i = 0; i < retries + 1; i++) {
        PyObject* U = PyLong_FromUnsignedLongLong(PyLong_AsUnsignedLongLong(V));
        if (F == nullptr) F = F_default;
        for (uintmax_t j = 0; !max_steps || j <= max_steps; j++) {
            temp = F(U, n_obj, a_obj);
            Py_DECREF(U);
            U = temp;

            temp = F(V, n_obj, a_obj);
            Py_DECREF(V);
            V = temp;

            temp = F(V, n_obj, a_obj);
            Py_DECREF(V);
            V = temp;

            uintmax_t g = gcd(PyLong_AsLongLong(U) - PyLong_AsLongLong(V), (intmax_t)n);
            if (g == 1) continue;
            if (g == n) break;

            ret = g;
            break;
        }

        if (ret) break;

        uniform_int_distribution<uintmax_t> uni(0, n - 1);
        temp = PyLong_FromUnsignedLongLong(uni(eng));
        Py_DECREF(V);
        V = temp;
        uniform_int_distribution<uintmax_t> uni2(1, n - 3);
        temp = PyLong_FromUnsignedLongLong(uni2(eng));
        Py_DECREF(a_obj);
        a_obj = temp;
        F = nullptr;
    }
    Py_DECREF(V);
    Py_DECREF(n_obj);
    Py_DECREF(a_obj);
    return ret;
}


void factorint(uintmax_t n, factormap& factors, uintmax_t limit) {
    if (limit && limit < 2) {
        if (n == 1) {
            factors = {};
            return;
        }
        factors = { {n, 1} };
        return;
    }
    else if (n < 10) {
        switch (n) {
            case 0: factors = { {0, 1} }; return;
            case 1: factors = {}; return;
            case 2: factors = { {2, 1} }; return;
            case 3: factors = { {3, 1} }; return;
            case 4: factors = { {2, 2} }; return;
            case 5: factors = { {5, 1} }; return;
            case 6: factors = { {2, 1}, {3, 1} }; return;
            case 7: factors = { {7, 1} }; return;
            case 8: factors = { {2, 3} }; return;
            case 9: factors = { {3, 2} }; return;
        }
    }

    tuple<uintmax_t, uintmax_t> ret;
    uintmax_t small = _2__15;
    if (limit) 
        small = min(small, limit);
    _factorint_small(factors, n, small, 600, ret);
    n = std::get<0>(ret);
    uintmax_t next_p = std::get<1>(ret);

    if (next_p == 0) {
        if (n > 1) {
            factors[n] = 1;
        }
        return;
    }

    // continue with more advanced factorization methods

    if (limit && next_p > limit) {
        if (_check_termination(factors, n, limit)) return;

        if (n > 1) factors[n] = 1;
        return;
    }

    uintmax_t sqrt_n = isqrt(n);
    uintmax_t a = sqrt_n += 1;
    uintmax_t a2 = ipow(a, 2);
    uintmax_t b;
    uintmax_t b2 = a2 - n;
    tuple<uintmax_t, bool> output;
    bool fermat;
    for (uintmax_t i = 0; i < 3; i++) {
        integer_nthroot(b2, 2, output);
        b = get<0>(output);
        fermat = get<1>(output);
        if (fermat) break;
        b2 += 2 * a + 1;
        a += 1;
    }
    if (fermat) {
        // TODO: Merge these two r choices into a for loop using... something
        if (limit) limit--;
        uintmax_t r = a - b;
        factormap facs;
        factorint(r, facs, limit);
        for (const std::pair<uintmax_t, uintmax_t>& v : facs) {
            factors[v.first] += v.second;
        }

        r = a + b;
        facs.clear();
        factorint(r, facs, limit);
        for (const std::pair<uintmax_t, uintmax_t>& v : facs) {
            factors[v.first] += v.second;
        }
        return;
    }

    if (_check_termination(factors, n, limit)) return;

    uintmax_t low = next_p;
    uintmax_t high = 2 * next_p;

    if (!limit) limit = sqrt_n;
    limit += 1;
    uintmax_t iteration = 0;
    for (;;) {
        uintmax_t high_ = high;
        if (limit < high_) high_ = limit;

        // TODO: This actually uses sieve.primerange. I now see why the sieve code exists everywhere that I've been ignoring...
        //  I _might_ implement that, but it was probably the reason why the Python version took over 11GB after running all night
        PrimeRange ps(low, high_);
        tuple<uintmax_t, bool> ret2;
        _trial(factors, n, ps, ret2);
        n = get<0>(ret2);
        bool found_trial = get<1>(ret2);
        if (found_trial && _check_termination(factors, n, limit)) {
            return;
        }

        if (high > limit) {
            if (n > 1) factors[n] = 1;
            return;
        }

        // Only used advanced methods when no small factors were found
        if (!found_trial) {
            uintmax_t high_root = max((uintmax_t)log(pow(high, 0.7)), low);
            if (high_root < 3) high_root = 3;

            // Pollard p-1
            uintmax_t c = pollard_pm1(n, high_root, 2, 0, high_, iteration == 0);
            if (c) {
                factormap ps;
                factorint(c, ps, limit - 1);
                _trial(factors, n, ps, output);
                n = get<0>(output);
                if (_check_termination(factors, n, limit)) return;
            }

            // Pollard rho
            uintmax_t max_steps = high_root;
            c = pollard_rho(n, 2, 1, 1, high_, max_steps);
            if (c) {
                factormap ps;
                factorint(c, ps, limit - 1);
                _trial(factors, n, ps, output);
                n = get<0>(output);
                if (_check_termination(factors, n, limit)) return;
            }
        }

        iteration++;
        if (iteration >= 3 && n >= _10__25) break;
        low = high;
        high *= 2;
    }

    uintmax_t B1 = 10000;
    uintmax_t B2 = 100 * B1;
    uintmax_t num_curves = 50;

    // TODO: Very advanced stuff
    PyErr_SetString(PyExc_NotImplementedError, "Haven't implemented very advanced factoring methods");
    return;
}

void factorint(uintmax_t n, factormap& factors) {
    factorint(n, factors, 0);
}


static PyObject *method_factorint(PyObject *self, PyObject *args) {
    uintmax_t n = 0;

    /* Parse arguments */
    if(!PyArg_ParseTuple(args, "K", &n)) {
        return NULL;
    }

    factormap r;
    factorint(n, r);

    PyObject* return_data = PyDict_New();
    vector<pair<uintmax_t, uintmax_t>> elems(r.begin(), r.end());
    sort(elems.begin(), elems.end());
    for( const pair<uintmax_t, uintmax_t>& v : elems) {
        PyDict_SetItem(return_data, PyLong_FromUnsignedLongLong(v.first), PyLong_FromUnsignedLongLong(v.second));
    }
    return return_data;
}


static PyMethodDef FactoringMethods[] = {
    {"factorint", method_factorint, METH_VARARGS, "C method to factor integers, similar to sympy's version"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef factoringmodule = {
    PyModuleDef_HEAD_INIT,
    "factoring",
    "C helper methods for factoring",
    -1,
    FactoringMethods
};


PyMODINIT_FUNC PyInit_factoring(void) {
    return PyModule_Create(&factoringmodule);
}
