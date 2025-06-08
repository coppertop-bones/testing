# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import antlr4, traceback, os

from bones.jones import BTypeError
from coppertop.dm.utils.testing import assertRaises
from bones.core.context import context              # needed for conditional break points whilst debugging

from bones.ts.core import TLError, bmtatm
from bones.ts.type_lang import TypeLangInterpreter
from bones.ts._type_lang.py_type_manager import PyTypeManager
from bones.ts._type_lang.jones_type_manager import JonesTypeManager


import pytest
type_lang = pytest.mark.type_lang
pytestmark = pytest.mark.parametrize("TM", [PyTypeManager, JonesTypeManager])
xfail = pytest.mark.xfail


@type_lang
def test_atom1(TM):
    tli = TypeLangInterpreter(tm := TM())

    assert tm['sally'].id == 0

    t = tli.eval('sally: atom')
    assert tm.bmtid(t) == bmtatm

    assert tm['sally'] == t
    assert tm.name(t) == 'sally'

    assert t == tli.eval('sally')
    assert t == tm['sally']

    return "test_atom passed"


@type_lang
def test_atom2(TM):
    tli = TypeLangInterpreter(tm := TM())
    t1 = tli.eval('''
        txt: atom
        txt
    ''')
    t2 = tm['txt']
    assert tm.bmtid(t1) == bmtatm, f'{t1} is not an Atom'
    assert t1 == t2 , f'{t1} != {t2}'


@xfail
@type_lang
def test_atom_redefine(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        txt: atom
        txt: atom
    ''')

    tli.eval('''
        isin: atom in txt
        isin: atom in txt
    ''')

    # should we allow this module to redefine the atom but keep the old one?
    # on the one hand it makes sense, but on the other it may cause confusion as cusip will
    # behave like it is "in txt" but it looks locally like it is not "in txt"
    # on balance I think we should prevent permissive redefinitions, but allow permissive lookups
    with assertRaises(TLError) as ex:
        tli.eval('''
            cusip: atom in txt
            cusip: atom
        ''')

    with assertRaises(TLError) as ex:
        tli.eval('''
            bbgcode: atom
            bbgcode: atom in txt
        ''')


@type_lang
def test_intersection(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        txt: isin: atom
        t1: isin & txt & isin
    ''')
    t1 = tm['t1']
    t2 = tli.eval('txt & isin & txt')
    assert t1 == t2, f'{t1} != {t2}'


@xfail
@type_lang
def test_intersection_redefine(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        txt: financial: atom
    ''')

    tli.eval('''
        isin: isin & txt in financial
        isin: isin & txt in financial
        bbgcode: bbgcode & txt in financial
        bbgcodeOrIsin: bbgcode & txt + isin & txt  // okay if not assigning
    ''')

    with assertRaises(Exception):
        tli.eval('''
            isin: isin & txt in financial
            isin: isin & txt
        ''')

    with assertRaises(Exception):
        tli.eval('''
            cusip: cusip & txt
            cusip: cusip & txt in financial
        ''')


@type_lang
def test_complicated_spaces(TM):
    tli = TypeLangInterpreter(tm := TM())

    tli.eval('''
        S1: S2: S3: a: b: c: d: f: atom
        ab: a & b in S1
        cd: c & d in S1

        e: atom in S1
        ef: e & f in S1
        aef: a & ef in S1
        ac: a & c in S2

        g: atom in S1

        ag: a & g in S2
        acef: aef & ac in S3
    ''')

    with assertRaises((BTypeError, TLError)):
        tli.eval('ab & cd')  # ab and cd are both in S1

    with context(stop=False):
        with assertRaises((BTypeError, TLError)):
            tli.eval('acef & ab')  # e and ab are in S1

    with assertRaises((BTypeError, TLError)):
        tli.eval('acef & ag')  # e and g are in S1


@type_lang
def test_union(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        txt: null: atom
        t1: txt + null + null
    ''')
    t1 = tm['t1']
    t2 = tli.eval('null + txt + txt')
    assert t1 == t2, f'{t1} != {t2}'

    tli.eval('''
        node: tbc
        holder: txt * node
        node: holder + null
    ''')


@type_lang
def test_intersection_union_precedence(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        txt: isin: err: atom
        t1: txt & isin + err
    ''')
    t1 = tm['t1']
    t2 = tli.eval('err + isin & txt')
    assert t1 == t2, f'{t1} != {t2}'


@type_lang
def test_tuple(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        txt: isin: err: f64: atom
        t1: f64 * txt & isin + err
        t2: f64 * txt & isin + err * f64
    ''')
    f64 = tm['f64']
    t1, t2, t3 = tm['t1'], tm['t2'], tli.eval('f64 * txt & isin + err * f64')
    u1 = tli.eval('err + isin & txt')
    assert tm.tupleTl(t1) == (f64, u1), f'{tm.tupleTl(t1)} != {(f64, u1)}'
    assert tm.tupleTl(t2) == (f64, u1, f64), f'{tm.tupleTl(t2)} != {(f64, u1, f64)}'
    assert t2 is t3, f'{t2} != {t3}'


@type_lang
def test_paren(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        txt: isin: err: f64: atom
        t1: f64 * txt & isin + err * f64 * txt & isin + err 
        t2: (f64 * txt & isin + err) * (f64 * txt & isin + err) 
        t3: f64 * txt & isin + err
    ''')
    t1, t2, t4 = tm['t1'], tm['t2'], tli.eval('t3 * t3')
    assert t1 is not t2, f'{t1} == {t2}'
    assert t2 is t4, f'{t2} == {t4}'


@type_lang
def test_doc2_othogonal_spaces(TM):
    tli = TypeLangInterpreter(tm := TM())

    src = '''
        index: txt: mem: atom
        pydict: pylist: atom in mem
    '''
    tli.eval(src)

    with assertRaises(TLError) as ex:
        tli.eval('pydict & pylist')

    with assertRaises(TLError) as ex:
        tli.eval('''
            (index ** txt) & pydict & 
            (index ** txt) & pylist
        ''')

    with assertRaises(Exception) as ex:
        # this is a bit more complex since we haven't thought through intersections of maps and seq only fns
        # e.g. (a ** b & mem) & (c ** d & mem)
        # e.g. (N ** b & mem) & (N ** d & mem)
        # in functions the return type is a union of all the return types
        tli.eval('(index ** txt & pydict) & (index ** txt & pylist)')
        raise Exception()

        # a function overload requires a langauge mechanism to select the actual function being used ideally statically
        # and dynamically if necessary. It is hard to imagine a memory backed data arrow serving the same role.
        # Therefore we will disallow more than one arrow per intersection. Structs and tuples can be converted in an
        # isomorphic manner so we probably don't need to be able to intersect them.from

        # what about fx?

        # GBPUSD: domfor & f64
        # GBPUSD: domfor & (f64 * ccy * ccy)

        # here the struct domfor is only a label, e.g.

        # (N ** txt & isin) & (index ** txt) & pylist   - a pylist of isin that is serializable
        # (N1 ** N2 ** f64) & (index ** f64) & array    - a serializable matrix

        # given that an overload is special is it really a intersection type?

        # i32 ^ txt
        # i32 ** txt
        # N ** txt

        # from the memory manager's perspective memory an object has extant and pointers (pointer location could be
        # data dependent which is more complex)


@xfail
@type_lang
def test_namespaces(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        txt: isin: atom
        mod1.t1: isin & txt & isin
        mod2.t2: isin & txt & isin
    ''')
    t1 = tm['mod1.t1']
    t2 = tm['mod2.t2']
    assert t1 is t2, f'{t1} != {t2}'


@type_lang
def test_arrow_intersections(TM):
    tli = TypeLangInterpreter(tm := TM())

    src = '''
        f64: txt: mem: index: atom
        peopleframe: (N ** {name:txt, age:f64}) & {name:N**txt, age:N**f64}
    '''
    tli.eval(src)

    src = '''
        listOfTxt: (N ** txt) & (index ** txt)
    '''
    tli.eval(src)


@type_lang
def test_runtime_ccy(TM):
    tli = TypeLangInterpreter(tm := TM())
    src = '''
        ccysym: atom
        GBP_: GBP_ & ccysym
        USD_: USD_ & ccysym
        GBP: GBP & ccysym in ccysym
        USD: USD & ccysym in ccysym
    '''
    tli.eval(src)
    # the following shows that "intersection" is not enough but "intersection in" is required
    tli.eval('GBP_ & USD_')
    with assertRaises(TLError):
        tli.eval('GBP & USD')
    assert tm.fitsWithin(tm['GBP'], tm['ccysym'])
    assert not tm.fitsWithin(tm['GBP'], tm['USD'])


@type_lang
def test_runtime_fx(TM):
    tli = TypeLangInterpreter(tm := TM())
    src = '''
        ccyfx: ccysym: f64: atom
        ccy: ccy && {v:f64, ccy:ccysym} in ccyfx
        fx: fx && {v:f64, dom:ccysym, for:ccysym} in ccyfx
        convert_ccy_fn: ccy * fx ^ ccy
        GBP: GBP & ccysym in ccysym
        USD: USD & ccysym in ccysym
    '''
    tli.eval(src)


@type_lang
def test_runtime_fx_err(TM):
    # ccy is correctly to be an implicit recursive type but is not used immediately in the assignment
    tli = TypeLangInterpreter(tm := TM())
    src = '''
        ccyfx: ccysym: f64: atom
        fred: ccy && {v:f64, ccy:ccysym} in ccyfx
    '''
    with assertRaises(TLError):
        tli.eval(src)


@type_lang
def test_static_fx1(TM):
    tli = TypeLangInterpreter(tm := TM())

    # NOTES:
    # - each ccy, GBP, JPY, etc is an intersection of ccy and orthognal to ccy
    # - each fx, GBPUSD, etc is an intersection of fx and domfor and orthognal to fx
    # - domfor types are not orthognal relying on the fx set to provide that
    # - parentheses are necessary around anonymous domfor creation to match with the predeclared ones
    # - fx and ccy are explicitly matched

    src = '''
        ccyfx: atom
        ccy: atom explicit in ccyfx
        GBP: GBP & ccy in ccy
        USD: USD & ccy in ccy
        JPY: JPY & ccy in ccy

        domfor: {dom: ccy & T1, for: ccy & T2}

        fx: atom explicit in ccyfx

        GBPUSD: fx & GBPUSD & {dom:GBP, for:USD} in fx
        USDJPY: fx & USDJPY & {dom:USD, for:JPY} in fx
    '''

    tli.eval(src)

    # NOTES:
    # - since domfor is not orthognal, domfor(GBP, USD) & domfor(USD, JPY) is valid
    src = '''
        # ccyfx: atom
        # ccy: atom explicit in ccyfx
        # GBP: GBP & ccy in ccy
        # USD: USD & ccy in ccy
        # JPY: JPY & ccy in ccy
        # 
        # domfor(T1, T2): {dom: ccy & T1, for: ccy & T2}
        # 
        # fx: atom explicit in ccyfx
        GBPUSD: fx & GBPUSD & domfor(GBP, USD) in fx
        USDJPY: fx & USDJPY & domfor(USD, JPY) in fx
        
        
        *: (ccy & T1) * (fx & {dom: ccy & T1, for: ccy & T2}) ^ (ccy & T2)
    '''


@xfail
@type_lang
def test_static_fx2(TM):
    tli = TypeLangInterpreter(tm := TM())

    # NOTES:
    # - each ccy, GBP, JPY, etc is an intersection of ccy and orthognal to ccy
    # - each fx, GBPUSD, etc is an intersection of fx and domfor and orthognal to fx
    # - each domfor, GBP2USD, etc is an intersection of domfor and orthognal to domfor
    # - parentheses are necessary around anonymous domfor creation to match with the predeclared ones
    # - fx and ccy are explicitly matched

    src = '''
        ccyfx: atom
        ccy: atom explicit in ccyfx
        GBP: GBP & ccy in ccy
        USD: USD & ccy in ccy
        JPY: JPY & ccy in ccy
        
        domfor: {dom: ccy & T1, for: ccy & T2} & domfor in domfor
        GBP2USD: {dom:GBP, for:USD} & domfor in domfor
        USD2JPY: {dom:USD, for:JPY} & domfor in domfor
        
        fx: fx & domfor in ccyfx
        GBPUSD: fx & GBPUSD & ({dom:GBP, for:USD} & domfor) in fx
        USDJPY: fx & USDJPY & ({dom:USD, for:T1} & domfor) in fx
    '''

    tli.eval(src)

    src = '''
        ccyfx: atom
        ccy: ccy & T1 in ccyfx
        ccy(T1): ccy & T1 in ccy            // a type macro
        GBP: ccy(GBP)
        USD: ccy(USD)
        JPY: ccy(JPY)

        domforspc: atom
        domfor: {dom: ccy & T1, for: ccy & T2} & domfor in domforspc
        domfor(T1, T2): {dom: ccy & T1, for: ccy & T2} & domfor(T1,T2) in domforspc

        fx: fx & domfor in ccyfx
        fx(T1, T2): fx & {dom: ccy & T1, for: ccy & T2} & domfor in ccyfx
        
        GBPUSD: fx & GBPUSD & f(GBP, USD) in fx
        USDJPY: fx & USDJPY & domfor(USD, JPY) in fx
        
        
        *: (ccy & T1) * (fx(T1, T2)) ^ (ccy & T2)
        
        
        problem is we have {dom: ccy & T1, for: ccy & T2} & {dom: ccy & GBP, for: ccy & USD} in GBPUSD
    '''

    # NOTES:
    # three orthogonal spaces: ccy, fx, domfor
    # use && for intersections "in"
    # do not need type macros, but they would be useful for readability

    src = '''
        ccyfx: atom
        ccy: atom explicit in ccyfx             // disallow GBP & USD => GBP && ccy & USD && ccy
        fx: atom explicit in ccyfx              // disallow ccy & fx
        domfor: atom explicit in domfor         // allow fx & domfor
        
        ccy(T1): ccy(T1) && ccy in ccy          // a type macro
        GBP: ccy(GBP)
        GBP: GBP && ccy in ccy                  // where ccy(T1) is "GBP" and T1 is "GBP"
        USD: ccy(USD)
        USD: USD && ccy in ccy
        JPY: ccy(JPY)
        JPY: JPY && ccy in ccy

        domfor(T1, T2): domfor && {dom: ccy && T1, for: ccy && T2} in domfor
        GBP2USD: domfor(GBP, USD)
        GBP2USD: domfor && {dom:GBP, for:USD} in domfor      // where domfor(T1, T2) is "GBP2USD" and T1 is "GBP" and T2 is "USD"
        USD2JPY: domfor(USD, JPY)
        USD2JPY: domfor && {dom:USD, for:JPY} in domfor


        GBPUSD: fx & domfor(GBP, USD) in fx
        GBPUSD: fx & domfor && {dom:GBP, for:USD} in fx
        GBPUSD: fx & (domfor && {dom:GBP, for:USD} in domfor) in fx
        
        USDJPY: fx & domfor(USD, JPY) in fx
        USDJPY: fx & domfor && {dom:USD, for:JPY} in fx

        *: (ccy && T1) * (fx & domfor(T1, T2)) ^ (ccy && T2)
        *: (ccy && T1) * (fx & domfor && {dom: ccy && T1, for: ccy && T2})) ^ (ccy && T2)

    '''


@type_lang
def test_fitsWithin(TM):
    tli = TypeLangInterpreter(tm := TM())
    
    src = '''
        isin: err: mem: ccyfx: atom
        f64: txt: pylist: pydict: atom in mem
        ccy: fx: atom in ccyfx
    '''
    tli.eval(src)

    with assertRaises(TLError):
        tli.eval('f64 & txt')

    assert not tm.fitsWithin(tli.eval('isin'), tli.eval('txt'))

    assert tm.fitsWithin(tli.eval('isin & txt'), tli.eval('txt'))
    assert tm.fitsWithin(tli.eval('isin & txt'), tli.eval('isin'))
    assert tm.fitsWithin(tli.eval('isin & txt'), tli.eval('isin & txt'))

    assert tm.fitsWithin(tli.eval('isin'), tli.eval('isin + txt'))
    assert tm.fitsWithin(tli.eval('txt'), tli.eval('isin + txt'))
    assert tm.fitsWithin(tli.eval('isin + txt'), tli.eval('isin + txt'))

    assert tm.fitsWithin(tm['f64'], tm['T1'])


@type_lang
def test_recursive_space(TM):
    tli = TypeLangInterpreter(tm := TM())
    t = tli.eval('ccyfx: atom')
    assert t == tm['ccyfx']

    tli.eval('domfor: atom explicit in ccyfx')

    tli.eval('''
        GBP: tbc
        ccy: atom in ccyfx implicitly GBP
        GBP: GBP & ccy
    ''')

    tli.eval('''
        mut: tbc
        consty: atom implicitly mut
        const: atom in consty
        mut: mut & const
    ''')

    # OPEN: handle this
    # tli.eval('''
    #     GBP: tbc
    #     ccy: atom explicit in ccy implicitly GBP
    #     GBP: GBP & ccy
    # ''')


@type_lang
def test_pyAndPylistEtc(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        mem: atom
        py: atom in mem
        txt: txt & py in mem
        pylist: pylist & py in mem
        pydict: pydict & py in mem
    ''')
    pylist = tm['pylist']
    txts = tli.eval('N**txt')
    t = tm.intersection((txts, pylist))
    
    tli.eval('(N**txt) & pylist')

    with assertRaises((BTypeError, TLError)):
        tli.eval('pylist & py')

    with assertRaises((BTypeError, TLError)):
        tli.eval('pylist & pydict')


@type_lang
def test_cStyleConst(TM):
    tli = TypeLangInterpreter(tm := TM())

    tli.eval('''
        fred: joe: sally: consty: atom
        mut: tbc
        const: atom in consty implicitly mut
        mut: mut & const in consty
    ''')

    tli.eval('fred & const')
    tli.eval('fred & const & joe')
    tli.eval('fred & mut')
    tli.eval('fred & mut & joe')

    with assertRaises((BTypeError, TLError)):
        tli.eval('mut & const')


@type_lang
def test_files(TM):
    tli = TypeLangInterpreter(tm := TM())
    thisPath = os.path.dirname(__file__)
    tli.eval(antlr4.FileStream(os.path.join(thisPath, 'example.tl')))


@xfail
@type_lang
def test_pp(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        isin: txt: financial: atom
        mod1.cusip: cusip & txt in financial
    ''')

    # the type manager is responsible for pretty printing
    # in Python we could keep a backpointer in the PyBType to the type manager that created it (adding 8 bytes to a
    # to a 24 byte object slot) - is this convenience worth the cost? we can assume that in coppertop debugging the
    # __repr__ method will use the global type manager (and the global namespace only?)

    assert tm.pp(tm['mod1.cusip'], tm.namespace('mod1')) == 'cusip'
    assert tm.pp(tm['mod1.cusip'], tm.namespace('global')) == 't77 & txt in financial'
    assert tm.pp(tm['isin & txt'], tm.namespace('global')) == 'txt & isin'

    # from global import isin as ISIN
    assert tm.pp(tm['ISIN'], tm.namespace('mod1'), use_root_names=False) == 'ISIN'
    assert tm.pp(tm['ISIN'], tm.namespace('mod1'), use_root_names=True) == 'isin'

    # OPEN: requirements
    # - need to be able to specify when to use names (it may be helpful sometimes to even just use t77 etc)
    pass



@type_lang
def debug(TM):
    tli = TypeLangInterpreter(tm := TM())
    tli.eval('''
        f64: null: atom
        f64list: f64 * f64list + null
    ''')





def main():
    fns = [
        test_recursive_space,
        test_runtime_ccy,
        test_atom1,
        test_atom2,
        # test_atom_redefine,
        test_intersection,
        # test_intersection_redefine,
        test_complicated_spaces,
        test_union,
        # test_namespaces,
        test_fitsWithin,
        test_intersection_union_precedence,
        test_tuple,
        test_paren,
        test_doc2_othogonal_spaces,
        # test_arrow_intersections,
        test_runtime_ccy,
        test_runtime_fx,
        test_runtime_fx_err,
        test_static_fx1,
        # test_static_fx2,
        test_pyAndPylistEtc,
        test_cStyleConst,
        test_files,
        # test_pp,                  // requires namespaces
    ]

    TMs = (PyTypeManager, JonesTypeManager)

    for fn in fns:
        for TM in TMs:
            print('----------------------------------------------------------------------------------')
            print(f'{fn.__name__} - {TM.__name__}')
            print('----------------------------------------------------------------------------------')
            fn(TM)
    print('----------------------------------------------------------------------------------')


if __name__ == '__main__':
    main()
    print('passed')
