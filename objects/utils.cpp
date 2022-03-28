#include <Python.h>
#include <intrin.h>
#include <tuple>
#include <unordered_map>
#include <list>

using namespace std;

struct pair_hash
{
    template <class T1, class T2>
    std::size_t operator() (const std::pair<T1, T2>& pair) const {
        return std::hash<T1>()(pair.first) ^ std::hash<T2>()(pair.second);
    }
};


uintmax_t __inline trailing(uintmax_t value)
{
    unsigned long trailing_zero = 0;

    if (_BitScanForward64(&trailing_zero, value))
        return trailing_zero;
    else
        return 0;
}


uintmax_t ipow(uintmax_t x, uintmax_t p)
{
    if (p == 0) return 1;
    if (p == 1) return x;

    uintmax_t tmp = ipow(x, p / 2);
    if (p % 2 == 0) return tmp * tmp;
    else return x * tmp * tmp;
}


uintmax_t ipow(uintmax_t a, uintmax_t b, uintmax_t m)
{
    uintmax_t res = 1;
    a %= m;
    while (b > 0)
    {
        if (b & 1) {
            res = (res * a) % m;
            b--;
        }

        a = (a * a) % m;
        b >>= 1;
    }
    return res;
}


uintmax_t multiplicity(uintmax_t p, uintmax_t n) {
    if (p == 2)
        return trailing(n);
    else if (p == n)
        return 1;

    uintmax_t m = 0;
    uintmax_t rem = n % p;
    n /= p;
    while (!rem) {
        m += 1;
        if (m > 5) {
            uintmax_t e = 2;
            while (true) {
                uintmax_t ppow = ipow(p, e);
                if (ppow < n) {
                    uintmax_t nnew = n / ppow;
                    rem = n % ppow;
                    if (!rem) {
                        m += e;
                        e *= 2;
                        n = nnew;
                        continue;
                    }
                }
                return m + multiplicity(p, n);
            }
        }

        rem = n % p;
        n /= p;
    }

    return m;
}

uintmax_t gcd(uintmax_t u, uintmax_t v) {
    while (v != 0) {
        uintmax_t r = u % v;
        u = v;
        v = r;
    }
    return u;
}

intmax_t gcd(intmax_t u, intmax_t v) {
    if (u < 0) {
        return gcd((uintmax_t)-u, (uintmax_t)v);
    }
    return gcd((uintmax_t)u, (uintmax_t)v);
}


static PyObject* method_ipow(PyObject* self, PyObject* args) {
    uintmax_t a, b, m;

    /* Parse arguments */
    if (!PyArg_ParseTuple(args, "KKK", &a, &b, &m)) {
        return NULL;
    }

    return PyLong_FromUnsignedLongLong(ipow(a, b, m));
}


static PyMethodDef UtilMethods[] = {
    {"ipow", method_ipow, METH_VARARGS, "Integer power with modulo"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef utilmodule = {
    PyModuleDef_HEAD_INIT,
    "utils",
    "Utilities for magic_sq problem",
    -1,
    UtilMethods
};


PyMODINIT_FUNC PyInit_utils(void) {
    return PyModule_Create(&utilmodule);
}

