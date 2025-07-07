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



from bones.ts import select
select.DISABLE_RETURN_CHECK = True
select.DISABLE_ARG_CHECK_FOR_SOLE_FN = True


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
        return xs[n:]

@coppertop(style=binary)
def take(xs, c):
    if c >= 0:
        return xs[0:c]
    else:
        return xs[c:]

@coppertop(style=binary)
def prependTo(x, xs):
    return [x] + xs

@coppertop(style=binary)
def takeDrop(xs, s):
    return xs[:s], xs[s:]

@coppertop(style=binary)
def collect(xs, f):
    return [f(x) for x in xs]

@coppertop(style=binary)
def join(xs, ys):
    return xs + ys

@coppertop
def unpack(f):
    return lambda args: f(*args)

@coppertop
def joinAll(lol):
    return itertools.chain(*lol)
    answer = []
    for e in xs:
        answer += e
    return answer

@coppertop
def toList(i):
    return list(i)

# list(itertools.chain(*lol))


@coppertop(style=binary)
def partitions(xs, sizes: pylist) -> pylist:
    sizes >> sum >> check >> equals >> (xs >> count)
    return _partitionsCptFaster(list(xs), xs >> count, sizes)

@coppertop
def _partitionsCptFaster(xs: pylist, n: index, sizes: pylist) -> pylist:
    if not sizes: return [[]]
    return  toList(joinAll(collect(
        _combRestCptFaster(xs, n, sizes[0]),
        unpack(lambda comb, rest: collect(
            _partitionsCptFaster(rest, n - sizes[0], sizes[1:]),
            (lambda partitions:[comb] + partitions)
        ))
    )))

@coppertop
def _combRestCptFaster(xs: pylist, n: index, m: index) -> pylist:
    '''answer [m items chosen from n items, the rest]'''
    if m == 0: return [([], xs)]
    if m == n: return [(xs, [])]
    s1, s2 = xs[:1], xs[1:]
    return (
        collect(_combRestCptFaster(s2, n - 1, m - 1), (lambda xy: (s1 + xy[0], xy[1]))) +
        collect(_combRestCptFaster(s2, n - 1, m), (lambda xy: (xy[0], s1 + xy[1])))
    )

def test():
    t1 = time.perf_counter_ns()
    for i in range(1):
        x = partitions(list(range(13)), [5, 4, 4])
        assert len(x) == 90090
    t2 = time.perf_counter_ns()
    print(f'{__file__} took {(t2 - t1) / 1_000_000} ms')


if __name__ == '__main__':
    test()
    print('passed')
