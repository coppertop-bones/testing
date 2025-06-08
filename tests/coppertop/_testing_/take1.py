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
from coppertop.dm.core.types import pylist, pytuple, index

ellipsis = type(...)


sys._BREAK = True  # hasattr(sys, '_BREAK') and sys._BREAK


@coppertop(style=binary)
def _take(xs:pylist, n:index) -> pylist:
    '''hello'''
    if n >= 0:
        return xs[:n]
    else:
        return xs[len(xs) + n:]

@coppertop(style=binary)
def _take(xs: pylist, os: pylist) -> pylist:
    '''there'''
    return [xs[o] for o in os]

@coppertop(style=binary)
def _take(xs:pylist, ss:pytuple) -> pylist:
    s1, s2 = ss
    if s1 is Ellipsis:
        if s2 is Ellipsis:
            return xs
        else:
            return xs[:s2]
    else:
        if s2 is Ellipsis:
            return xs[s1:]
        else:
            return xs[s1:s2]
