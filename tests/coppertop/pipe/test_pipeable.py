# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import sys
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)


from coppertop.pipe import *
from bones.core.errors import NotYetImplemented
from bones.ts.metatypes import BTAtom
from coppertop.dm.utils.testing import assertRaises
from coppertop.dm.testing import check, equals
from coppertop._testing_.take1 import _take
from _.coppertop._testing_.take2 import _take
from coppertop.dm.core.types import index, pylist, litint, darray

mat = BTAtom("mat2")
vec = BTAtom("vec2")


@coppertop(style=binary)
def mmul(A:mat, B:vec) -> vec:
    answer = A @ B | vec
    return answer


def test_mmul():
    a = darray(mat, [[1, 2], [3, 4]])
    b = darray(vec, [1, 2])
    res = a >> mmul >> b
    res >> check >> typeOf >> vec


def testTake():
    [1, 2, 3] >> _take >> 2 >> check >> equals >> [1, 2]
    [1, 2, 3] >> _take >> -2 >> check >> equals >> [2, 3]
    [1, 2, 3] >> _take >> (..., ...) >> check >> equals >> [1, 2, 3]
    [1, 2, 3] >> _take >> (1, ...) >> check >> equals >> [2, 3]
    [1, 2, 3] >> _take >> (..., 2) >> check >> equals >> [1, 2]
    [1, 2, 3] >> _take >> (0, 2) >> check >> equals >> [1, 2]

    {"a":1, "b":2, "c":3} >> _take >> "a" >> check >> equals >> {"a":1}
    {"a":1, "b":2, "c":3} >> _take >> ["a", "b"] >> check >> equals >> {"a":1, "b":2}


def testTypeOf():
    1 >> check >> typeOf >> litint
    1 >> typeOf >> check >> fitsWithin >> index


def testDoc():
    _take(pylist, index).d.__doc__ >> check >> equals >> 'hello'
    _take(pylist, pylist).d.__doc__ >> check >> equals >> 'there'


def main():
    testTake()
    testTypeOf()
    testDoc()
    test_mmul()


if __name__ == '__main__':
    main()
    print('pass')

