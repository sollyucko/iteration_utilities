/******************************************************************************
 * Licensed under Apache License Version 2.0 - see LICENSE
 *****************************************************************************/

static PyObject *
PyIU_AllIsinstance(PyObject *m,
                   PyObject *args,
                   PyObject *kwargs)
{
    static char *kwlist[] = {"iterable", "types", NULL};
    PyObject *iterable;
    PyObject *types;

    PyObject *iterator;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OO:all_isinstance", kwlist,
                                     &iterable, &types)) {
        return NULL;
    }

    iterator = PyObject_GetIter(iterable);
    if (iterator == NULL) {
        return NULL;
    }

    for (;;) {
        int ok;
        PyObject *item = Py_TYPE(iterator)->tp_iternext(iterator);
        if (item == NULL) {
            break;
        }

        ok = PyObject_IsInstance(item, types);
        Py_DECREF(item);

        if (ok != 1) {
            Py_DECREF(iterator);
            if (ok == 0) {
                Py_RETURN_FALSE;
            } else {
                return NULL;
            }
        }
    }

    Py_DECREF(iterator);

    if (PyErr_Occurred()) {
        if (PyErr_ExceptionMatches(PyExc_StopIteration)) {
            PyErr_Clear();
        } else {
            return NULL;
        }
    }

    Py_RETURN_TRUE;
}
