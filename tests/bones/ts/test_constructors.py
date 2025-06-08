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


from coppertop.pipe import *
from bones.ts.metatypes import BTAtom, BType, BTSeq, BTMap, BTFn, BTStruct, isT
from coppertop.dm.testing import check, equals
from coppertop.dm.utils.testing import assertRaises
from coppertop.dm.core.aggman import collect, joinAll, sortUsing
from coppertop.dm.core.conv import to
from coppertop.dm.core.misc import box

from coppertop.dm.core.types import index, count, offset, num, txt, N, null, T, T1, dstruct, dseq
from coppertop.dm.finance.types import ccy, fx



tFred = BTAtom('fred')
tJoe = BTAtom('joe')
tSally = BTAtom('sally')



def testBTAtom():
    assert repr(tFred) == 'fred'
    assert tFred == BType('fred')
    assert tFred is BType('fred')

    x = 'hello' >> box | tFred
    assert isinstance(x, tFred)
    assert x._v == 'hello'

    i1 = 1 | index
    assert i1._t == index
    c1 = 1 | count
    assert c1._t == count
    o1 = 1 | offset
    assert o1._t == offset
    n1 = 1 | num
    assert n1._t == num


def testBTUnion():
    s = tFred + tJoe

    assert (repr(s) == 'fred+joe') or (repr(s) == 'joe+fred')
    assert tFred in s
    assert tSally not in s
    assert tJoe+tFred == s   # is commutative

    assert isinstance('hello' >> box | tFred, s)


def testBTTuple():
    p1 = tFred*tJoe
    assert repr(p1) == 'fred*joe'
    assert p1 != tJoe*tFred              # the product is not commutative
    assert p1 == tFred*tJoe


def testBTSeq():
    tArr = N ** (num+null)
    repr(tArr) >> check >> equals >> f'N**{num+null}'
    assert isinstance(tArr, BTSeq)


def testBTMap():
    tMap = index ** (num+null)
    repr(tMap) >> check >> equals >> f'index**({num+null})'
    assert isinstance(tMap, BTMap)


def testBTFn():
    fn = (tSally+null) ^ (tFred*tJoe)
    rep = (([tSally, null]
        >> sortUsing >> (lambda x: x.id)
        >> collect >> (lambda x: txt(x))        # OPEN: add unary piping to types so can do x >> txt? is x >> to >> txt a coersion or a conversion?
        | (N**txt)[dseq])
        >> joinAll(_, '+')
    )
    repr(fn) >> check >> equals >> f'{rep} ^ fred*joe'
    assert isinstance(fn, BTFn)


def testStructCreation():
    label = BType('label: atom in mem').setConstructor(dstruct)
    title = label(text='My cool Tufte-compliant scatter graph')
    title._keys() == ['text']


def test_hasT():
    assert isT(T)
    assert isT(T1)

    matrix = BTAtom('matrix2')
    inout = BTAtom('inout')
    out = BTAtom('out')
    assert matrix[inout, T1].hasT

    ccy = BType('ccy')
    fx = BType('fx')
    GBP = BType('GBP: GBP & ccy')
    USD = BType('USD: USD & ccy')
    assert fx[BTStruct(domestic=GBP, foreign=T1)].hasT

    N = BTAtom('N')
    assert (N**T).hasT
    assert ((T*num)^num).hasT
    assert ((num*num)^T).hasT

    assert BTStruct(name=T, age=num).hasT
    assert (T**num).hasT
    assert (num**T).hasT
    assert (num**T).hasT

    with assertRaises(TypeError):
        1 | T


def testNaming():
    tUnusualThing = (num+txt).nameAs('tUnusualThing')
    assert BType('tUnusualThing') == tUnusualThing



def main():
    testBTAtom()
    testBTUnion()
    testBTTuple()
    testBTSeq()
    testBTMap()
    # testBTFn()
    test_hasT()
    testStructCreation()
    testNaming()


if __name__ == '__main__':
    main()
    print('pass')

