# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import time, itertools, builtins

from coppertop.pipe import *
from coppertop.dm.core.types import pylist, index
from coppertop.dm.testing import check, equals
from coppertop.dm.pp import PP

from coppertop import pipe

pipe.FN_ONLY_NAMES = [
    'sum', 'first', 'count', 'drop', 'take', 'prependTo', 'takeDrop', 'takeDrop_', 'ucollect', 'ucollect_', 'join', 'join_',
    'unpackArgsInto', 'joinAll', 'joinAll_', 'toList',
    'partitions', '_partitions', '_combRest'
]


@coppertop
def sum(x):
    return builtins.sum(x)

@coppertop
def first(xs):
    return xs[0]

@coppertop
def count(xs):
    return len(xs)

@coppertop(style=binary)
def drop(xs, n):
    if n >= 0:
        return xs[n:]
    else:
        1/0

@coppertop(style=binary)
def take(xs, c):
    if c >= 0:
        return xs[0:c]
    else:
        return xs[c:]

@coppertop(style=binary)
def prependTo(x, xs):
    return itertools.chain(x, xs)

@coppertop(style=binary)
def takeDrop(xs, s):
    return xs[:s], xs[s:]

@coppertop(style=binary)
def takeDrop_(xs, n):
    if isinstance(xs, itertools.chain):
        xs = list(xs)
    return xs[:n], xs[n:]

@coppertop(style=binary)
def ucollect(xs, f):
    return [f(x) for x in xs]

@coppertop(style=unary)
def ucollect_(xs, f):
    return map(f, xs)

@coppertop(style=binary)
def join(xs, ys):
    return xs + ys

@coppertop(style=binary)
def join_(xs, ys):
    return itertools.chain(xs, ys)

@coppertop(style=binary)
def unpackArgsInto(args, f):
    return f(*args)

@coppertop
def joinAll(lol):
    return itertools.chain(*lol)

@coppertop
def joinAll_(lol):
    return itertools.chain(*lol)

@coppertop
def toList(i):
    return list(i)

@coppertop(style=binary)
def partitions(xs, sizes):
    n = xs >> count
    sizes >> sum >> check >> equals >> n
    return list(_partitions(xs, n, sizes))

@coppertop
def _partitions(xs, n, sizes):
    if sizes:
        return (
            _combRest(xs, n, sizes[0]) >> ucollect_(_, lambda comb_rest:
                _partitions(comb_rest[1], n - sizes[0], sizes[1:]) >> ucollect_(_, lambda partitions:
                    [comb_rest[0]] >> join >> partitions
                )
            )
            >> joinAll_
            >> toList
        )
    else:
        return [[]]

@coppertop
def _combRest(xs, n, m):
    '''answer [m items chosen from n items, the rest]'''
    if m == 0:
        return [([], xs)]
    if m == n:
        return [(xs, [])]
    s1, s2 = xs >> takeDrop_ >> 1
    return (
        _combRest(s2, n - 1, m - 1) >> ucollect_(_, lambda xy: (s1 >> join_ >>  xy[0], xy[1]))
        >> join_ >>
        _combRest(s2, n - 1, m) >> ucollect_(_, lambda xy: (xy[0], s1 >> join_ >> xy[1]))
    )



pipe.FN_ONLY_NAMES = []


def test():
    t1 = time.perf_counter_ns()
    for i in range(1):
        x = partitions(range(13), [5, 4, 4])
        assert len(x) == 90090
    t2 = time.perf_counter_ns()
    print(x[0])
    print(f'{__file__} took {(t2 - t1) / 1_000_000} ms')


if __name__ == '__main__':
    test()
    print('passed')
