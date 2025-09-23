# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import pytest

from coppertop.pipe import *
from coppertop.utils import assertRaises, Missing

xfail = pytest.mark.xfail

from bones.ts.metatypes import BType
from coppertop.dm.testing import check, equals
from coppertop.dm.core.aggman import append, prepend, prependTo, appendTo, join, drop, at, keys, sort, kvs, copy
from coppertop.dm.core.misc import _v, box
from coppertop.dm.core.conv import to
from coppertop.dm.pp import PP
from coppertop.dm.core.structs import _tvtuple, _tvstruct, _tvseq, _tvmap, _tvarray, _tvdate, _tvtime, _tvdatetime

from coppertop.dm.core.types import N, num, index, txt, litint, pydict, pylist, dtup, dstruct, dseq, dmap, darray, \
    dframe, T1, littxt, pyint
# def to(xs:N**T, t:N**(T)) -> N**(T):



def test_tuple():
    # inferred type one level and 1D only
    # dtup() >> typeOf >> check >> equals >> null

    a = dtup(litint*litint*littxt, (1, 2, 'hello'))
    a >> typeOf >> check >> equals >> litint*litint*littxt
    a[0] = 2
    a[0] >> check >> equals >> 2

    fred = dtup(N**(N**index), [[1,2]])

    # test inference of type from construction
    # dtup((1,2,'hello')) >> typeOf >> check >> equals >> litint*litint*littxt

    # with assertRaises(NotYetImplemented):
    #     # inferring type of more than 2d is ambiguous - should a nested list be a subarray or a pylist?
    #     dtup(((1, 2), 'hello'))


def test_struct():
    t2D = BType('{x:num, y:num}')
    t3D = BType('{x:num, y:num, z:num}')

    # fully typed construction
    v2 = _tvstruct(t2D, dict(x=1, y=2))
    assert v2._t == t2D

    # initializing a structure in steps
    tUninitPoint = BType('{x:num+missing, y:num+missing}')
    tmp = _tvstruct(t2D)
    assert tmp._t == tUninitPoint
    assert tmp.x == Missing
    tmp.x = 1.0
    tmp.y = 2.0
    assert tmp._t == tUninitPoint
    v1 = tmp | t2D               # can we ever to inplace coercion in Python?
    assert v1._t == t2D

    # extending a structure (in place)
    v1.z = 3.0
    assert v1._t == t3D

    # creating an empty structure
    tEmpty = BType('{}')
    tmp2 = _tvstruct()
    assert tmp2._t == tEmpty
    tmp2.x = 1.0
    tmp2.y = 2.0
    assert tmp2._t == t2D
    tmp2.z = 3.0
    assert tmp2._t == t3D

    # using dstruct
    tPoint2 = t2D & dstruct
    v3 = tPoint2(dict(x=1,y=2))
    v4 = tPoint2([1,2])
    v3.x, v4.x = 2, 2
    assert v3._v == v4._v

    # check the indexable interface
    assert v3['x'] == 2
    v3['x'], v4['x'] = 1, 1
    assert v3._v == v4._v

    # pvt data
    v3._fred = 1
    assert v3._fred == 1

    assert repr(v3) == f'<{v3._t}>({_ppTvstructKVs(v3._v)})'


def _ppTvstructKVs(s):
    itemStrings = (f"{str(k)}={repr(v)}" for k, v in s._kvs())
    return ", ".join(itemStrings)


def test_seq():
    v1 = _tvseq(N**pyint, [1,2,3])
    tstseq = BType('tstseq: tstseq & py in py')
    with assertRaises(TypeError):
        tstseq([1,2,3])
    tstseq.setConstructor(_tvseq)
    v2 = tstseq([1,2,3])
    with assertRaises(TypeError):
        (N**pyint)([1,2,3])

    v3 = dseq([1,2])
    assert v3 >> typeOf >> dseq

    intseq = dseq & (N ** pyint)
    xs1 = intseq([1,2])

    xs1 >> _v >> check >> equals >> [1, 2]
    xs1 >> check >> typeOf >> intseq
    xs2 = 0 >> prependTo >> xs1
    xs3 = xs2 >> append >> 3
    xs4 = xs3 >> join >> intseq([4, 5])
    xs4 >> _v >> check >> equals >> [0, 1, 2, 3, 4, 5]


@xfail
def test_map():
    DF2 = BType('DF2: DF2 & dmap')

    @coppertop
    def kvs(x: dmap[T1]) -> pylist:
        return list(x.items())

    @coppertop
    def values(x: dmap[T1]) -> pylist:
        return list(x.values())

    @coppertop
    def keys(x: dmap[T1]) -> pylist:
        return list(x.keys())

    DF2()
    # we can either specify a bones type or infer types on construction - need to write an inference function and
    # decide on mapping from python types to bones types, e.g. is a pyint a litint or an index, we can stop at pylist
    # etc so we end up with strongly typed outer with dynamic inner. obviously calling from python to bones is always
    # a full selection

    # + t1&err was meant so could pass any error to + e.g. `txt("nan")&err + 1 -> txt&err` so an intersection with
    # a T can't really be statically inferred?'

    # https://discourse.julialang.org/t/union-types-good-or-bad/46255

    # txt&err < T1 & err  => T1 = txt

    dmap((txt**litint)[dmap], a=1, b=2, c=3) >> drop >> ['a', 'b'] >> to >> pydict >> check >> equals >> dict(c=3)
    [dict(a=1)] >> at >> 0 >> at >> "a" >> check >> equals >> 1
    dict(b=1, a=2) >> keys >> to >> pylist >> sort
    df = DF2(a=1, b=2)
    df >> keys >> check >> equals >> ['a', 'b']
    df >> kvs >> check >> equals >> [('a', 1), ('b', 2)]
    dm = dmap(a=1, b=2)
    dm >> keys >> check >> equals >> ['a', 'b']
    dm >> kvs >> to >> pylist >> check >> equals >> [('a', 1), ('b', 2)]


def test_frame():
    rx = "rx"; oe = "oe"
    bf1 = dframe(date=[1, 2, 3, 1, 2, 3], asset=[rx, rx, rx, oe, oe, oe])
    bf2 = dframe(date=[1, 2, 3, 1, 2, 3], asset=[rx, rx, rx, oe, oe, oe])




import numpy as np


class _nd(np.ndarray):
    def __rrshift__(self, arg):  # so doesn't get in the way of arg >> func
        return NotImplemented

    def __rshift__(self, arg):  # so doesn't get in the way of func >> arg
        return NotImplemented

    def __array_finalize__(self, instance):
        # see - https://numpy.org/doc/stable/user/basics.subclassing.html
        if instance is None: return
        #self._t_ = getattr(instance, '_t_', darray)

    def __new__(cls, *args, **kwargs):
        instance = np.asarray(args[0], **kwargs).view(cls)
        return instance


@coppertop
def T(A:_nd):
    return A.T

@coppertop
def allTrue(A:_nd):
    return bool(A.all())


def test_nd_():
    assert ((_nd([[1, 2], [3, 4]]) >> T >> T) == (_nd([[1, 3], [2, 4]]) >> T >> T >> T)) >> allTrue




def main():
    test_frame()
    test_tuple()
    test_struct()
    test_seq()
    test_map()
    test_nd_()


if __name__ == '__main__':
    main()
    print('pass')




