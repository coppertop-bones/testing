# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import sys
# sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

import enum, pytest

from coppertop.pipe import *
from coppertop.dm.testing import check
from coppertop.dm.core import sequence, collect, inject
from coppertop.dm.core.comparisons import equals
from coppertop.dm.core.types import dstruct
from coppertop.dm.pmf import uniform, rvAdd, mix, toXsPs, PMF, pmfMul, normalise, L, formatPmf, CMF, quantile
from _ import SS, PP, at, atSlot, atSlotPut, to, closeTo


class E(enum.IntEnum):
    A = enum.auto()
    B = enum.auto()
    C = enum.auto()
    V = enum.auto()
    J1 = enum.auto()
    J2 = enum.auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

A = E.A
B = E.B
C = E.C
V = E.V
J1 = E.J1
J2 = E.J2


def test_pmf():
    d4 = sequence(1, 4) >> uniform
    d6 = sequence(1, 6) >> uniform
    rv = d4 >> rvAdd >> d4

    rv >> at >> 2 >> check >> equals >> 1/16

    d4d6 = [d4, d6] >> mix
    result = d4d6 >> at >> 1
    expected = (1/4 + 1/6) / (4 * (1/4 + 1/6) + 2 * 1/6)
    assert closeTo(result, expected, 0.00001), '%s != %s' % (result, expected)

    (d4 >> toXsPs)[0] >> check >> equals >> (1.0, 2.0, 3.0, 4.0)

    PMF({A:30, B:10}) >> at >> A >> check >> closeTo >> 0.75

def test_cmf():
    d6 = uniform(sequence(1, 6))
    cmf = d6 >> to >> CMF
    cmf >> quantile(_, 0.5) >> check >> equals >> 3

def test_MM():
    bag1994 = dstruct(Brown=30, Yellow=20, Red=20, Green=10, Orange=10, Tan=10)
    bag1996 = dstruct(Brown=13, Yellow=14, Red=13, Green=20, Orange=16, Blue=24)
    prior = PMF({A:0.5, B:0.5})
    likelihood = L({
        A: bag1994.Yellow * bag1996.Green,
        B: bag1994.Green * bag1996.Yellow
    })
    post = prior >> pmfMul >> likelihood >> normalise
    post >> at >> A >> check >> closeTo >> 20/27

def test_monty():
    prior = PMF({A:1, B:1, C:1})
    likelihood = L({  # i.e. likelihood of monty opening B given that the car is behind each, i.e. p(data|hyp)
        A:0.5,  # prob of opening B if behind A - he can choose at random so 50:50
        B:0,  # prob of opening B if behind B - Monty can't open B else he'd reveal the car, so cannot open B => 0%
        C:1,  # prob of opening B if behind C - Monty can't open C else he'd reveal the car, so must open B => 100%
    })
    posterior = prior >> pmfMul >> likelihood >> normalise
    posterior >> at >> C >> check >> closeTo(_,_,0.001) >> 0.667

@pytest.mark.skip
def test_PP():
    PMF({A: 0.5, B: 0.5}) >> SS >> check >> equals >> 'PMF(A: 0.500, B: 0.500)'

def test_jar():
    @coppertop
    def jarLikelihood(jarsStates, flavour) -> L:
        return jarsStates >> collect >> (lambda j: (j.tag, j >> atSlot >> flavour)) >> to >> L

    @coppertop
    def updateJarModel(jarsStateAndPrior, flavour):
        jarsState, prior = jarsStateAndPrior
        posterior = prior >> pmfMul >> jarLikelihood(jarsState, flavour) >> normalise
        jarsState = jarsState >> collect >> (lambda s: s >> atSlotPut >> flavour >> max(((s >> atSlot >> flavour) - 1, 0)))
        f'Took: {flavour},  posterior: {posterior >> formatPmf},  newState: {jarsState}'
        return (jarsState, posterior)

    modelState = [dstruct(V=30, C=10, tag=J1), dstruct(V=20, C=20, tag=J2)]

    ['C', 'V'] >> inject(_, (modelState, PMF({J1:0.5, J2:0.5})), _) >> updateJarModel;

def main():
    test_MM()
    test_monty()
    test_pmf()
    test_cmf()
    test_jar()



if __name__ == '__main__':
    main()
    print('pass')

