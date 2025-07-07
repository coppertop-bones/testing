# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import time, itertools

from coppertop.pipe import *
from coppertop.dm.core.types import pylist, index
from coppertop.dm.testing import check, equals
from coppertop.dm.core import first, count, drop, collect, prependTo, join, joinAll, take, sum, unpack
from coppertop.dm.pp import PP


@coppertop(style=binary)
def partitions(xs, sizes: pylist) -> pylist:
    sizes >> sum >> check >> equals >> (xs >> count)
    return _partitions(xs, xs >> count, sizes)

def _partitions(xs: pylist, n: index, sizes: pylist):
    if not sizes: return [[]]
    a = map(
        (lambda comb_rest:
            map(
                lambda partitions: [comb_rest[0]] + partitions,
                _partitions(comb_rest[1], n - sizes[0], sizes[1:])
            )
         ),
        _combRest(xs, n, sizes[0])
    )
    return list(itertools.chain(*a))

def _combRest(xs: pylist, n: index, m: index):
    '''answer [m items chosen from n items, the rest]'''
    if m == 0: return [([], xs)]
    if m == n: return [(xs, [])]
    s1, s2 = xs[:1], xs[1:]
    return itertools.chain(
        map(lambda xy: (s1 + xy[0], xy[1]), _combRest(s2, n - 1, m - 1)),
        map(lambda xy: (xy[0], s1 + xy[1]), _combRest(s2, n - 1, m))
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
