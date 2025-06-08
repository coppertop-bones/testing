# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import sys, traceback

import pytest

from bones import jones
from bones.core.sentinels import Missing
from coppertop.dm.utils.testing import assertRaises
from bones.jones import BTypeError
from bones.ts.type_lang import TypeLangInterpreter
from bones.ts._type_lang.py_type_manager import PyTypeManager
from bones.ts._type_lang.jones_type_manager import JonesTypeManager
from bones.ts.core import TLError, bmtnul, bmtatm, bmtint, bmtuni, bmttup, bmtstr, bmtrec, bmtseq, bmtmap, bmtfnc, bmtsvr


# TODO
#   once all types can be created rework bones.ts.metatypes
#   create the null tuple for functions that take no arguments

# OPEN:
#   - intersections of unions
#   - handle recursion in PP
#   - check every valid arg in constructor can handle recursion (fiddly)
#   - handle tm.minus(t1, tm.intersection(t1, t2)) == tm.intersection(t1, tm.exclusion(t2))? currently consider it
#     hard to reason about so probably not
#   - sizes



def test_atom(TM):
    tli = TypeLangInterpreter(tm := TM())
    t = tm['sally']
    assert t.id == 0
    t = tm.bind('sally', tm.initAtom())

    assert tm['sally'].id == t.id
    assert tm.bmtid(t) == bmtatm
    assert tm.name(t) == 'sally'

    assert t == tli.eval('sally')
    assert t is tm['sally']

    return "test_atom passed"


def test_intersection(TM):
    tli = TypeLangInterpreter(tm := TM())

    mem = tli.eval('mem: atom')
    ccy = tli.eval('ccy: atom')

    t = tli.eval('ccy & (_GBP: atom)')
    assert t == tm.intersection((tm['_GBP'], ccy))

    i1 = tm.intersection((mem, t))
    i2 = tm.intersection((mem, tm['_GBP'], mem, ccy, t))
    assert i1 == i2

    for t in tm.intersectionTl(i1):
        assert t in [ccy, mem, tm['_GBP']]

    # OPEN: test create recursive intersection

    return "test_intersection passed"


def test_union(TM):
    tli = TypeLangInterpreter(tm := TM())

    tli.eval('u32: err: txt: atom')
    u32, err, txt = tm['u32'], tm['err'], tm['txt']

    assert tli.eval('u32 + err') == tli.eval('err + u32'), f"{tli.eval('u32 + err')} != {tli.eval('err + u32')}"
    assert tli.eval('u32 + err + u32') == tli.eval('err + u32 + err')
    assert tli.eval('(u32 + err) + u32') == tli.eval('err + (err + u32)')

    tl = tm.unionTl(tli.eval('(u32 + err) + u32'))
    assert tl == (err, u32), f'{tl} != {(err, u32)}'       # err is created before u32 above

    # with assertRaises(Exception):
    mut = tm.reserve(space=err)
    mut = tm.union((u32, err, txt), btype=mut)

    # fred: tbc
    # fred: f64 + {lhs:fred, rhs:fred}

    return "test_union passed"


def test_tuple(TM):
    tli = TypeLangInterpreter(tm := TM())

    t1 = tli.eval('''
        u32: err: atom
        fred: u32 * err
    ''')
    t1, t2, fred = tm['u32','err', 'fred']

    assert tm.tuple((t1, t2)) == fred
    assert tm.tuple((t2, t1)) != fred

    assert tm.tupleTl(fred) == (t1, t2)

    nullTup = tm.tuple(())
    assert tm.tupleTl(nullTup) == ()

    return "test_tuple passed"


def test_struct(TM):
    tli = TypeLangInterpreter(tm := TM())

    tli.eval('''
        f64: txt: atom
        fred: {val:f64, name:txt}
    ''')
    t1, t2, fred = tm['f64', 'txt', 'fred']

    assert tm.struct(('val', 'name'), (t1, t2)) == fred
    assert tm.struct(('name', 'val'), (t1, t2)) != fred

    assert tm.structNames(fred) == ('val', 'name')
    assert tm.structTl(fred) == (t1, t2)

    return "test_struct passed"


def test_sequence(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('u32: err: atom')

    t1 = tm.union((tm['u32'], tm['err']))
    assert tm.seq(t1) == tm.seq(t1)
    assert tm.seqT(tm.seq(t1)) == t1

    return "test_sequence passed"


def test_map(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('txt: f64: atom')
    txt, f64 = tm['txt', 'f64']

    assert tm.map(txt, f64) == tm.map(txt, f64)
    assert tm.mapTK(tm.map(txt, f64)) == txt
    assert tm.mapTV(tm.map(txt, f64)) == f64

    return "test_map passed"


def test_function(TM):
    tli = TypeLangInterpreter(tm := TM())
    u1 = tli.eval('''
        err: u32: atom
        err + u32
    ''')
    u32 = tm['u32']

    assert tm.fn(tm.tuple((u32, u32)), u1) == tm.fn(tm.tuple((u32, u32)), u1)
    assert tm.tupleTl(tm.fnTArgs(tm.fn(tm.tuple((u32, u32)), u1))) == (u32, u32)
    assert tm.fnTRet(tm.fn(tm.tuple((u32, u32)), u1)) == u1

    return "test_function passed"


def test_schemavar(TM):
    tli = TypeLangInterpreter(tm := TM())

    t = tm.bind('T100', tm.schemavar())
    assert tm['T100'] == t
    assert tm.name(t) == 'T100'

    return "test_schemavar passed"


def test_assign(TM):
    tli = TypeLangInterpreter(tm := TM())
    mem = tli.eval('mem: _GBP: atom')

    tCcy = tm.bind('f8', tm.initAtom(btype=tm.reserve(space=mem)))
    GBP = tm.intersection((tCcy, tm['_GBP']))

    # test nameAs
    assert tm.name(GBP) != 'GBP'
    t = tm.bind('GBP', GBP)
    assert GBP == t
    assert tm.name(GBP) == 'GBP'

    return "test_assign passed"


def test_orthogonal_spaces(TM):
    tli = TypeLangInterpreter(tm := TM())

    ccyfx = tli.eval('ccyfx: atom')

    opts = tm.reserve()
    assert opts is not None

    opts = tm.reserve(space=ccyfx)
    assert tm.space(opts) == ccyfx

    tbc = tm.reserve(space=ccyfx)
    t = tm.initAtom(btype=tbc)
    ccy = tm.bind('ccy', t)
    assert ccy == tm['ccy']

    # let's try to reconstruct ccy however if we decide that ccy2 is ccy then we have the throw away opts as they are
    # preallocated
    opts = tm.reserve(space=ccyfx)
    assert opts != ccy
    with assertRaises(BTypeError):
        ccy2 = tm.bind('ccy', tm.initAtom(btype=opts))

    if tm['fx'].id == 0:
        fx = tm.bind('fx', tm.initAtom(btype=tm.reserve(space=ccyfx)))

    assert tm.space(ccy) == ccyfx
    assert tm.rootSpace(fx) == ccyfx

    with assertRaises(BTypeError):
        t = tm.intersection((ccy, fx))

    tli.eval('lit: sz: null: py: mem: atom')
    mem, py, null, sz, lit = tm['mem', 'py', 'null', 'sz', 'lit']

    m64 = tm.bind('m64', tm.initAtom(btype=tm.reserve(space=sz)))

    f64 = tm.bind('f64', tm.reserve())
    f64 = tm.intersection((f64, m64), btype=f64, space=mem)

    GBP = tm.bind('GBP', tm.reserve())
    GBP = tm.intersection((GBP, f64, ccy), btype=GBP, space=ccy)
    print(tm.rootSpace(GBP))

    USD = tm.bind('USD', tm.reserve())
    USD = tm.intersection((USD, f64, ccy), btype=USD, space=ccy)

    with assertRaises(BTypeError):
        tm.intersection((GBP, USD))


    # OPEN: what are we trying to do here?
    pylist = tm.intersection((tm.bind('pylist', tm.reserve()),), space=py)
    pytup = tm.intersection((tm.bind('pytup', tm.reserve()),), space=py)

    # pyToBones[list] = pylist
    # pyToBones[tuple] = pytup

    littxt = tm.intersection((tm.bind('littxt', tm.reserve()),), space=lit)

    return "test_orthogonal passed"


def test_cStyleConst(TM):
    tli = TypeLangInterpreter(tm := TM())

    # C style const
    # mut: tbc
    # const: atom in const implicitly mut
    # mut: mut & const

    const_ = tm.bind('const_', tm.initAtom())
    mut = tm.reserve()
    const = tm.reserve()
    const = tm.bind('const', tm.initAtom(space=const_, btype=const, implicitly=mut))
    mut = tm.bind('mut', tm.intersection((const, mut), btype=mut))
    tm.intersection((const, mut))

    lit = tli.eval('lit: atom')
    tm.intersection((lit, const))
    tm.intersection((lit, mut))
    tli.eval('lit & mut')    # should be (lit, mut) not (lit, mut, const)


def test_create_various_recursions(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('f64: txt: null: u8: atom')

    u8, null, txt, f64 = tm['u8', 'null', 'txt', 'f64']

    # check each type can be made recursive

    # struct - linked list of u8
    tr1 = tm.reserve()
    tnode1 = tm.struct(('i', 'next'), (u8, tm.union((tr1, null))), btype=tr1)
    assert tr1 == tnode1

    # check we can't use tr1 again
    with assertRaises(BTypeError):
        tm.tuple((u8, tm.union((tr1, null))), btype=tr1)

    # tuple - linked list of u8
    tr2 = tm.reserve()
    tnode2 = tm.tuple((u8, tm.union((tr2, null))), btype=tr2)
    assert tr2 == tnode2

    # seq - linked list of u8
    tr3 = tm.reserve()
    tnode3 = tm.seq(tm.union((u8, tr3, null)), btype=tr3)
    assert tr3 == tnode3

    # map - linked list of u8 - txt {"this", "next"} -> u8 + tr4 + null
    tr4 = tm.reserve()
    tnode4 = tm.map(txt, tm.union((u8, tr4, null)), btype=tr4)
    assert tr4 == tnode4

    # union
    tr5 = tm.reserve()
    tnode5 = tm.union((null, tm.tuple((u8, tr5))), btype=tr5)
    assert tr5 == tnode5

    # intersection
    tr6 = tm.reserve()
    GBP = tm.bind('GBP', tm.intersection((tr6, f64), btype=tr6))

    return "test_create_various_recursions passed"


def test_minus(TM):
    tli = TypeLangInterpreter(tm := TM())

    t3 = tm.atom('GBP')     # deliberately in reverse order
    t2 = tm.atom('ccy')
    t1 = tm.atom('f64')
    t4 = tm.atom('u32')

    # not an intersection or union
    with assertRaises(BTypeError):
        tm.minus(t1, t2)

    # intersections
    assert tm.minus(tm.intersection((t1, t2, t3)), t2) == tm.intersection((t1, t3))
    assert tm.minus(tm.intersection((t1, t2, t3)), tm.intersection((t1, t3))) == t2
    with assertRaises(BTypeError):
        tm.minus(tm.intersection((t1, t2, t3)), t4)
    with assertRaises(BTypeError):
        tm.minus(tm.intersection((t1, t2, t3)), tm.intersection((t1, t3, t4)))
    with assertRaises(BTypeError):
        tm.intersectionTl(tm.minus(tm.intersection((t1, t2, t3)), tm.intersection((t1, t2, t3))))

    # unions
    assert tm.minus(tm.union((t1, t2, t3)), t2) == tm.union((t1, t3))
    assert tm.minus(tm.union((t1, t2, t3)), tm.union((t1, t3))) == t2
    with assertRaises(BTypeError):
        tm.minus(tm.union((t1, t2, t3)), t4)
    with assertRaises(BTypeError):
        tm.minus(tm.union((t1, t2, t3)), tm.union((t1, t3, t4)))
    with assertRaises(BTypeError):
        tm.unionTl(tm.minus(tm.union((t1, t2, t3)), tm.union((t1, t2, t3))))

    return "test_minus passed"


def test_hasT(TM):
    tli = TypeLangInterpreter(tm := TM())

    t1 = tm.atom("u8")
    assert tm.hasT(t1) == False

    T1 = tm.lookup('T1')
    assert tm.hasT(T1) == True

    assert tm.hasT(tm.intersection((t1, T1))) == True
    assert tm.hasT(tm.union((t1, T1))) == True
    assert tm.hasT(tm.tuple((t1, T1))) == True
    assert tm.hasT(tm.seq(T1)) == True
    assert tm.hasT(tm.map(t1, T1)) == True
    assert tm.hasT(tm.fn(tm.tuple((t1, t1)), T1)) == True
    assert tm.hasT(tm.struct(("x",), (T1,))) == True

    return "test_hasT passed"


def test_isRecursive(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('f64: ccy: null: atom')
    f64, ccy, null = tm['f64', 'ccy', 'null']

    GBP = tm.bind('GBP', tm.reserve())
    GBP = tm.intersection((GBP, f64, ccy), btype=GBP, space=ccy)
    assert tm.isRecursive(GBP)

    # recursive types do not need to be named
    f64Tree = tm.reserve()
    tLhs = tm.union((f64Tree, f64, null))
    tRhs = tm.union((f64Tree, f64, null))
    f64Tree = tm.struct(('lhs', 'rhs'), (tLhs, tRhs), btype=f64Tree)

    assert tm.isRecursive(f64Tree) and not tm.isRecursive(tLhs) and not tm.isRecursive(tRhs)


@pytest.mark.skip
def test_offsets(TM):
    tli = TypeLangInterpreter(tm := TM())

    mem = tm.exclusionCat('mem')
    f64 = tm.exclusiveNominal('f64', mem, 8)
    u32 = tm.exclusiveNominal('f64', mem, 4)

    s1 = tm.struct(('t', 'x', 'y'), (u32, f64, f64))
    assert tm.sz(s1) == 24
    assert tm.align(s1) == 8
    assert tm.offsets(s1) == (0, 8, 16)

    s2 = tm.struct(('x', 'y', 't'), (f64, f64, u32))
    assert tm.sz(s2) == 20
    assert tm.align(s2) == 8
    assert tm.offsets(s2) == (0, 8, 16)

    s3 = tm.struct(('x', 'y', 't'), (u32, u32, u32))
    assert tm.sz(s3) == 12
    assert tm.align(s3) == 4
    assert tm.offsets(s3) == (0, 4, 8)

    return "test_offsets passed"


def test_fred(TM):
    tli = TypeLangInterpreter(tm := TM())

    c = tli.eval('''
        a:b:mem: atom
        py: atom in mem
        c: a & py in mem
    ''')

    bc = tli.eval('c & b')

    print(bc)



@pytest.yield_fixture
def TM():
    yield JonesTypeManager
    # yield PyTypeManager



def main():

    fns = [
        test_fred,
        test_atom,
        test_intersection,
        test_union,
        test_tuple,
        test_struct,
        test_sequence,
        test_map,
        test_function,
        test_schemavar,

        test_assign,
        test_orthogonal_spaces,
        test_cStyleConst,
        test_create_various_recursions,

        test_minus,
        test_hasT,
        test_isRecursive,
        # test_offsets,            # needed for memory layout but not for dispatch
    ]

    for fn in fns:
        for TM in (JonesTypeManager, PyTypeManager):
            print(fn(TM))






if __name__ == '__main__':
    main()
    sys._k = None
    print('passed')

