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

import enum, pytest
skip = pytest.mark.skip

from coppertop.pipe import *
from coppertop.utils import assertRaises
from coppertop.dm.testing import check #, subClassOf
from coppertop.dm.core import sequence, collect, inject, atSlot, atSlotPut, closeTo, to
from coppertop.dm.core.comparisons import equals, different
from coppertop.dm.core.types import dstruct, pyndarray
from coppertop.dm.polarframe import polarframe, polarseries, at



@skip
def test_lots():

    f = polarframe(a=[1,2,1,2,1,2], b=[2,2,2,1,1,1], c=['a','b','c','d','e','f'])
    g = polarframe([
        {'a':1, 'b':2, 'c':'a'},
        {'a':2, 'b':2, 'c':'b'},
        {'a':1, 'b':2, 'c':'c'},
        {'a':2, 'b':1, 'c':'d'},
        {'a':1, 'b':1, 'c':'e'},
        {'a':2, 'b':1, 'c':'f'}
    ])
    h = polarframe({
        'a': [1,2,1,2,1,2],
        'b': [2,2,2,1,1,1],
        'c': ['a','b','c','d','e','f']
    })

    f >> check >> equals >> g

    f >> at >> 'a' >> check >> equals >> polarseries(a=[1, 2, 1, 2, 1, 2])
    f >> at >> ['a', 'b']  >> check >> equals >> polarframe(a=[1, 2, 1, 2, 1, 2], b=[2, 2, 2, 1, 1, 1])
    f >> at >> ['a', 'b', 'c'] >> check >> equals >> h


if __name__ == '__main__':
    test_lots()
    print('Passed')
