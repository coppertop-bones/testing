# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import sys, builtins
# sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

from coppertop.pipe import *
from coppertop.dm.utils.testing import assertRaises
from coppertop.dm.testing import check, equals
from coppertop.dm.core import collect, interleave
from coppertop.dm.pp import PP
from coppertop.dm.core.types import txt, index, num, bool, T1, litint, pylist
from bones.ts.metatypes import BTAtom
from coppertop.dm._core.structs import tv

from coppertop._testing_.int_adders import addOne, eachAddOne, eachAddTwo


A = BTAtom("A")
B = BTAtom("B")
(A & B & litint).setCoercer(tv)
(A & litint).setCoercer(tv)
(B & litint).setCoercer(tv)



@coppertop
def fred(a:index, b:txt, c:bool, d, e:num, f:num, g:txt+num) -> txt:
    return [a,b,c,d,e,f,g] >> collect >> typeOf >> collect >> builtins.str >> interleave >> ","
    # [a,b,c,d,e,f,g] collect {e typeOf to(,<:txt>)} interleave ","

@coppertop
def addOneAgain(x: txt) -> txt:
    return x + 'One'

@coppertop
def addOneAgain(x):
    return x + 1

@coppertop
def addOneAgain(x):
    return x + 2

@coppertop
def joe(x:pylist):
    return x

@coppertop
def sally(x:T1 & A & B, tByT):
    return f"AB {tByT[T1]}"

@coppertop
def sally(x:T1&A, tByT):
    return f"A {tByT[T1]}"



def test_sally():
    with context(stop=True):
        (1 | (litint & A & B)) >> sally >> check >> equals >> "AB litint"
        (1 | (litint & A)) >> sally >> check >> equals >> "A litint"
        with assertRaises(Exception):
            1 | (litint & B) >> sally >> check >> equals >> "A"

def test_joe():
    # check joe can't be called with dict_keys
    with assertRaises(Exception):
        dict(a=1).keys() >> joe

def test_redefine():
    1 >> addOneAgain >> check >> equals >> 3

def check_types_of_weak_things():
    fred(1 | index, "hello", True, (), 1, 1.3, 1.3 | num) >> check >> equals >> "index,txt,bool,pytuple,litint,litnum,num"


def main():
    test_sally()
    test_redefine()
    check_types_of_weak_things()
    test_joe()


if __name__ == '__main__':
    main()
    print('pass')

