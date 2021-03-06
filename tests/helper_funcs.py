# Licensed under Apache License Version 2.0 - see LICENSE

"""
This module contains callable test cases.
"""
# Built-ins
import copy

# 3rd party
import pytest

# This module
import iteration_utilities
from iteration_utilities._compat import filter

# helper
from helper_cls import T


def iterator_copy(thing):
    """Normal copies are not officially supported but ``itertools.tee`` uses
    ``__copy__`` if implemented it is either forbid both or none. Given that
    ``itertools.tee`` is a very useful function ``copy.copy`` is allowed but
    no garantuees are made. This function just makes sure they can be copied
    and the result has at least one item in it (call ``next`` on it)"""
    # Even though normal copies are discouraged they should be possible.
    # Cannot do "list" because it may be infinite :-)
    next(copy.copy(thing))


def iterator_setstate_list_fail(thing):
    with pytest.raises(TypeError) as exc:
        thing.__setstate__([])
    assert 'tuple' in str(exc) and 'list' in str(exc)


def iterator_setstate_empty_fail(thing):
    with pytest.raises(TypeError) as exc:
        thing.__setstate__(())
    assert '0 given' in str(exc)


# Helper classes for certain fail conditions. Bundled here so the tests don't
# need to reimplement them.


def CacheNext(item):
    """Iterator that modifies it "next" method when iterated over."""
    if iteration_utilities.EQ_PY2:
        def subiter():
            def newnext(self):
                raise CacheNext.EXC_TYP(CacheNext.EXC_MSG)
            Iterator.next = newnext
            yield item

        # Need to subclass a C iterator because only the "tp_iternext" slot is
        # cached, the "__next__" method itself always behaves as expected.
        class Iterator(filter):
            pass
    else:
        def subiter():
            def newnext(self):
                raise CacheNext.EXC_TYP(CacheNext.EXC_MSG)
            Iterator.__next__ = newnext
            yield item

        # Need to subclass a C iterator because only the "tp_iternext" slot is
        # cached, the "__next__" method itself always behaves as expected.
        class Iterator(filter):
            pass

    return Iterator(iteration_utilities.return_True, subiter())


CacheNext.EXC_MSG = 'next call failed, because it was modified'
CacheNext.EXC_TYP = ValueError


class FailIter(object):
    """A class that fails when "iter" is called on it.

    This class is currently not interchangable with a real "iter(x)" failure
    because it raises another exception.
    """

    EXC_MSG = 'iter call failed'
    EXC_TYP = ValueError

    def __iter__(self):
        raise self.EXC_TYP(self.EXC_MSG)


class FailNext(object):
    """An iterator that fails when calling "next" on it.

    The parameter "offset" can be used to set the number of times "next" works
    before it raises an exception.
    """

    EXC_MSG = 'next call failed'
    EXC_TYP = ValueError

    def __init__(self, offset=0, repeats=1):
        self.offset = offset
        self.repeats = repeats

    def __iter__(self):
        return self

    def __next__(self):
        if self.offset:
            self.offset -= 1
            return T(1)
        else:
            raise self.EXC_TYP(self.EXC_MSG)

    next = __next__  # python 2.x compatibility


class FailLengthHint(object):
    """Simple iterator that fails when length_hint is called on it."""

    EXC_MSG = "length_hint call failed"
    EXC_TYP = ValueError

    def __init__(self, it):
        self.it = iter(it)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.it)

    next = __next__  # python 2.x compatibility

    def __length_hint__(self):
        raise self.EXC_TYP(self.EXC_MSG)


class OverflowLengthHint(object):
    """Simple iterator that allows to set a length_hint so that one can test
    overflow in PyObject_LengthHint.

    Should be used together with "sys.maxsize" so it works on 32bit and 64bit
    builds.
    """
    def __init__(self, it, length_hint):
        self.it = iter(it)
        self.lh = length_hint

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.it)

    next = __next__  # python 2.x compatibility

    def __length_hint__(self):
        return self.lh


if iteration_utilities.EQ_PY2:
    exec("""
import abc

class FailingIsinstanceClass:
    __metaclass__ = abc.ABCMeta

    EXC_MSG = 'isinstance call failed'
    EXC_TYP = TypeError

    @classmethod
    def __subclasshook__(cls, C):
        raise cls.EXC_TYP(cls.EXC_MSG)
""")
else:
    exec("""
import abc

class FailingIsinstanceClass(metaclass=abc.ABCMeta):

    EXC_MSG = 'isinstance call failed'
    EXC_TYP = TypeError

    @classmethod
    def __subclasshook__(cls, C):
        raise cls.EXC_TYP(cls.EXC_MSG)
""")
