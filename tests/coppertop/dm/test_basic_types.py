# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

# map, seq are abstract?
# pydict, pylist, pyset, pytuple are

from coppertop.pipe import *
from bones.ts.metatypes import BType
from coppertop.dm.core.types import txt, num, count, index, offset, dmap, dseq

from coppertop.dm.core.aggman import join
from coppertop.dm.testing import check, equals, different


def test_txt():
    txt('hello') >> join >> ' world' >> check >> equals >> 'hello world'
    ('hello' | txt) >> check >> equals >> 'hello'
    'hello' >> typeOf >> check >> fitsWithin >> txt

    # the intersection safetxt will use the txt coercer / construction
    safetxt = BType('safetxt: safetxt & txt in mem')
    safetxt('hello') >> join >> safetxt(' world') >> check >> equals >> 'hello world'
    'hello world' >> check >> different >> safetxt('hello world')

    x = 'hello' | txt
    y = x | safetxt
#

# @coppertop(style=binary)
# def different(a, b) -> bool:
#     return not fitsWithin(typeOf(a), typeOf(b)) or a != b
#
# @coppertop(style=binary, dispatchEvenIfAllTypes=True)
# def equals(a, b) -> bool:
#     return fitsWithin(typeOf(a), typeOf(b)) and a == b
#
# @coppertop(style=binary)
# def join(s1:txt, s2:txt) -> txt:
#     return s1 + s2
#
# @coppertop(style=binary)
# def join(s1:txt[T1], s2:txt[T1], tByT) -> txt[T1]:
#     return s1 + s2





