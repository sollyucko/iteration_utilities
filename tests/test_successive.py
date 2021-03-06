# Licensed under Apache License Version 2.0 - see LICENSE

# Built-ins
from __future__ import absolute_import, division, print_function
import operator
import pickle
import sys

# 3rd party
import pytest

# This module
import iteration_utilities

# Test helper
import helper_funcs as _hf
from helper_cls import T, toT
from helper_leak import memory_leak_decorator


successive = iteration_utilities.successive


@memory_leak_decorator()
def test_successive_empty1():
    assert list(successive([])) == []


@memory_leak_decorator()
def test_successive_empty2():
    assert list(successive([T(1)])) == []


@memory_leak_decorator()
def test_successive_empty3():
    assert list(successive([], times=10)) == []


@memory_leak_decorator()
def test_successive_empty4():
    assert list(successive([T(1), T(2), T(3)], times=10)) == []


@memory_leak_decorator()
def test_successive_normal1():
    assert (list(successive([T(1), T(2), T(3), T(4)])) ==
            [(T(1), T(2)), (T(2), T(3)), (T(3), T(4))])


@memory_leak_decorator()
def test_successive_normal2():
    assert (list(successive([T(1), T(2), T(3), T(4)], times=3)) ==
            [(T(1), T(2), T(3)), (T(2), T(3), T(4))])


@memory_leak_decorator()
def test_successive_normal3():
    assert (list(successive([T(1), T(2), T(3), T(4)], times=4)) ==
            [(T(1), T(2), T(3), T(4))])


@memory_leak_decorator()
def test_successive_normal4():
    assert (dict(successive([T(1), T(2), T(3), T(4)])) ==
            {T(1): T(2), T(2): T(3), T(3): T(4)})


@memory_leak_decorator(collect=True)
def test_successive_failure1():
    with pytest.raises(_hf.FailIter.EXC_TYP) as exc:
        successive(_hf.FailIter())
    assert _hf.FailIter.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_successive_failure2():
    with pytest.raises(ValueError):  # times must be > 0
        successive([T(1), T(2), T(3)], 0)


@memory_leak_decorator(collect=True)
def test_successive_failure3():
    # Test that a failing iterator doesn't raise a SystemError
    with pytest.raises(_hf.FailNext.EXC_TYP) as exc:
        next(successive(_hf.FailNext(), 1))
    assert _hf.FailNext.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_successive_failure4():
    # Too few arguments
    with pytest.raises(TypeError):
        successive()


@memory_leak_decorator(collect=True, offset=1)
def test_successive_failure5():
    # Changing next method
    with pytest.raises(_hf.CacheNext.EXC_TYP) as exc:
        list(successive(_hf.CacheNext(1), 3))
    assert _hf.CacheNext.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_successive_copy1():
    _hf.iterator_copy(successive(toT([1, 2, 3, 4])))


@memory_leak_decorator(collect=True)
def test_successive_failure_setstate1():
    # first argument must be a tuple
    suc = successive([T(1), T(2), T(3), T(4)], 2)
    with pytest.raises(TypeError):
        suc.__setstate__(([T(1), T(2)], ))


@memory_leak_decorator(collect=True)
def test_successive_failure_setstate2():
    # length of first argument not equal to times
    suc = successive([T(1), T(2), T(3), T(4)], 2)
    with pytest.raises(ValueError):
        suc.__setstate__(((T(1), ), ))


@memory_leak_decorator(collect=True)
def test_successive_failure_setstate3():
    # length of first argument not equal to times
    suc = successive([T(1), T(2), T(3), T(4)], 2)
    with pytest.raises(ValueError):
        suc.__setstate__(((T(1), T(2), T(3)), ))


@memory_leak_decorator(collect=True)
def test_successive_failure_setstate4():
    _hf.iterator_setstate_list_fail(
            successive([T(1), T(2), T(3), T(4)], 2))


@memory_leak_decorator(collect=True)
def test_successive_failure_setstate5():
    _hf.iterator_setstate_empty_fail(
            successive([T(1), T(2), T(3), T(4)], 2))


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_successive_pickle1():
    suc = successive([T(1), T(2), T(3), T(4)])
    assert next(suc) == (T(1), T(2))
    x = pickle.dumps(suc)
    assert list(pickle.loads(x)) == [(T(2), T(3)), (T(3), T(4))]


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_successive_pickle2():
    suc = successive([T(1), T(2), T(3), T(4)])
    x = pickle.dumps(suc)
    assert list(pickle.loads(x)) == [(T(1), T(2)), (T(2), T(3)),
                                     (T(3), T(4))]


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
@memory_leak_decorator()
def test_successive_lengthhint1():
    it = successive([0]*6, 4)
    assert operator.length_hint(it) == 3
    next(it)
    assert operator.length_hint(it) == 2
    next(it)
    assert operator.length_hint(it) == 1
    next(it)
    assert operator.length_hint(it) == 0


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
@memory_leak_decorator()
def test_successive_lengthhint2():
    assert operator.length_hint(successive([0]*6, 11)) == 0


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
@memory_leak_decorator(collect=True)
def test_successive_failure_lengthhint1():
    f_it = _hf.FailLengthHint(toT([1, 2, 3]))
    it = successive(f_it)
    with pytest.raises(_hf.FailLengthHint.EXC_TYP) as exc:
        operator.length_hint(it)
    assert _hf.FailLengthHint.EXC_MSG in str(exc)

    with pytest.raises(_hf.FailLengthHint.EXC_TYP) as exc:
        list(it)
    assert _hf.FailLengthHint.EXC_MSG in str(exc)


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
@memory_leak_decorator(collect=True)
def test_successive_failure_lengthhint2():
    # This only checks for overflow if the length_hint is above PY_SSIZE_T_MAX.
    # In theory that would be possible because with times the length would be
    # shorter but "length_hint" throws the exception so we propagate it.
    of_it = _hf.OverflowLengthHint(toT([1, 2, 3]), sys.maxsize + 1)
    it = successive(of_it)
    with pytest.raises(OverflowError):
        operator.length_hint(it)

    with pytest.raises(OverflowError):
        list(it)
