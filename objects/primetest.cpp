#include <Python.h>
#include <vector>
#include "../include/utils.h"


static bool _test(uintmax_t n, uintmax_t base, uintmax_t s, uintmax_t t) {
	// Miller-Rabin strong pseudoprime test for one base.
	PyObject* base_obj = PyLong_FromUnsignedLongLong(base);
	PyObject* t_obj = PyLong_FromUnsignedLongLong(t);
	PyObject* n_obj = PyLong_FromUnsignedLongLong(n);
	PyObject* two = PyLong_FromUnsignedLongLong(2);
	PyObject* b_obj = PyNumber_Power(base_obj, t_obj, n_obj);
	PyObject* temp;
	uintmax_t b = PyLong_AsUnsignedLongLong(b_obj);
	bool ret = false;

	if (b == 1 || b == n - 1)
		ret = true;
	else for (uintmax_t j = 1; j < s; j++) {
		temp = PyNumber_Power(b_obj, two, n_obj);
		Py_DECREF(b_obj);
		b_obj = temp;

		uintmax_t b = PyLong_AsUnsignedLongLong(b_obj);
		if (b == n - 1) {
			ret = true;
			break;
		}
		if (b == 1)
			break;
	}
	Py_DECREF(base_obj);
	Py_DECREF(t_obj);
	Py_DECREF(n_obj);
	Py_DECREF(two);
	Py_DECREF(b_obj);

	return ret;
}


static bool mr(uintmax_t n, vector<uintmax_t> bases) {
	if (n < 2) return false;

	uintmax_t s = trailing(n - 1);
	uintmax_t t = n >> s;

	for (uintmax_t base : bases) {
		if (base >= n) base %= n;
		if (base >= 2) {
			if (!_test(n, base, s, t)) return false;
		}
	}
	
	return true;
}


bool isprime(uintmax_t n) {
	// Step 1, do quick composite testing via trial division.
	if (n == 2 || n == 3 || n == 5)
		return true;

	if (n < 2 || (n % 2) == 0 || (n % 3) == 0 || (n % 5) == 0)
		return false;

	if (n < 49)
		return true;

	if ((n % 7) == 0 || (n % 11) == 0 || (n % 13) == 0 || (n % 17) == 0 ||
		(n % 19) == 0 || (n % 23) == 0 || (n % 29) == 0 || (n % 31) == 0 ||
		(n % 37) == 0 || (n % 41) == 0 || (n % 43) == 0 || (n % 47) == 0)
		return false;

	if (n < 2809)
		return true;

	if (n <= 23001)
		return ipow(2, n, n) == 2 && (n != 7957 && n != 8321 && n != 13747 && n != 18721 && n != 19951);

	// Step 2: deterministic Miller-Rabin testing for numbers < 2^64
	if (n < 341531)
		return mr(n, { 9345883071009581737 });
	if (n < 885594169)
		return mr(n, { 725270293939359937, 3569819667048198375 });
	if (n < 350269456337)
		return mr(n, { 4230279247111683200, 14694767155120705706, 16641139526367750375 });
	if (n < 55245642489451)
		return mr(n, {2, 141889084524735, 1199124725622454117, 11096072698276303650});
	if (n < 7999252175582851)
		return mr(n, { 2, 4130806001517, 149795463772692060, 186635894390467037, 3967304179347715805 });
	if (n < 585226005592931977)
		return mr(n, { 2, 123635709730000, 9233062284813009, 43835965440333360, 761179012939631437, 1263739024124850375 });
	if (n <= 18446744073709551615)
		return mr(n, { 2, 325, 9375, 28178, 450775, 9780504, 1795265022 });

	// If we make it to this point, we are passed the range of 64-bit numbers
	// TODO: Implement passed here
	return false;
}


static PyObject* method_isprime(PyObject* self, PyObject* args) {
	uintmax_t n = 0;

	/* Parse arguments */
	if (!PyArg_ParseTuple(args, "K", &n)) {
		return NULL;
	}

	if (isprime(n)) {
		Py_RETURN_TRUE;
	}
	else {
		Py_RETURN_FALSE;
	}
}


static PyMethodDef PrimetestMethods[] = {
	{"isprime", method_isprime, METH_VARARGS, "C method to test primality"},
	{NULL, NULL, 0, NULL}
};


static struct PyModuleDef primetestmodule = {
	PyModuleDef_HEAD_INIT,
	"primetest",
	"C helper methods for testing primality",
	-1,
	PrimetestMethods
};


PyMODINIT_FUNC PyInit_primetest(void) {
	return PyModule_Create(&primetestmodule);
}
