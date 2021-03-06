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


accumulate = iteration_utilities.accumulate


@memory_leak_decorator()
def test_accumulate_empty1():
    assert list(accumulate([])) == []


@memory_leak_decorator()
def test_accumulate_normal1():
    assert list(accumulate([T(1), T(2), T(3)])) == [T(1), T(3), T(6)]


@memory_leak_decorator()
def test_accumulate_normal2():
    # binop=None is identical to no binop
    assert list(accumulate([], None)) == []


@memory_leak_decorator()
def test_accumulate_normal3():
    # binop=None is identical to no binop
    assert list(accumulate([T(1), T(2), T(3)], None)) == [T(1), T(3), T(6)]


@memory_leak_decorator()
def test_accumulate_binop1():
    assert list(accumulate([T(1), T(2), T(3), T(4)],
                           operator.add)) == [T(1), T(3), T(6), T(10)]


@memory_leak_decorator()
def test_accumulate_binop2():
    assert list(accumulate([T(1), T(2), T(3), T(4)],
                           operator.mul)) == [T(1), T(2), T(6), T(24)]


@memory_leak_decorator()
def test_accumulate_initial1():
    assert list(accumulate([T(1), T(2), T(3)],
                           None, T(10))) == [T(11), T(13), T(16)]


@memory_leak_decorator(collect=True)
def test_accumulate_failure1():
    with pytest.raises(TypeError):
        list(accumulate([T(1), T(2), T(3)], None, T('a')))


@memory_leak_decorator(collect=True)
def test_accumulate_failure2():
    with pytest.raises(TypeError):
        list(accumulate([T(1), T(2), T(3)], operator.add, T('a')))


@memory_leak_decorator(collect=True)
def test_accumulate_failure3():
    with pytest.raises(TypeError):
        list(accumulate([T('a'), T(2), T(3)]))


@memory_leak_decorator(collect=True)
def test_accumulate_failure4():
    # Test that a failing iterator doesn't raise a SystemError
    with pytest.raises(_hf.FailNext.EXC_TYP) as exc:
        next(accumulate(_hf.FailNext()))
    assert _hf.FailNext.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_accumulate_failure5():
    with pytest.raises(_hf.FailIter.EXC_TYP) as exc:
        accumulate(_hf.FailIter())
    assert _hf.FailIter.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_accumulate_failure6():
    # Too few arguments
    with pytest.raises(TypeError):
        accumulate()


@memory_leak_decorator(collect=True)
def test_accumulate_copy1():
    _hf.iterator_copy(accumulate(toT([1, 2, 3])))


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_accumulate_pickle1():
    acc = accumulate([T(1), T(2), T(3), T(4)])
    assert next(acc) == T(1)
    x = pickle.dumps(acc)
    assert list(pickle.loads(x)) == [T(3), T(6), T(10)]


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_accumulate_pickle2():
    acc = accumulate([T(1), T(2), T(3), T(4)])
    x = pickle.dumps(acc)
    assert list(pickle.loads(x)) == [T(1), T(3), T(6), T(10)]


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_accumulate_pickle3():
    acc = accumulate([T(1), T(2), T(3), T(4)], operator.mul)
    assert next(acc) == T(1)
    x = pickle.dumps(acc)
    assert list(pickle.loads(x)) == [T(2), T(6), T(24)]


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_accumulate_pickle4():
    acc = accumulate([T(1), T(2), T(3), T(4)], None, T(4))
    x = pickle.dumps(acc)
    assert list(pickle.loads(x)) == [T(5), T(7), T(10), T(14)]


@memory_leak_decorator()
def test_accumulate_attributes1():
    it = accumulate(toT([1, 2, 3]))
    assert it.func is None
    with pytest.raises(AttributeError):
        it.current

    for item in it:
        assert item == it.current
        assert it.func is None


@memory_leak_decorator()
def test_accumulate_attributes2():
    it = accumulate(toT([1, 2, 3]), operator.add)
    for item in it:
        assert item == it.current
        assert it.func is operator.add


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
@memory_leak_decorator()
def test_accumulate_lengthhint1():
    it = accumulate([1, 2, 3, 4])
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
def test_accumulate_lengthhint_failure1():
    f_it = _hf.FailLengthHint(toT([1, 2, 3]))
    acc = accumulate(f_it)
    with pytest.raises(_hf.FailLengthHint.EXC_TYP) as exc:
        operator.length_hint(acc)
    assert _hf.FailLengthHint.EXC_MSG in str(exc)

    with pytest.raises(_hf.FailLengthHint.EXC_TYP) as exc:
        list(acc)
    assert _hf.FailLengthHint.EXC_MSG in str(exc)


@pytest.mark.xfail(not iteration_utilities.GE_PY34,
                   reason='length does not work before Python 3.4')
@memory_leak_decorator(collect=True)
def test_accumulate_lengthhint_failure2():
    of_it = _hf.OverflowLengthHint(toT([1, 2, 3]), sys.maxsize + 1)
    acc = accumulate(of_it)
    with pytest.raises(OverflowError):
        operator.length_hint(acc)

    with pytest.raises(OverflowError):
        list(acc)
