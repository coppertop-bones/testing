# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import pytest
bones_lang = pytest.mark.bones_lang
xfail = pytest.mark.xfail
skip = pytest.mark.skip


from coppertop.pipe import *
from bones.core.sentinels import Missing
from bones.kernel import psm
from bones.kernel.bones import BonesKernel
from bones.kernel.core import GLOBAL_CTX, SCRATCH_CTX
from bones.kernel.symbol_table import SymbolTable
import bones.kernel.symbol_table
from bones.parse.lex import LINE_COMMENT, BREAKOUT
from bones.execute.tc_interpreter import TCInterpreter
from bones.lang._testing_.utils import stripSrc
from bones.lang.types import litdate, litsym


from coppertop.dm.testing import check, equals, raises
from coppertop.dm.core import startsWith, underride, withCtx, drop
from coppertop.dm.core.types import litint, littxt, void, litnum, num, index, txt, T1, T2, T3, T4, T5, bool, count, \
    pylist, dframe
from coppertop.dm.core.structs import _tvstruct, _tvtuple
from coppertop.dm.pp import PP


bones.kernel.symbol_table.PYCHARM = True


def _newKernel():
    sm = psm.PythonStorageManager()
    k = BonesKernel(sm, litdateCons=litdate, litsymCons=litsym, littupCons=_tvtuple, litstructCons=_tvstruct, litframeCons=dframe)
    k.ctxs[GLOBAL_CTX] = SymbolTable(k, Missing, Missing, Missing, Missing, GLOBAL_CTX)
    k.ctxs[SCRATCH_CTX] = scratchCtx = SymbolTable(k, Missing, Missing, Missing, k.ctxs[GLOBAL_CTX], SCRATCH_CTX)
    k.scratch = scratchCtx
    k.tcrunner = TCInterpreter(k, scratchCtx)
    sm.framesForSymTab(k.ctxs[GLOBAL_CTX])
    sm.framesForSymTab(k.ctxs[SCRATCH_CTX])
    return k

class Res: pass

@coppertop
def evalPyInComments(res):
    commentTypes = []
    for token in res.tokens:
        if token.tag == LINE_COMMENT:
            pysrc = token.src[2:].strip()
            try:
                t = eval(pysrc)
                commentTypes.append(t)
            except Exception as ex:
                commentTypes.append(ex)
    res2 = Res()
    res2.tokens = res.tokens
    res2.types = res.types
    res2.result = res.result
    res2.error = res.error
    res2.commentTypes = commentTypes
    return res2

@coppertop
def errorMsg(res):
    return res.error.args[0]

@coppertop
def pace(k, src):
    return k.pace(src)

@coppertop
def pace_(k, src):
    return lambda : k.pace(src)



@bones_lang
def test_overload_fail(**ctx):
    k = _newKernel()

    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, true, false, join, +
        b: (true ifTrue: "1.0" ifFalse: 1)      // litint + littxt
        addOne: {x + 1}                         // litint + litnum + num + index + count) ^ (litint + litnum + num + index + count)
        addOne(b)
    ''' >> stripSrc

    if context.analyse:
        context.testcase = 'overload fail - static'
        res = src >> withCtx >> ctx >> pace(k,_) >> evalPyInComments
        res \
            >> check >> errorMsg >> startsWith >> 'cannot constrain {littxt} <:' \
            >> check >> (lambda x: [e[1] for e in x.types]) >> drop >> 2 >> equals >> res.commentTypes
    else:
        context.testcase = 'overload fail - dynamic'
        src >> withCtx >> ctx >> check >> pace_(k, _) >> raises >> TypeError


@bones_lang
def test_fun(**ctx):
    k = _newKernel()

    src = r'''
        // dynamic dispatch
        
        load coppertop.dm.stdlib, coppertop.dm.core, coppertop.dm.testing
        from coppertop.dm.stdlib import *, ifTrue:ifFalse:, true, false, join, +, ==, PP, typeOf
        from coppertop.dm.core import collect, to
        from coppertop.dm.testing import check, equals
        
        addOne: {[x:litint] <:litint> x + 1}                            // type info needed here since we are overloading addOne and in dynamic dispatch mode
        addOne: {[x:littxt] <:littxt> x join "One"}
          
        (1, "Two ") to <:pylist> :fred collect {x addOne} :joe PP
        
        sally: fred collect {                                           // since there is no overload [x:litint + littxt] <:litint + littxt>  is not needed here
            x typeOf == <:litint> ifTrue: {
                x + 1
            } ifFalse: {
                x join "One"
            }
        }
        joe check equals sally
        
    ''' >> stripSrc

    # ctx['showGroups'] = True
    ctx['EE'] = print
    with context(**ctx):
        res = k.pace(src)
        res.result >> typeOf >> check >> equals >> bool
        res.result._v >> check >> equals >> True


@bones_lang
def test_overload(**ctx):
    k = _newKernel()

    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, true, false, join, +
        b: (true ifTrue: "1.0" ifFalse: 1)      // litint + littxt
        addOne: {x + 1}                         // (litint + litnum + num + index) ^ (litint + litnum + num + index)
        addOne: {x join "One"}                  // (txt^txt) & ((litint + litnum + num + index) ^ (litint + litnum + num + index))
        addOne(b)                               // litint + litnum + txt + num + index      # really this should be litint + txt (as littxt is weakened to txt)
    ''' >> stripSrc

    with context(**ctx):
        res = k.pace(src) >> evalPyInComments
        assert res.result == '"1.0""One"'       # OPEN: need to fix the quotes
        types = [e[1] for e in res.types]
        for i, (a, b) in enumerate(zip(types, res.commentTypes)):
            if a != b:
                if a.types != b.types:
                    raise AssertionError(f'{i} : {a} != {b}')


@skip
@bones_lang
def test_SO1(**ctx):
    k = _newKernel()
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, true, false, join, +
        id: {x}                                         // T1 ^ T1
        a: (true ifTrue: id("1.0") ifFalse: id(1))      // litint + littxt
    ''' >> stripSrc
    with context(**ctx, analyse=True):
        res = k.pace(src)
        types = [e[1] for e in res.types]
        for i, (a, b) in enumerate(zip(types, res.commentTypes)):
            if a != b:
                if a.types != b.types:
                    raise AssertionError(f'{i} : {a} != {b}')


@skip
@bones_lang
def test_SO2(**ctx):
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, true, false, join, +
        id: {x}                                 // T1 ^ T1
        foo: {x ifTrue: f(y) ifFalse: f(z)}     // (((T1^T2)&(T3^T4)) * bool * T1 * T3) ^ (T2+T4)
        result: foo(id, true, 1, "hi")          // litint + littxt
    ''' >> stripSrc
    with context(**ctx):
        res = pace(src)
        types = [e[1] for e in res.types]
        for i, (a, b) in enumerate(zip(types, res.commentTypes)):
            if a != b:
                if a.types != b.types:
                    raise AssertionError(f'{i} : {a} != {b}')


@skip
@bones_lang
def test_unionThenOverload(**ctx):
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, true, false, join, +
        a: (true ifTrue: "1.0" ifFalse: 1)      // litint + littxt
        addTwo: {x + 2}                         // (litint + litnum + num + index) ^ (litint + litnum + num + index)
        addTwo: {x join "Two"}                  // (txt ^ txt) & ((litint + litnum + num + index) ^ (litint + litnum + num + index))
        a addTwo                                // litint + litnum + txt + num + index
    ''' >> stripSrc
    with context(**ctx):
        res = pace(src)
        types = [e[1] for e in res.types]
        for i, (a, b) in enumerate(zip(types, res.commentTypes)):
            if a != b:
                if a.types != b.types:
                    raise AssertionError(f'{i} : {a} != {b}')


@skip
@bones_lang
def test_polymorphic1(**ctx):
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import toTxt, join
        thing: {join(f(x), f(y))}               // (((T1^txt) & (T2^txt)) * T1 * T2) ^ txt
        thing(toTxt, 1, "two")                  // txt
    ''' >> stripSrc

    with context(**ctx):
        res = pace(src)
        if res.error: raise res.error
        types = [e[1] for e in res.types]
        for i, (a, b) in enumerate(zip(types, res.commentTypes)):
            if a != b:
                if a.types != b.types:
                    raise AssertionError(f'{i} : {a} != {b}')


@skip
@bones_lang
def test_polymorphic2(**ctx):
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, true, false, join, +
        id: {x}                             // T1 ^ T1
        addTwo: {{f(x) + 2}}                // ((T1 ^ (litint + litnum + num + index)) * T1) ^ (litint + litnum + num + index)
        addTwo: {{f(x) join "Two"}}         // (((T1 ^ (litint + litnum + num + index)) * T1) ^ (litint + litnum + num + index)) & (((T1 ^ txt) * T1) ^ txt)
        addTwo(id, 2)                       // (litint + litnum + num + index + txt)    # unrestricted version
    ''' >> stripSrc
    with context(**ctx):
        res = pace(src)
        if res.error: raise res.error
        types = [e[1] for e in res.types]
        for i, (a, b) in enumerate(zip(types, res.commentTypes)):
            if a != b:
                if a.types != b.types:
                    raise AssertionError(f'{i} : {a} != {b}')


@skip
@bones_lang
def test_polymorphicInFn(**ctx):
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, true, false, join, +, isString, addOne
        add: {x+y}                                  // ((litint+litnum+num+index) * (litint+litnum+num+index)) ^ (litint+litnum+num+index)
        id: {x}                                     // T1 ^ T1
        mapOne: {f(x)}                              // ((T1^T2) * T1) ^ T2
        foo: {x ifTrue: f(1) ifFalse: f("hi")}      // (((litint^T1) & (littxt^T2)) * bool) ^ (T1+T2)
        fooer: {x ifTrue: f(y) ifFalse: f(z)}       // (((T1^T2) & (T3^T4)) * bool * T1 * T3) ^ (T2+T4)
        addOne: {x + 1}                             // (txt^txt) & (index^index) & ((litint+litnum+num+index) ^ (litint+litnum+num+index))
        addOne: {join(x, "One")}                    // (txt^txt) & (index^index) & ((litint+litnum+num+index) ^ (litint+litnum+num+index))
        id(2)                                       // litint
        id("too")                                   // littxt
        mapOne(id, 2)                               // litint
        mapOne(id, "Two")                           // littxt
        mapOne(addOne, 2)                           // litint+litnum+txt+num+index
        foo(id, true)                               // litint+littxt
        foo(addOne, true)                           // litint+litnum+txt+num+index
        fooer(id, true, 1, "Two")                   // litint+littxt
        fooer(addOne, true, 1, "Two")               // litint+litnum+txt+num+index
    ''' >> stripSrc

    with context(**ctx):
        res = pace(src, 14)
        if res.error: raise res.error
        types = [e[1] for e in res.types]
        for i, (a, b) in enumerate(zip(types, res.commentTypes)):
            if a != b:
                if a.types != b.types:
                    raise AssertionError(f'{i} : {a} != {b}')


@skip
@bones_lang
def test_polymorphicInFn2(**ctx):
    src = r'''
        // https://stackoverflow.com/questions/36587571/confusing-about-haskell-type-inference
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, true, false, join, +

        hoo: {x ifTrue: f(y) ifFalse: f(z)}
        addOne: {x + 1}
        addOne: {join(x, "One")}
        hoo(addOne, true, 1, "Two")
    ''' >> stripSrc

    expected = [
        void,
        void,
        T1 ^ T1,
        (((T1 + T2) ^ T3) * bool * T1 * T2) ^ T3,
        litint + littxt,
    ]

    with context(**ctx):
        res = pace(src)
        types = [e[1] for e in res.types]
        types >> check >> equals >> expected


@skip
@bones_lang
def test_polymorphicInFn3(**ctx):
    src = r'''
        // https://stackoverflow.com/questions/36587571/confusing-about-haskell-type-inference
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, true, false, join, +

        fxAddTwo: {f(x) + 2}
        fxAddTwo: {f(x) join "Two"}
        id: {x}
        fxAddTwo(id, 2)
    ''' >> stripSrc

    expected = [
        void,
        void,
        T1 ^ T1,
        (((T1 + T2) ^ T3) * bool * T1 * T2) ^ T3,
        litint + littxt,
    ]

    with context(**ctx):
        res = pace(src)
        types = [e[1] for e in res.types]
        types >> check >> equals >> expected


    # '{[f] {[t] f(t)}}' >> checkSig(False) >> '((a -> b) -> (a -> b))'


@skip
@bones_lang
def test_polymorphicInFn4(**ctx):
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, true, false, join, +

        fxAddTwo: {f(x) + 2}
        fxAddTwo: {f(x) join "Two"}
        addOne: {x + 1}
        addOne: {join(x, "One")}
        fxAddTwo(addOne, 2)
    ''' >> stripSrc

    expected = [
        void,
        void,
        T1 ^ T1,
        (((T1 + T2) ^ T3) * bool * T1 * T2) ^ T3,
        litint + littxt,
    ]

    with context(**ctx):
        res = pace(src)
        types = [e[1] for e in res.types]
        types >> check >> equals >> expected


@skip
@bones_lang
def test_recursive(**ctx):
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, <, ==, count, +, *, PP, true, false, ID, toIndex, join
        range: {
            addAndDec: {if x == 0 addAndDec(acc + x}; x - 1
            addAndDec(x, x-1)
        }
    ''' >> stripSrc

    expected = [
        void,
        void,
        T1 ^ T1,
        (((T1 + T2) ^ T3) * bool * T1 * T2) ^ T3,
        litint + littxt,
    ]

    with context(**ctx):
        res = pace(src)
        types = [e[1] for e in res.types]
        types >> check >> equals >> expected


@skip
@bones_lang
def prog5(**ctx):
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import ifTrue:ifFalse:, <, ==, count, +, *, PP, true, false, toIndex, join
        a = (id 1, id True)
        foo f a b = (f a, f b)
        result = foo id 1 True
    ''' >> stripSrc

    expected = [
        void,
        void,
        T1 ^ T1,
        (((T1 + T2) ^ T3) * bool * T1 * T2) ^ T3,
        litint + littxt,
    ]

    with context(**ctx):
        res = pace(src)
        types = [e[1] for e in res.types]
        types >> check >> equals >> expected


@skip
@bones_lang
def test_compile(**ctx):
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import +
        // add will expose a single overload which is the upper bound of all the overloads of +
        add: {{x + y}}      
        // add2 will expose the 
        add2: {{x add y}}
        // the following apply of add2 will trigger a compile resulting in a new add2 : litint*litint ^ litint and 
        // a new add : litint*litint ^ litint
        1 add2 2
    ''' >> stripSrc

    expected = [
        void,
        void,
        T1 ^ T1,
        (((T1 + T2) ^ T3) * bool * T1 * T2) ^ T3,
        litint + littxt,
    ]

    with context(**ctx):
        res = pace(src)
        types = [e[1] for e in res.types]
        types >> check >> equals >> expected


@skip
@bones_lang
def test_current(**ctx):
    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import +, *, ifTrue:ifFalse:, true, false, ==, join
        x: 1 + 1                        // litint+litnum+num+index
        y: 2                            // index
        x * y
        1 == 1 ifTrue: x + 1 ifFalse: y + 1
        hoo: {x ifTrue: f(y) ifFalse: f(z)}
        addOne: {x + 1}
        addOne: {x join "One"}
        hoo(addOne, 1 == 1, 2, "Two") 
        
        1 == 2 ifTrue: x + 4 ifFalse: y + 8
    ''' >> stripSrc

    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import +, *, ifTrue:ifFalse:, true, false, ==, join
        foo: {g(x, f(x))}         // ((T1^T2) * ((T3*T2) ^ T4) * (T1&T3)) ^ T4
    ''' >> stripSrc

    src = r'''
        load bones.tstlib.core
        from bones.tstlib.core import +, *, ifTrue:ifFalse:, true, false, ==, join
        hoo: {f(y, x)}                  // (((T1*T2)^T3) * T2 * T1) ^ T3
        woo: {g(hoo, f(hoo))}           // ((((T1*T2 ^ T3) * T2 * T1) ^ T3)^T4 * (((((T1*T2 ^ T3) * T2 * T1) ^ T3) * T4) ^ T5)) ^ T5
    ''' >> stripSrc

    src = r'''
        load dm.pmf
        load bones.tstlib.core
        from bones.tstlib.core import +, *
        load dm.core
        //from dm.pmf import toPMF, toL, normalise
        from dm.kitchen_sink import PP, *, /
        bag1994: {Brown:30, Yellow:20, Red:20, Green:10, Orange:10, Tan:10} toPMF PP
        bag1996: {Brown:13, Yellow:14, Red:13, Green:20, Orange:16, Blue:24} toPMF PP.
        prior: {hypA:0.5, hypB:0.5} toPMF PP

        likelihood: {
            hypA:bag1994.Yellow * bag1996.Green, 
            hypB:bag1994.Green * bag1996.Yellow
        } toL PP
        
        post: prior * likelihood normalise PP

    ''' >> stripSrc

    src = r'''
        id: {x}
        bag1994: {Brown:30, Yellow:20, Red:20, Green:10, Orange:10, Tan:10} id
        bag1996: {Brown:13, Yellow:14, Red:13, Green:20, Orange:16, Blue:24} id.
        bag1994.Yellow :numYellow1994
    ''' >> stripSrc


    # schema variables need translating so T1 and T1 don;t conflate - but we don't want to instantiate and constrain
    # when they are not applied...


    with context(**ctx):
        res = pace(src, 3)
        if res.error: raise res.error
        types = [e[1] for e in res.types]
        for i, (a, b) in enumerate(zip(types[2:], res.commentTypes)):
            if a != b:
                try:
                    if a.types != b.types:
                        raise AssertionError(f'{i} : {a} != {b}')
                except:
                    raise AssertionError(f'{i} : {a} != {b}')
    # 1/0


@pytest.fixture(scope='module')
def ctx():
    return {}


# TODO
# assignment of literals weakens them to their defaults
# restrict upper bound of overload according to the types known at the call site


def main():
    # from bones.lang.infer import InferenceLogger
    debug = dict(showSrc=True, showGroups=False, showTc=True, RESTRICT_NOTES=False, ALL=False) #, tt=InferenceLogger())
    debugNoRun = dict(showSrc=True, showGroups=False, showTc=True, RESTRICT_NOTES=False, ALL=False, run=False) #, tt=InferenceLogger())

    # test_current(debug)
    # test_compile()
    test_fun(**debug)
    test_overload_fail(analyse=False)
    test_overload_fail(analyse=True)
    test_overload(**debug)
    test_SO1(**debug)
    test_SO2()
    test_unionThenOverload()
    test_polymorphic1()
    test_polymorphic2()
    test_polymorphicInFn()

    # test_polymorphicInFn3()
    # test_polymorphicInFn4()
    # test_recursive()


# // with [f: (T1 + T2) ^ (txt + N ** T3), x: T1, y: T2] -> (txt + N ** T3)

# %%types
# fred: {x join y}
# fred: {x arrayJoin y}

# hoo: {x ifTrue: f(y) ifFalse: f(z)}
# addOne2: {x + 1}
# addOne2: {join(x, "One")}
# hoo(addOne2, true, 1, "Two")

# bones = """
#
# map: {[collection <:n**T1>, fn <:unary><:(T1) -> T2>]
#     n: collection count <:count>
#     i: 1i
#     resultType: fn typeof answers // or can we refer to T2 below?
#     answer: () <:{n}**{resultType}>
#     i <= n whileTrue: [
#         x: .i
#         i: i + 1o
#         answer(i): fn(collection(i))
#     ]
#     answer
# }
#
# stdout ((1,2,3) map {x+1})
#
# """

if __name__ == '__main__':
    main()
    print('pass')
