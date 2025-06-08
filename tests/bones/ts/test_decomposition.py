# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import random, pytest
xfail = pytest.mark.xfail
type_system = pytest.mark.type_system

from coppertop.pipe import *
from bones.ts.metatypes import BTAtom, BTStruct, _partitionIntersectionTLs, weaken, BTypeError, BTReserved, BType
import bones.ts.metatypes
from coppertop.dm._core.structs import tv
from coppertop.dm.utils.testing import assertRaises
from coppertop.dm.testing import check, equals, fitsWithin, doesNotFitWithin
from coppertop.dm.core.misc import _v
from coppertop.dm.core.conv import to
from coppertop.dm.core.aggman import drop
from coppertop.dm.core.types import txt, N, T, T1, T2, T3, num, pylist, dtup, dseq
from coppertop.dm.finance.types import ccy, fx
from coppertop.dm.linalg.types import square, right

oldWeakenings = bones.ts.metatypes._weakenings

mem = BType('mem')
tFred = BTAtom('fred')
tJoe = BTAtom('joe')
tSally = BTAtom('sally')
pystr2 = BTAtom('pystr2')
weaken(txt, (pystr2,))

aliased = BTReserved()
_aliased = BTAtom('_aliased', implicitly=aliased)
aliased = BTAtom('aliased', btype=aliased, space=_aliased)
anon = BTAtom('anon', space=_aliased)
named = BTAtom('named', space=_aliased)
weaken(anon, aliased)
weaken(named, aliased)


# we have these metatypes - nominal, union, intersection, product (tuples and structs), exponential (arrays, maps
# and functions) & distinguished.
#
#
# when we do X <: Y we partition the two sets into three parts
#
# X intersect Y' - stuff in X but not in Y - anything here then it's not a fit
# X intersect Y - common stuff, if we only have common stuff then it's an exact fit
# X' intersect Y - X' & Y - stuff not in X but in Y - we term this the residual


# A & B <: A
# {}, A & B, A - A&B  (A & B')

# A <: A & B


# f64 <: f64 & cm
#
# QR(f64 & numpy)
# QR(f64 & lol)
#
# txt & isin
#
# concat(txt & isin, txt & isin)
# concat(txt, txt)
# concat(txt & T, txt & T)
#
#
# txt & isin <: txt?
# {}, txt & isin, {}



# when types are in the residual set we allow them to behave in exlusively one of the following ways:
#
# generic - the default of all types, e.g. matrix (i.e. N**N**num), matrix&left, right, upper, lower, orthogonal,
#     identity, diagonal, tridiagonal, banddiagonal, positivedefinite, positivesemidefinite etc
#     all matrix operations are available and some are optimisable. e.g. cov = AT @ A can return identity for the
#     orthogonal case
#     i.e. generics do not prevent matching, thus effectively are discarded from the matching decision
#
#
# IMPLICIT TYPES
# implicit - e.g. anon, named, aliased with aliased as the implicit default, defaults do not prevent matching, and
#     non-defaults can be explicity weakened to the default to provide the right behaviour
#
# e.g if the residual contains an implicit type we can safely ignore it and no distance is added
#
#
# EXPLICIT TYPES
# e,g, ccy, fx, anything explicit in a residual results in no match, e.g.
# - f64 <: f64 & inches has inches in the residual
# - f64 & inches <: f64 has inches & (f64 & inches)'
#
#
# familial - e.g. ISIN, CUSIP, inches, cm, all instances in the signature must have the same residual, i.e. like a T1,
#     thus add(num, num) called with (cm, inches) will not match as cm and inches are both familial, and (cm, num) will
#     not match as cm is familial to all other types
#
#
# orthogonal - e.g. listOfLists, dtup, ascii, txt (typically classes / structs / values / etc) only one orthogonal type
#     may exist in the residual and common. Currently classes are the only orthogonal type I can think of - maybe null set,
#     void, missing, are too. But what about void&num?


# generic / vanilla / tags / occasional / unremarkable / exceptional / partial / minor /


tmatrix = BTAtom('tmatrix')
tdd = BTAtom('tdd')

# implicit / contextual
red = BTAtom('red')
yellow = BTAtom('yellow')
blue = BTAtom('blue')
# mouseButton = BTSet([red, yellow, blue], default=blue)


_ISINy = BTAtom('_ISINy')
ISIN = BType('ISIN: atom explicit in _ISINy')
CUSIP = BType('CUSIP: atom explicit in _ISINy')
inches = BTAtom('inches', space=_ISINy)
cm = BTAtom('cm', space=_ISINy)


# explicit
col = BTAtom('col', explicit=True)
row = BTAtom('row', explicit=True)

GBP = BType('GBP2: GBP2 & ccy').setCoercer(tv)
USD = BType('USD2: USD2 & ccy').setCoercer(tv)


# orthogonal
# anything including a python class, e.g. tmatrix&darray
lol = BTAtom('lol', space=mem)         # the type for a list of lists (regular?), e.g. tmatrix[lol]

# (txt).setConstructor(tv)
(ISIN & txt)
(CUSIP & txt)


join_psps = '_join(a:txt, b:txt)'
@coppertop(style=binary)
def _join(a:txt, b:txt) -> txt:
    return join_psps

# is it possible to handle this one automatically (by detecting the familial type)?
# is it desirable from a clarity perspective?
join_pstpst = '_join(a:txt & T1, b:txt & T1)'
@coppertop(style=binary)
def _join(a:txt & T1, b:txt & T1) -> txt:
    return join_pstpst

join_ipsips = '_join(a:ISIN & txt, b:ISIN & txt)'
@coppertop(style=binary)
def _join(a:ISIN & txt, b:ISIN & txt) -> txt:
    return join_ipsips

add_mm = 'add(a:tmatrix, b:tmatrix)'
@coppertop(style=binary)
def add(a:tmatrix, b:tmatrix) -> txt:
    return add_mm

add_msms = 'add(a:tmatrix&square, b:tmatrix&square)'
@coppertop(style=binary)
def add(a:tmatrix&square, b:tmatrix&square) -> txt:
    return add_msms


@coppertop(style=binary)
def mul(a:tmatrix & lol, b:tmatrix & lol) -> txt:
    return 'a:tmatrix & lol, b:tmatrix & lol'


@coppertop
def cov(a:tmatrix&tdd) -> txt:
    # n rows of m variables
    # return a >> T >> mul >> a
    return 'a:tmatrix'


@coppertop
def opA(A:tmatrix&aliased[T1], tByT) -> tmatrix&anon[T1]:
    return A | (tmatrix & anon & tByT[T1])

@coppertop
def opB(A:tmatrix&aliased[T1], tByT) -> tmatrix&anon[T1]:
    return A | (tmatrix & anon & tByT[T1])

@coppertop
def opB(A:tmatrix&anon) -> tmatrix&anon:
    return A


@type_system
def testPartition():
    _partitionIntersectionTLs((tmatrix & square).types, (tmatrix, )) >> check >> equals >> ((square,), (tmatrix,), (), {})
    _partitionIntersectionTLs((tmatrix & square).types, (ISIN, CUSIP)) >> check >> equals >> ((square, tmatrix,), (), (ISIN, CUSIP), {})
    _partitionIntersectionTLs((txt & square).types, (pystr2, )) >> check >> equals >> ((square,), (txt,), (), {txt:pystr2})
    _partitionIntersectionTLs((pystr2 & square).types, (txt, )) >> check >> equals >> ((square, pystr2), (), (txt,), {})


@type_system
def testExclusive():
    with assertRaises(BTypeError) as ex:
        lol & pylist
    (txt & square) >> check >> fitsWithin >> txt
    tv(tmatrix & tdd, [[]]) >> cov >> check >> equals >> 'a:tmatrix'
    tv(tmatrix & lol & tdd, [[]]) >> cov >> check >> equals >> 'a:tmatrix'
    tv(tmatrix & dtup & tdd, [[]]) >> cov >> check >> equals >> 'a:tmatrix'


@type_system
def testGeneric():
    (tmatrix & square) >> check >> fitsWithin >> tmatrix
    tmatrix >> check >> doesNotFitWithin >> (tmatrix & square)
    tv(tmatrix, [[]] ) >> add >> tv(tmatrix, [[]] ) >> check >> equals >> add_mm
    tv(tmatrix & right, [[]] ) >> add >> tv(tmatrix & right, [[]] ) >> check >> equals >> add_mm
    tv(tmatrix & square, [[]] ) >> add >> tv(tmatrix & square, [[]] ) >> check >> equals >> add_msms


@xfail
@type_system
def testImplicit():
    tmatrix >> check >> fitsWithin >> (tmatrix & aliased)
    (tmatrix & aliased) >> check >> fitsWithin >> tmatrix
    (tmatrix & anon) >> check >> fitsWithin >> tmatrix      # although we might weaken anon to aliased
    (tmatrix & cm) >> check >> doesNotFitWithin >> tmatrix
    tmatrix >> check >> doesNotFitWithin >> (tmatrix & anon)

    (tmatrix & named) >> check >> fitsWithin >> tmatrix

    # show here that named, anon and aliased work as a set i.e.
    lmatrix = (tmatrix & pylist).setConstructor(tv)
    A = lmatrix([[1, 2], [3, 4]]) | +named
    A2 = A >> opA
    A3 = A2 >> opB      # dispatches to opB(A:tmatrix&aliased) but is subset of anon
    A4 = (A3 | -anon) >> opB
    A4 >> _v >> check >> equals >> A._v

    A = lmatrix([[1, 2], [3, 4]]) | +named
    A._t >> check >> fitsWithin >> (lmatrix[T1])
    # A._t >> PP >> check >> fitsWithin >> (lmatrix[T1] >> PP) >> PP


@type_system
def testOrthogonal():
    (txt & ISIN) >> check >> doesNotFitWithin >> str  # because ISIN is left in the residual
    (str & ISIN) >> check >> doesNotFitWithin >> (str & CUSIP)  # conflict between ISIN and CUSIP
    (str & ISIN) >> check >> fitsWithin >> (str & ISIN)
    (str & ISIN & square) >> check >> fitsWithin >> (str & ISIN)
    (str & ISIN) >> check >> fitsWithin >> (str & T1)
    (str & ISIN) >> check >> doesNotFitWithin >> (str & ISIN & T)

    (str)('DE') >> _join >> (str)('0008402215') >> check >> equals >> join_psps
    (CUSIP & txt)('DE') >> _join >> (CUSIP & txt)('0008402215') >> check >> equals >> join_pstpst
    (ISIN & txt)('DE') >> _join >> (ISIN & txt)('0008402215') >> check >> equals >> join_ipsips
    with assertRaises(BTypeError) as ex:
        (ISIN & txt)('DE') >> _join >> ('0008402215')


@type_system
def testExplicit():
    GBP >> check >> fitsWithin >> GBP
    GBP >> check >> fitsWithin >> ccy
    ccy >> check >> fitsWithin >> ccy
    ccy >> check >> doesNotFitWithin >> T                           # ccy is explicit
    ccy >> check >> doesNotFitWithin >> ccy[T]                      # T has nothing
    GBP >> check >> fitsWithin >> ccy[T]                            # T will equal the _GBP part
    (GBP & square) >> check >> fitsWithin >> GBP                    # square is in residual
    (GBP & square) >> check >> fitsWithin >> ccy[T]                 # square is in residual
    (N ** ccy) >> check >> doesNotFitWithin >> (N ** T)
    (N ** GBP) >> check >> fitsWithin >> (N ** ccy[T])


@coppertop(style=binary)
def mul(c:ccy[T1], f:fx[BTStruct(d=ccy[T1], f=ccy[T2])], tByT) -> ccy[T2]:
    return tv(ccy[tByT[T2]], c._v * f._v)

@coppertop(style=binary)
def mul(c:ccy[T1], f:fx[BTStruct(d=ccy[T2], f=ccy[T1])], tByT) -> ccy[T2]:
    return tv(ccy[tByT[T2]], c._v / f._v)


@type_system
def testMisc():
    (txt & square) >> check >> fitsWithin >> pystr2
    (pystr2 & square) >> check >> doesNotFitWithin >> txt
    tmatrix[square,right] >> check >> fitsWithin >> (tmatrix & right & square)


@type_system
def testAddAndSubtract():
    BType('tmatrix & pylist in mem').setConstructor(tv)
    A = tmatrix[pylist]([[1,2],[3,4]])
    (A | +square) >> check >> typeOf >> (tmatrix[pylist] & square)
    (A | +square | -tmatrix[pylist]) >> check >> typeOf >> square

    mutable = BTAtom('mutable')
    maddResult = BTAtom('maddResult')
    rowmajor = BTAtom('rowmajor')
    matrix = BType('matrix')
    dseq = BType('dseq')
    Matrix = BType('Matrix: matrix & rowmajor & dseq in mem')
    x = tv(Matrix, 0) | +(mutable & maddResult)
    actual = x | -(mutable & maddResult)
    actual >> check >> typeOf >> Matrix


@xfail
@type_system
def testDrop():
    card = BType('card: card & txt')
    cards = (N ** card)[dseq].setPP('deck').setConstructor(dseq)
    Gr = 'Green'
    Mu = 'Mustard'
    Or = 'Orchid'
    Pe = 'Peacock'
    Pl = 'Plum'
    Sc = 'Scarlet'
    people = [Gr, Mu, Or, Pe, Pl, Sc] >> to >> cards
    people >> drop >> [0, 5] >> _v >> check >> equals >> [Mu, Or, Pe, Pl]


@xfail
@type_system
def testExplicitStructs():
    # GBPUSD = fx[BTStruct(d=GBP, f=USD).setExplicit].setCoercer(tv)
    GBPUSD = fx[BTStruct(d=GBP, f=USD)].setCoercer(tv)
    GBPUSD >> check >> doesNotFitWithin >> fx
    GBPUSD >> check >> doesNotFitWithin >> fx[BTStruct(d=T1, f=T2)]        # ccy is not explicit in the rhs
    GBPUSD >> check >> fitsWithin >> fx[BTStruct(d=ccy[T1], f=ccy[T2])]
    (100 | GBP) >> mul >> (1.30 | GBPUSD) >> check >> equals >> (130 | USD)
    (130 | USD) >> mul >> (1.30 | GBPUSD) >> check >> equals >> (100 | GBP)



@type_system
def testTypes():
    (num & anon & col & num) >> check >> fitsWithin >> (col & anon & num)


@type_system
def testFitsWithin():
    # (num & col & anon) >> check >> fitsWithin >> num
    (num & col & anon) >> check >> fitsWithin >> (col & anon)

    num >> check >> doesNotFitWithin >> (num & col & anon)
    (num & col & anon) >> check >> doesNotFitWithin >> (num & col & tdd)
    (num & col & anon) >> check >> doesNotFitWithin >> (num & col & anon & tdd)



def main():
    testTypes()
    testFitsWithin()
    testPartition()
    testExclusive()
    testGeneric()
    testOrthogonal()
    testMisc()
    testExplicit()
    # testAddAndSubtract()
    # testDrop()
    # testExplicitStructs()
    # testImplicit()
    print(f'{__file__} has failing tests')

if __name__ == '__main__':
    t = fx[BTStruct(d=ccy[T1], f=ccy[T2])]
    main()
    print('pass')

bones.ts.metatypes._weakenings = oldWeakenings
