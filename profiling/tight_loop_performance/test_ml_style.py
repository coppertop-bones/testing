# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import time


def partitions(xs, sizes):
    n = sum(sizes)

    def go(xs, n, sizes):
        return [
            [l] + r
            for (l, rest) in choose(xs)(n)(sizes[0])
            for r in go(rest, n - sizes[0], sizes[1:])
        ] if sizes else [[]]

    return go(xs, n, sizes)


# choose :: [Int] -> Int -> Int -> [([Int], [Int])]
def choose(xs):
    '''(m items chosen from n items, the rest)'''

    def go(xs, n, m):
        f = cons(xs[0])
        choice = choose(xs[1:])(n - 1)
        return [([], xs)] if 0 == m else (
            [(xs, [])] if n == m else (
                    [first(f)(xy) for xy in choice(m - 1)] +
                    [second(f)(xy) for xy in choice(m)]
            )
        )

    return lambda n: lambda m: go(xs, n, m)


# cons :: a -> [a] -> [a]
def cons(x):
    '''Construction of a list from x as head, and xs as tail.'''
    return lambda xs: [x] + xs


# first :: (a -> b) -> ((a, c) -> (b, c))
def first(f):
    '''A simple function lifted to a function over a tuple, with f applied only the first of two values.'''
    return lambda xy: (f(xy[0]), xy[1])


# second :: (a -> b) -> ((c, a) -> (c, b))
def second(f):
    '''A simple function lifted to a function over a tuple, with f applied only the second of two values.'''
    return lambda xy: (xy[0], f(xy[1]))



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
