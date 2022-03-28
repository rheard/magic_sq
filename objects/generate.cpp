#include <Python.h>
#include "../include/generate.h"
#include "../include/primetest.h"


uintmax_t nextprime(uintmax_t n) {
    // Get the next prime greater than n
    if (n < 2) return 2;
    if (n < 7) {
        switch (n) {
            case 2: return 3;
            case 3:
            case 4: return 5;
            case 5:
            case 6: return 7;
        }
    }

    uintmax_t nn = 6 * (n / 6);
    if (nn == n) {
        n += 1;
        if (isprime(n)) return n;
        n += 4;
    }
    else if (n - nn == 5) {
        n += 2; 
        if (isprime(n)) return n;
        n += 4;
    }
    else n = nn + 5;

    for (;;) {
        if (isprime(n)) return n;
        n += 2;
        if (isprime(n)) return n;
        n += 4;
    }
}


static PyObject* method_nextprime(PyObject* self, PyObject* args) {
    uintmax_t n = 0;

    /* Parse arguments */
    if (!PyArg_ParseTuple(args, "K", &n)) {
        return NULL;
    }

    n = nextprime(n);

    return PyLong_FromUnsignedLongLong(n);
}


PrimeRange::PrimeRange(uintmax_t a, uintmax_t b)
{
    this->a = a - 1;
    this->b = b;
}

PrimeRange::PrimeRange(uintmax_t b)
{
    this->a = 1;
    this->b = b;
}

uintmax_t PrimeRange::next() {
    if (this->a == 0 || this->a >= this->b) {
        return 0;
    }

    this->a = nextprime(this->a);
    if (this->a < this->b) return this->a;
    else return 0;
}


typedef struct {
    PyObject_HEAD
    uintmax_t a;
    uintmax_t b;
} PyPrimeRange;


PyObject* PyPrimeRange_iter(PyObject* self)
{
    Py_INCREF(self);
    return self;
}


PyObject* PyPrimeRange_iternext(PyObject* self)
{
    PyPrimeRange* p = (PyPrimeRange*)self;
    if (p->a != 0 && p->a < p->b) {
        p->a = nextprime(p->a);
        if (p->a < p->b)
            return PyLong_FromUnsignedLongLong(p->a);
    }

    /* Raising of standard StopIteration exception with empty value. */
    PyErr_SetNone(PyExc_StopIteration);
    return NULL;
}


static PyTypeObject PyPrimeRangeType = {
    PyObject_HEAD_INIT(NULL)
    "generate.PrimeRange",     /*tp_name*/
    sizeof(PyPrimeRange),       /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
    0,                         /*tp_vectorcall_offset*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_as_async*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,
    /* tp_flags: Py_TPFLAGS_HAVE_ITER tells python to
       use tp_iter and tp_iternext fields. */
    "A generator for primes in a range",  /* tp_desc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare */
    0,  /* tp_weaklistoffset */
    PyPrimeRange_iter,  /* tp_iter: __iter__() method */
    PyPrimeRange_iternext  /* tp_iternext: next() method */
};


static PyObject* method_primerange(PyObject* self, PyObject* args) {
    uintmax_t a, b = 0;

    /* Parse arguments */
    if (!PyArg_ParseTuple(args, "K|K", &a, &b)) {
        return NULL;
    }

    if (!b) {
        b = a;
        a = 2;
    }

    PyPrimeRange*p = PyObject_New(PyPrimeRange, &PyPrimeRangeType);
    if (!p) return NULL;

    /* I'm not sure if it's strictly necessary. */
    if (!PyObject_Init((PyObject*)p, &PyPrimeRangeType)) {
        Py_DECREF(p);
        return NULL;
    }

    p->a = a - 1;
    p->b = b;
    return (PyObject*)p;
}


static PyMethodDef GenerateMethods[] = {
    {"next_prime", method_nextprime, METH_VARARGS, "C method to get the next prime after n"},
    {"primerange", method_primerange, METH_VARARGS, "C method to get primes in a certain range"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef generatemodule = {
    PyModuleDef_HEAD_INIT,
    "generate",
    "C helper methods for generating primes",
    -1,
    GenerateMethods
};


PyMODINIT_FUNC PyInit_generate(void) {
    return PyModule_Create(&generatemodule);
}
