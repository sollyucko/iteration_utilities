# Licensed under Apache License Version 2.0 - see LICENSE

# Built-ins
from __future__ import absolute_import, division, print_function
import operator
import pickle

# 3rd party
import pytest

# This module
import iteration_utilities

# Test helper
import helper_funcs as _hf
from helper_cls import T, toT
from helper_leak import memory_leak_decorator


unique_everseen = iteration_utilities.unique_everseen
Seen = iteration_utilities.Seen


@memory_leak_decorator()
def test_uniqueeverseen_empty1():
    assert list(unique_everseen([])) == []


@memory_leak_decorator()
def test_uniqueeverseen_normal1():
    assert list(unique_everseen([T(1), T(2), T(1)])) == [T(1), T(2)]


@memory_leak_decorator()
def test_uniqueeverseen_normal2():
    # key=None is identical to no key
    assert list(unique_everseen([T(1), T(2), T(1)], None)) == [T(1), T(2)]


@memory_leak_decorator()
def test_uniqueeverseen_key1():
    assert list(unique_everseen([T(1), T(2), T(1)], abs)) == [T(1), T(2)]


@memory_leak_decorator()
def test_uniqueeverseen_key2():
    assert list(unique_everseen([T(1), T(1), T(-1)], abs)) == [T(1)]


@memory_leak_decorator()
def test_uniqueeverseen_unhashable1():
    assert list(unique_everseen([{T(1): T(1)}, {T(2): T(2)},
                                 {T(1): T(1)}])) == [{T(1): T(1)},
                                                     {T(2): T(2)}]


@memory_leak_decorator()
def test_uniqueeverseen_unhashable2():
    assert list(unique_everseen([[T(1)], [T(2)], [T(1)]])) == [[T(1)], [T(2)]]


@memory_leak_decorator()
def test_uniqueeverseen_unhashable3():
    assert list(unique_everseen([[T(1), T(1)], [T(1), T(2)], [T(1), T(3)]],
                                operator.itemgetter(0))) == [[T(1), T(1)]]


@memory_leak_decorator()
def test_uniqueeverseen_getter1():
    t = unique_everseen([T(1), T([0, 0]), T(3)])
    assert not t.seen
    assert t.key is None
    assert next(t) == T(1)
    assert t.seen == Seen({T(1)})
    assert t.key is None
    assert next(t) == T([0, 0])
    assert T(1) in t.seen
    assert T([0, 0]) in t.seen
    assert t.key is None
    assert next(t) == T(3)
    assert t.seen == Seen({T(1), T(3)}, [T([0, 0])])
    assert t.key is None


@memory_leak_decorator()
def test_uniqueeverseen_getter2():
    t = unique_everseen([T(1), T([0, 0]), T(3)],
                        iteration_utilities.return_identity)
    assert not t.seen
    assert t.key is iteration_utilities.return_identity
    assert next(t) == T(1)
    assert t.seen == Seen({T(1)})
    assert t.key is iteration_utilities.return_identity
    assert next(t) == T([0, 0])
    assert T(1) in t.seen
    assert T([0, 0]) in t.seen
    assert t.key is iteration_utilities.return_identity
    assert next(t) == T(3)
    assert t.seen == Seen({T(1), T(3)}, [T([0, 0])])
    assert t.key is iteration_utilities.return_identity


@memory_leak_decorator(collect=True)
def test_uniqueeverseen_failure1():
    with pytest.raises(_hf.FailIter.EXC_TYP) as exc:
        unique_everseen(_hf.FailIter())
    assert _hf.FailIter.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_uniqueeverseen_failure2():
    with pytest.raises(TypeError):
        list(unique_everseen([T(1), T(2), T(3), T('a')], abs))


@memory_leak_decorator(collect=True)
def test_uniqueeverseen_failure3():
    # Test that a failing iterator doesn't raise a SystemError
    with pytest.raises(_hf.FailNext.EXC_TYP) as exc:
        next(unique_everseen(_hf.FailNext()))
    assert _hf.FailNext.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_uniqueeverseen_failure4():
    # Too few arguments
    with pytest.raises(TypeError):
        unique_everseen()


@memory_leak_decorator(collect=True)
def test_uniqueeverseen_failure5():
    # Failure when comparing the object to the objects in the list
    class NoHashNoEq():
        def __hash__(self):
            raise TypeError('cannot be hashed')

        def __eq__(self, other):
            raise ValueError('bad class')

    with pytest.raises(ValueError) as exc:
        list(unique_everseen([[T(1)], NoHashNoEq()]))
    assert 'bad class' in str(exc)


@memory_leak_decorator(collect=True)
def test_uniqueeverseen_failure6():
    # Failure (no TypeError) when trying to hash the value
    class NoHash():
        def __hash__(self):
            raise ValueError('bad class')

    with pytest.raises(ValueError) as exc:
        list(unique_everseen([T(1), NoHash()]))
    assert 'bad class' in str(exc)


@memory_leak_decorator(collect=True)
def test_uniqueeverseen_copy1():
    _hf.iterator_copy(unique_everseen(toT([1, 2, 1, 2])))


@memory_leak_decorator(collect=True)
def test_uniqueeverseen_failure_setstate1():
    # __setstate__ only accepts Seen instances
    dp = unique_everseen(toT([1, 1]))
    with pytest.raises(TypeError):
        dp.__setstate__((set(toT(range(1, 3))),))


@memory_leak_decorator(collect=True)
def test_uniqueeverseen_failure_setstate2():
    _hf.iterator_setstate_list_fail(unique_everseen(toT([1, 1])))


@memory_leak_decorator(collect=True)
def test_uniqueeverseen_failure_setstate3():
    _hf.iterator_setstate_empty_fail(unique_everseen(toT([1, 1])))


@pytest.mark.xfail(iteration_utilities.EQ_PY2,
                   reason='pickle does not work on Python 2')
@memory_leak_decorator(offset=1)
def test_uniqueeverseen_pickle1():
    uqe = unique_everseen([T(1), T(2), T(1), T(2)])
    assert next(uqe) == T(1)
    x = pickle.dumps(uqe)
    assert list(pickle.loads(x)) == [T(2)]
