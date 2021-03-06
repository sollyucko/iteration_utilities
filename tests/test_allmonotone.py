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


all_monotone = iteration_utilities.all_monotone


@memory_leak_decorator()
def test_all_monotone_empty1():
    assert all_monotone([])


@memory_leak_decorator()
def test_all_monotone_normal1():
    assert all_monotone([T(1), T(1), T(1)])


@memory_leak_decorator()
def test_all_monotone_normal2():
    assert not all_monotone([T(1), T(1), T(1)], strict=True)


@memory_leak_decorator()
def test_all_monotone_normal3():
    assert all_monotone([T(1), T(2), T(3)])


@memory_leak_decorator()
def test_all_monotone_normal4():
    assert all_monotone([T(1), T(2), T(3)], strict=True)


@memory_leak_decorator()
def test_all_monotone_normal5():
    assert all_monotone([T(1), T(1), T(1)], decreasing=True)


@memory_leak_decorator()
def test_all_monotone_normal6():
    assert not all_monotone([T(1), T(1), T(1)], decreasing=True, strict=True)


@memory_leak_decorator()
def test_all_monotone_normal7():
    assert all_monotone([T(3), T(2), T(1)], decreasing=True)


@memory_leak_decorator()
def test_all_monotone_normal8():
    assert all_monotone([T(3), T(2), T(1)], decreasing=True, strict=True)


@memory_leak_decorator()
def test_all_monotone_normal9():
    # generator
    assert all_monotone(i for i in [T(1), T(1), T(1)])


@memory_leak_decorator(collect=True)
def test_all_monotone_failure1():
    with pytest.raises(_hf.FailIter.EXC_TYP) as exc:
        all_monotone(_hf.FailIter())
    assert _hf.FailIter.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_all_monotone_failure2():
    # comparison fail
    with pytest.raises(TypeError):
        all_monotone([T(1), T('a')])


@memory_leak_decorator(collect=True)
def test_all_monotone_failure3():
    # Test that a failing iterator doesn't raise a SystemError
    with pytest.raises(_hf.FailNext.EXC_TYP) as exc:
        all_monotone(_hf.FailNext())
    assert _hf.FailNext.EXC_MSG in str(exc)


@memory_leak_decorator(collect=True)
def test_all_monotone_failure4():
    # too few arguments
    with pytest.raises(TypeError):
        all_monotone()


@memory_leak_decorator(collect=True, offset=1)
def test_all_monotone_failure5():
    # Changing next method
    with pytest.raises(_hf.CacheNext.EXC_TYP) as exc:
        all_monotone(_hf.CacheNext(1))
    assert _hf.CacheNext.EXC_MSG in str(exc)
