# Licensed under Apache License Version 2.0 - see LICENSE

# Built-ins
from __future__ import absolute_import, division, print_function

# 3rd party
import pytest

# This module
import iteration_utilities

# Test helper
import helper_funcs as _hf
from helper_cls import T
from helper_leak import memory_leak_decorator


minmax = iteration_utilities.minmax


@memory_leak_decorator()
def test_minmax_normal1():
    assert minmax([T(1)]) == (T(1), T(1))


@memory_leak_decorator()
def test_minmax_normal2():
    assert minmax([T(1), T(2)]) == (T(1), T(2))


@memory_leak_decorator()
def test_minmax_normal3():
    assert minmax([T(2), T(1)]) == (T(1), T(2))


@memory_leak_decorator()
def test_minmax_normal4():
    assert minmax([T(1), T(2), T(3)]) == (T(1), T(3))


@memory_leak_decorator()
def test_minmax_normal5():
    assert minmax([T(1), T(3), T(2)]) == (T(1), T(3))


@memory_leak_decorator()
def test_minmax_normal6():
    assert minmax(map(T, range(100))) == (T(0), T(99))


@memory_leak_decorator()
def test_minmax_normal7():
    assert minmax(map(T, range(101))) == (T(0), T(100))


@memory_leak_decorator()
def test_minmax_normal8():
    assert minmax({T(1), T(2), T(-3)}) == (T(-3), T(2))


@memory_leak_decorator()
def test_minmax_normal9():
    assert minmax({T(1): T(0), T(2): T(0), T(3): T(0)}) == (T(1), T(3))


@memory_leak_decorator()
def test_minmax_normal10():
    assert minmax(T(1), T(2), T(3)) == (T(1), T(3))


@memory_leak_decorator()
def test_minmax_normal11():
    assert minmax(T(4), T(3), T(2), T(1)) == (T(1), T(4))


@memory_leak_decorator()
def test_minmax_normal12():
    assert minmax((T(i) for i in [4, 3, 2, 5, 3])) == (T(2), T(5))


@memory_leak_decorator()
def test_minmax_normal13():
    assert minmax((T(i) for i in [4, 3, 2, 5, 3, 3])) == (T(2), T(5))


@memory_leak_decorator()
def test_minmax_normal14():
    assert minmax((T(i) for i in [4, 3, 2, 5, 3]), key=abs) == (T(2), T(5))


@memory_leak_decorator()
def test_minmax_normal15():
    assert minmax((T(i) for i in [4, 3, 2, 5, 3, 3]), key=abs) == (T(2), T(5))


@memory_leak_decorator()
def test_minmax_keyNone1():
    # key=None is identical to no key
    assert minmax([T(1), T(2)], key=None) == (T(1), T(2))


@memory_leak_decorator()
def test_minmax_key1():
    assert minmax(T('a'), T('b'), T('c'),
                  key=lambda x: x.value.upper()) == (T('a'), T('c'))


@memory_leak_decorator()
def test_minmax_key2():
    assert minmax(T((T(1), T(2))), T((T(2), T(3))), T((T(3), T(1))),
                  key=lambda x: x.value[1]) == (T((T(3), T(1))),
                                                T((T(2), T(3))))


@memory_leak_decorator()
def test_minmax_default1():
    assert minmax([], default=T(10)) == (T(10), T(10))


@memory_leak_decorator()
def test_minmax_stability1():
    assert minmax([T((T(1), T(5)))],
                  key=lambda x: x.value[0]) == (T((T(1), T(5))),
                                                T((T(1), T(5))))


@memory_leak_decorator()
def test_minmax_stability2():
    assert minmax(T((T(1), T(5))), T((T(1), T(1))),
                  key=lambda x: x.value[0]) == (T((T(1), T(5))),
                                                T((T(1), T(5))))


@memory_leak_decorator()
def test_minmax_stability3():
    assert minmax(T((T(1), T(5))), T((T(1), T(1))), T((T(1), T(2))),
                  key=lambda x: x.value[0]) == (T((T(1), T(5))),
                                                T((T(1), T(5))))


@memory_leak_decorator()
def test_minmax_stability4():
    assert minmax(T((T(1), T(5))), T((T(1), T(1))), T((T(1), T(2))),
                  T((T(1), T(3))),
                  key=lambda x: x.value[0]) == (T((T(1), T(5))),
                                                T((T(1), T(5))))


@memory_leak_decorator()
def test_minmax_stability5():
    assert minmax(T((T(5), T(5))), T((T(1), T(5))),
                  T((T(1), T(2))), T((T(1), T(3))),
                  key=lambda x: x.value[0]) == (T((T(1), T(5))),
                                                T((T(5), T(5))))


@memory_leak_decorator()
def test_minmax_stability6():
    assert minmax(T((T(5), T(5))), T((T(3), T(5))),
                  T((T(1), T(5))), T((T(1), T(3))),
                  key=lambda x: x.value[0]) == (T((T(1), T(5))),
                                                T((T(5), T(5))))


@memory_leak_decorator()
def test_minmax_stability7():
    assert minmax(T((T(5), T(5))), T((T(3), T(5))),
                  T((T(4), T(5))), T((T(1), T(5))),
                  key=lambda x: x.value[0]) == (T((T(1), T(5))),
                                                T((T(5), T(5))))


@memory_leak_decorator(collect=True)
def test_minmax_failure1():
    # No args
    with pytest.raises(TypeError):
        minmax()


@memory_leak_decorator(collect=True)
def test_minmax_failure2():
    # empty sequence no default
    with pytest.raises(ValueError):
        minmax([])


@memory_leak_decorator(collect=True)
def test_minmax_failure3():
    # invalid kwarg
    with pytest.raises(TypeError):
        minmax(T(1), T(2), invalid_kw='a')


@memory_leak_decorator(collect=True)
def test_minmax_failure4():
    # default with multiple args
    with pytest.raises(TypeError):
        minmax(T(1), T(2), default=T(10))


@memory_leak_decorator(collect=True)
def test_minmax_failure5():
    with pytest.raises(_hf.FailIter.EXC_TYP) as exc:
        minmax(_hf.FailIter())
    assert _hf.FailIter.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_minmax_failure6():
    # func fails on odd numbered arg
    with pytest.raises(TypeError):
        minmax(T(100), T('a'), key=lambda x: x.value + '')


@memory_leak_decorator(collect=True)
def test_minmax_failure7():
    # func fails on even numbered arg
    with pytest.raises(TypeError):
        minmax(T('a'), T(100), key=lambda x: x.value + '')


@memory_leak_decorator(collect=True)
def test_minmax_failure8():
    # unable to compare first and second
    with pytest.raises(TypeError):
        minmax(T(100), T('a'))


@memory_leak_decorator(collect=True)
def test_minmax_failure9():
    # unable to compare third and fourth
    with pytest.raises(TypeError):
        minmax(T(100), T(20), T(100), T('a'))


@memory_leak_decorator(collect=True)
def test_minmax_failure10():
    # unable to compare first and third
    with pytest.raises(TypeError):
        minmax(T(1), T(20), T('a'), T('c'))


@pytest.mark.xfail(iteration_utilities.EQ_PY2, reason='cmp works on Python 2')
@memory_leak_decorator(collect=True)
def test_minmax_failure11():
    # unable to compare second and fourth

    # This is tricky. The elements are explicitly chosen so that
    # 1 compares with 2 without error: 1 current min, 2 current max
    # 3 compares with 4: 3 < 4
    # 3 compares with 1: 1 still current minimum
    # 4 compares not with 2 because the first element is equal and then
    # the comparison with the second element throws and error because
    # str and int are not compareable.
    with pytest.raises(TypeError):
        minmax(T((100, 'a')), T((200, 10)), T((150, 'b')), T((200, 'd')))


@memory_leak_decorator(collect=True)
def test_minmax_failure12():
    # Test that a failing iterator doesn't raise a SystemError
    with pytest.raises(_hf.FailNext.EXC_TYP) as exc:
        minmax(_hf.FailNext())
    assert _hf.FailNext.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_minmax_failure13():
    # Test that a failing iterator doesn't raise a SystemError
    with pytest.raises(_hf.FailNext.EXC_TYP) as exc:
        minmax(_hf.FailNext(offset=1))
    assert _hf.FailNext.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_minmax_failure14():
    # Test a weird class that has lt but no gt method
    class ltbutnogt(object):
        def __init__(self, val):
            self.val = val

        def __lt__(self, other):
            return self.val < other.val

        def __gt__(self, other):
            raise ValueError('no gt!')

    with pytest.raises(ValueError) as exc:
        minmax(ltbutnogt(10), ltbutnogt(5))
    assert 'no gt!' in str(exc)


@memory_leak_decorator(collect=True, offset=1)
def test_minmax_failure15():
    # Changing next method
    with pytest.raises(_hf.CacheNext.EXC_TYP) as exc:
        minmax(_hf.CacheNext(1))
    assert _hf.CacheNext.EXC_MSG in str(exc)
