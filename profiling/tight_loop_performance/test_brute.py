# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import itertools, time, pytest

def partitions(cards, handSizes):
    slices = []
    s1 = 0
    for handSize in handSizes:
        s2 = s1 + handSize
        slices.append((s1, s2))
        s1 = s2
    perms = filter(
        lambda perm: groupsInOrder(perm, slices),
        itertools.permutations(cards, len(cards))
    )
    return tuple(perms)

def groupsInOrder(xs, slices):
    for s1, s2 in slices:
        if not isAsc(xs[s1:s2]): return False
    return True

def isAsc(xs):
    p = xs[0]
    for n in xs[1:]:
        if n <= p: return False
        p = n
    return True

@pytest.mark.skip
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
