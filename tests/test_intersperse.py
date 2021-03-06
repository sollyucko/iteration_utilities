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


intersperse = iteration_utilities.intersperse


@memory_leak_decorator()
def test_intersperse_empty1():
    assert list(intersperse([], T(0))) == []


@memory_leak_decorator()
def test_intersperse_empty2():
    assert list(intersperse([T(1)], T(0))) == [T(1)]


@memory_leak_decorator()
def test_intersperse_normal1():
    assert list(intersperse([T(1), T(2)], T(0))) == toT([1, 0, 2])


@memory_leak_decorator()
def test_intersperse_attributes1():
    it = intersperse([T(1), T(2)], T(0))
    assert it.fillvalue == T(0)


@memory_leak_decorator(collect=True)
def test_intersperse_failure1():
    with pytest.raises(_hf.FailIter.EXC_TYP) as exc:
        intersperse(_hf.FailIter(), T(0))
    assert _hf.FailIter.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_intersperse_failure2():
    # Test that a failing iterator doesn't raise a SystemError
    with pytest.raises(_hf.FailNext.EXC_TYP) as exc:
        next(intersperse(_hf.FailNext(), T(0)))
    assert _hf.FailNext.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_intersperse_failure3():
    # Too few arguments
    with pytest.raises(TypeError):
        intersperse()


@memory_leak_decorator(collect=True)
def test_intersperse_copy1():
    _hf.iterator_copy(intersperse(toT([1, 2, 3]), T(0)))


@memory_leak_decorator(collect=True)
def test_intersperse_failure_setstate1():
    # When start==0 then no second item should be given to setstate
    its = intersperse(toT([1, 1]), None)
    with pytest.raises(ValueError):
        its.__setstate__((0, T(1)))


@memory_leak_decorator(collect=True)
def test_intersperse_failure_setstate2():
    _hf.iterator_setstate_list_fail(intersperse(toT([1, 1]), None))


@memory_leak_decorator(collect=True)
def test_intersperse_failure_setstate3():
    _hf.iterator_setstate_empty_fail(intersperse(toT([1, 1]), None))


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_intersperse_pickle1():
    its = intersperse(toT([1, 2, 3]), T(0))
    x = pickle.dumps(its)
    assert list(pickle.loads(x)) == toT([1, 0, 2, 0, 3])


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_intersperse_pickle2():
    its = intersperse(toT([1, 2, 3]), T(0))
    assert next(its) == T(1)
    x = pickle.dumps(its)
    assert list(pickle.loads(x)) == toT([0, 2, 0, 3])


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_intersperse_pickle3():
    its = intersperse([T(1), T(2), T(3)], T(0))
    assert next(its) == T(1)
    assert next(its) == T(0)
    x = pickle.dumps(its)
    assert list(pickle.loads(x)) == toT([2, 0, 3])


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_intersperse_pickle4():
    its = intersperse([T(1), T(2), T(3)], T(0))
    assert next(its) == T(1)
    assert next(its) == T(0)
    assert next(its) == T(2)
    x = pickle.dumps(its)
    assert list(pickle.loads(x)) == toT([0, 3])


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
@memory_leak_decorator()
def test_intersperse_lengthhint1():
    it = intersperse([1, 2, 3], 2)
    assert operator.length_hint(it) == 5
    next(it)
    assert operator.length_hint(it) == 4
    next(it)
    assert operator.length_hint(it) == 3
    next(it)
    assert operator.length_hint(it) == 2
    next(it)
    assert operator.length_hint(it) == 1
    next(it)
    assert operator.length_hint(it) == 0


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
@memory_leak_decorator(collect=True)
def test_intersperse_lengthhint_failure1():
    f_it = _hf.FailLengthHint(toT([1, 2, 3]))
    it = intersperse(f_it, 2)
    with pytest.raises(_hf.FailLengthHint.EXC_TYP) as exc:
        operator.length_hint(it)
    assert _hf.FailLengthHint.EXC_MSG in str(exc)

    with pytest.raises(_hf.FailLengthHint.EXC_TYP) as exc:
        list(it)
    assert _hf.FailLengthHint.EXC_MSG in str(exc)


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
@memory_leak_decorator(collect=True)
def test_intersperse_lengthhint_failure2():
    # This is the easy way to overflow the length_hint: If the iterable itself
    # has a length_hint > sys.maxsize
    of_it = _hf.OverflowLengthHint(toT([1, 2, 3]), sys.maxsize + 1)
    it = intersperse(of_it, 2)
    with pytest.raises(OverflowError):
        operator.length_hint(it)

    with pytest.raises(OverflowError):
        list(it)


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
@memory_leak_decorator(collect=True)
def test_intersperse_lengthhint_failure3():
    # The length_hint method multiplies the length_hint of the iterable with
    # 2 (and adds/subtracts 1) so it's actually possible to have overflow even
    # if the length of the iterable doesn't trigger the overflow!
    of_it = _hf.OverflowLengthHint(toT([1, 2, 3]), sys.maxsize)
    it = intersperse(of_it, 2)
    with pytest.raises(OverflowError):
        operator.length_hint(it)

    with pytest.raises(OverflowError):
        list(it)
