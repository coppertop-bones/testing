# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *
from bones.kernel import psm
from bones.kernel.bones import BonesKernel
from bones.lang.core import GLOBAL, SCRATCH
from bones.lang.symbol_table import SymTab
from bones.lang.lex import LINE_COMMENT
from bones.lang.execute import TCInterpreter
from bones.lang.types import litsym, litdate
from coppertop.dm.testing import check, equals, raises, same
from coppertop.dm.pp import PP, TT, DD, HH
from coppertop.dm.core.types import txt, dframe
from coppertop.dm.core.structs import _tvstruct, _tvtuple
from bones.lang import lex
from bones.core.errors import GroupError
from bones.lang.parse_groups import parseStructure, TUPLE_NULL, TUPLE_OR_PAREN, TUPLE_2D, TUPLE_0_EMPTY, TUPLE_1_EMPTY, \
    TUPLE_2_EMPTY, TUPLE_3_EMPTY, TUPLE_4_PLUS_EMPTY, SnippetGp
from bones.core.sentinels import function, Missing


def newKernel():
    sm = psm.PythonStorageManager()
    k = BonesKernel(sm, litdateCons=litdate, litsymCons=litsym, littupCons=_tvtuple, litstructCons=_tvstruct, litframeCons=dframe)
    k.ctxs[GLOBAL] = SymTab(k, Missing, Missing, Missing, Missing, GLOBAL)
    k.ctxs[SCRATCH] = scratchCtx = SymTab(k, Missing, Missing, Missing, k.ctxs[GLOBAL], SCRATCH)
    k.scratch = scratchCtx
    k.tcrunner = TCInterpreter(k, scratchCtx)
    sm.framesForSymTab(k.ctxs[GLOBAL])
    sm.framesForSymTab(k.ctxs[SCRATCH])
    return k

@coppertop
def stripSrc(s):
    return (s[1:] if s[0:1] == '\n' else s).rstrip()

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
def pace(k, src, stopAtLine):
    return k.pace(src, stopAtLine)

@coppertop
def pace_(k, src, stopAtLine):
    return lambda : k.pace(src, stopAtLine)

@coppertop
def group(src:txt, k):
    tokens, lines = lex.lexBonesSrc(0, src)
    return parseStructure(tokens, k.scratch, src)

@coppertop
def group_(src:txt, k) -> function:
    return lambda : src >> group(_, k)

@coppertop
def bb(g:SnippetGp) -> txt:
    return g.PPGroup

@coppertop
def stripSpace(x):
    return x.replace(' ', '')

@coppertop(style=binary)
def forcase(any, testcase):
    context.testcase = testcase
    return any

@coppertop
def setcase(testcase):
    context.testcase = testcase
    return None
