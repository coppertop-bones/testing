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
from coppertop.utils import Missing
from bones.kernel.core import BonesKernel
import bones.kernel.symbol_table
from bones.kernel.lex import LINE_COMMENT, BREAKOUT
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
    k = BonesKernel(litdateCons=litdate, litsymCons=litsym, littupCons=_tvtuple, litstructCons=_tvstruct, litframeCons=dframe)
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
def test_1(**ctx):
    k = _newKernel()

    src = r'''
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
        # src >> withCtx >> ctx >> check >> pace_(k, _) >> raises >> TypeError
        src >> withCtx >> ctx >> pace(k, _)



def main():
    # from bones.lang.infer import InferenceLogger
    debug = dict(showSrc=True, showGroups=False, showTc=True, RESTRICT_NOTES=False, ALL=False) #, tt=InferenceLogger())
    debugNoRun = dict(showSrc=True, showGroups=False, showTc=True, RESTRICT_NOTES=False, ALL=False, run=False) #, tt=InferenceLogger())

    test_1(**debugNoRun)


if __name__ == '__main__':
    main()
    print('pass')
