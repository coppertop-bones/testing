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
from coppertop.dm.core.types import litint, litnum, num, count as tCount, err, T, T1, T2
from bones.core.errors import NotYetImplemented



# **********************************************************************************************************************
# addition
# **********************************************************************************************************************

@coppertop(style=binary, name='+')
def add_(a:num, b:num) -> num:
    return a + b

@coppertop(style=binary, name='+')
def add_(a:litint, b:litint) -> litint:
    return a + b

@coppertop(style=binary, name='+')
def add_(a:litnum, b:litnum) -> litnum:
    return a + b

@coppertop(style=binary, name='+')
def add_(a:tCount, b:tCount) -> tCount:
    return a + b

# @coppertop(style=binary, name='+')
# def add_(a:err&T1, b:T2) -> err&T1:
#     raise NotYetImplemented()
#
# @coppertop(style=binary, name='+')
# def add_(a:T1, b:err&T2) -> err&T2:
#     raise NotYetImplemented()
#
# @coppertop(style=binary, name='+')
# def add_(a:err&T1, b:err&T1) -> err&T1:
#     raise NotYetImplemented()


# **********************************************************************************************************************
# subtraction
# **********************************************************************************************************************

@coppertop(style=binary, name='-')
def sub_(a:num, b:num) -> num:
    return a - b

@coppertop(style=binary, name='-')
def sub_(a:litint, b:litint) -> litint:
    return a - b

@coppertop(style=binary, name='-')
def sub_(a:litnum, b:litnum) -> litnum:
    return a - b

@coppertop(style=binary, name='-')
def sub_(a:tCount, b:tCount) -> tCount:
    return a - b

@coppertop(style=binary, name='-')
def sub_(a:err&T1, b:T2) -> err&T1:
    raise NotYetImplemented()

@coppertop(style=binary, name='-')
def sub_(a:T1, b:err&T2) -> err&T2:
    raise NotYetImplemented()

@coppertop(style=binary, name='-')
def sub_(a:err&T1, b:err&T1) -> err&T1:
    raise NotYetImplemented()


# **********************************************************************************************************************
# multiplication
# **********************************************************************************************************************

@coppertop(style=binary, name='*')
def mul_(a:num, b:num) -> num:
    return a * b

@coppertop(style=binary, name='*')
def mul_(a:litint, b:litint) -> litint:
    return a * b

@coppertop(style=binary, name='*')
def mul_(a:litnum, b:litnum) -> litnum:
    return a * b

@coppertop(style=binary, name='*')
def mul_(a:err&T1, b:T2) -> err&T1:
    raise NotYetImplemented()

@coppertop(style=binary, name='*')
def mul_(a:T1, b:err&T2) -> err&T2:
    raise NotYetImplemented()

@coppertop(style=binary, name='*')
def mul_(a:err&T1, b:err&T1) -> err&T1:
    raise NotYetImplemented()


# **********************************************************************************************************************
# division
# **********************************************************************************************************************

@coppertop(style=binary, name='/')
def div_(a:num, b:num) -> num + err&T:
    return a / b

@coppertop(style=binary, name='/')
def div_(a:err&T1, b:T2) -> err&T1:
    raise NotYetImplemented()

@coppertop(style=binary, name='/')
def div_(a:T1, b:err&T2) -> err&T2:
    raise NotYetImplemented()

@coppertop(style=binary, name='/')
def div_(a:err&T1, b:err&T1) -> err&T1:
    raise NotYetImplemented()


