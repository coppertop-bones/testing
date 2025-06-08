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

from coppertop.pipe import *
from bones.core.sentinels import Missing
from bones.lang.symbol_table import SymTab
import bones.lang.symbol_table
# from bones.lang.infer import InferenceLogger

from bones.lang._testing_.utils import stripSrc, pace, evalPyInComments, errorMsg, pace_, newKernel
from coppertop.dm.testing import check
from coppertop.dm.core import startsWith, drop
# from coppertop.dm.core import equals

import coppertop.dm.pp, coppertop.dm.testing
from coppertop.dm.core.types import litint, littxt, void, litnum, num, index, txt, T1, T2, T3, T4, T5, bool, count, pylist
from _ import *

bones.lang.symbol_table.PYCHARM = True


@xfail(reason='needs love')
@bones_lang
def test_ex_partitions(**ctx):
    k = newKernel()

    src = r'''
        load coppertop.dm.core, coppertop.dm.testing, coppertop.dm.core.bones2
        from coppertop.dm.core import sum, count, isEmpty, first, collect, joinAll, prependTo, to, takeDrop, join, equals
        from coppertop.dm.core.bones2 import ifTrue:
        from coppertop.dm.testing import check
        
        partitions: {{[xs, sizes]
            sizes sum check equals (xs count)
            xs _partitions(, xs count, sizes)
        }}
        
        _partitions: {[xs, n, sizes]
            sizes isEmpty ifTrue: [^ (())]
            xs _combRest(, n, sizes first) collect {[a, b]
                _partitions(b, .n - (.sizes first), .sizes drop 1) collect {
                    .a prependTo r
                }
            } joinAll
        }
        
        _combRest: {[xs, n, m]
            m == 0 ifTrue: [^ ( ((), xs) ) to <:N**T1>]
            m == n ifTrue: [^ ( (xs, ()) ) to <:N**T1>]
            (s1, s2): xs takeDrop 1
            _combRest(s2, s2 count, m - 1) collect { (.s1 join a, b) }    // #1
              join
              _combRest(s2, s2 count, m) collect { (a, .s1 join b) }      // #2
        }
    ''' >> stripSrc

    if context.analyse:
        context.testcase = 'overload fail - static'
        res = src >> withCtx >> ctx >> pace(k,_) >> evalPyInComments
        res \
            >> check >> errorMsg >> startsWith >> 'cannot constrain {littxt} <:' \
            >> check >> (lambda x: [e[1] for e in x.types]) >> drop >> 2 >> equals >> res.commentTypes
    else:
        context.testcase = 'run partitions'
        src >> pace(k, _)
        src >> withCtx >> ctx >> check >> pace_(k, _)
        #>> raises >> TypeError




def main():

    debug = dict(showSrc=True, showGroups=False, showTc=True, RESTRICT_NOTES=False, ALL=False)#, tt=InferenceLogger())
    debugNoRun = dict(showSrc=True, showGroups=False, showTc=True, RESTRICT_NOTES=False, ALL=False, run=False)#, tt=InferenceLogger())

    test_partitionExample()




if __name__ == '__main__':
    main()
    print('pass')
