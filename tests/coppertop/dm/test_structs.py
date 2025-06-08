# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *
from bones.ts.metatypes import BType
from coppertop.dm.testing import check, equals
from coppertop.dm.core.aggman import append, prepend, prependTo, appendTo, join, drop, at, keys, sort, kvs
from coppertop.dm.core.misc import _v, box
from coppertop.dm.core.conv import to
from coppertop.dm.pp import PP

from coppertop.dm.core.types import N, num, index, txt, litint, pydict, pylist, dtup, dstruct, dseq, dmap, dframe, T1, littxt
# def to(xs:N**T, t:N**(T)) -> N**(T):



def test_dtup():
    # inferred type one level and 1D only
    # dtup() >> typeOf >> check >> equals >> null

    a = dtup(litint*litint*littxt, (1, 2, 'hello'))
    a >> typeOf >> check >> equals >> litint*litint*littxt
    a[0] = 2
    a[0] >> check >> equals >> 2

    fred = dtup(N**(N**index), [[1,2]])

    # test inference of type from construction
    # dtup((1,2,"hello")) >> typeOf >> check >> equals >> litint*litint*littxt

    # with assertRaises(NotYetImplemented):
    #     # inferring type of more than 2d is ambiguous - should a nested list be a subarray or a pylist?
    #     dtup(((1, 2), "hello"))




def test_dstruct():
    fred = dstruct(N**(N**index), [[1,2]])
    fred.a = 1
    fred.b = 2
    fred['a'] >> PP
    fred['a'] = 5
    fred._fred = 1
    fred = fred | N**(N**index)
    fred._fred >> PP
    repr(fred) >> PP
    str(fred) >> PP
    for k, v in fred._kvs():
        f'{(k, v)}' >> PP


def test_dseq():
    fred = dseq((N**litint)[dseq], [1, 2])
    fred >> _v >> check >> equals >> [1, 2]
    fred >> check >> typeOf >> (N**litint)[dseq]
    fred = fred >> append >> 3
    fred = 0 >> prependTo >> fred
    fred = fred >> join >> dseq((N**litint)[dseq], [4, 5])
    fred >> _v >> check >> equals >> [0, 1, 2, 3, 4, 5]


def test_dmap():
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


def test_me():
    rx = "rx"; oe = "oe"
    bf1 = dframe(date=[1, 2, 3, 1, 2, 3], asset=[rx, rx, rx, oe, oe, oe])
    bf2 = dframe(date=[1, 2, 3, 1, 2, 3], asset=[rx, rx, rx, oe, oe, oe])




import numpy as np


class nd_(np.ndarray):
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
def T(A:nd_):
    return A.T

@coppertop
def allTrue(A:nd_):
    return bool(A.all())


def test_nd_():
    assert ((nd_([[1, 2], [3, 4]]) >> T >> T) == (nd_([[1, 3], [2, 4]]) >> T >> T >> T)) >> allTrue




def main():
    test_dtup()
    test_dstruct()
    test_dseq()
    test_dmap()
    test_me()
    test_nd_()


if __name__ == '__main__':
    main()
    print('pass')




