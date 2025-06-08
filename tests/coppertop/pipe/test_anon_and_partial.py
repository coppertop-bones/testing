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
from coppertop.dm.utils.testing import assertRaises
from coppertop.dm.testing import check, equals
from coppertop.dm.core.aggman import collect
from coppertop.dm.core.types import txt, index, N, py, dseq, pylist


def test_anon():
    f = makeFn(index^index, lambda x: x + 1)
    N ** index
    fxs = dseq((N ** index)[dseq], [1, 2, 3]) >> collect >> f
    fxs >> check >> typeOf >> (N ** index)[dseq]
    with assertRaises(TypeError):
        dseq((N ** index)[dseq], [1, 2, 3]) >> collect >> makeFn(txt ^ txt, lambda x: x + 1)


def test_partial():
    @coppertop
    def myunary_(a, b, c):
        return a + b + c
    myunary_ >> typeOf >> check >> equals >> ((py*py*py)^py)

    @coppertop
    def myunary(a: index, b: index, c: index) -> index:
        return a + b + c

    myunary >> check >> typeOf >> ((index*index*index)^index)
    myunary(1,_,3) >> check >> typeOf >> (index^index)

    [1, 2, 3] >> collect >> myunary(0,_,1) >> check >> typeOf >> pylist >> check >> equals >> [2,3,4]

    [1,2,3] >> collect >> makeFn((index*index) ^ index, lambda x, y: x + y)(_, 1) >> check >> equals >> [2,3,4]


def main():
    test_anon()
    test_partial()


if __name__ == '__main__':
    main()
    print('pass')

