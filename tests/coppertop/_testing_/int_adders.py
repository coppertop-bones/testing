# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *
from coppertop.dm.core.types import index, pylist


@coppertop
def addOne(x:index) -> index:
    return x + 1

# test that functions can be redefined in the same file (and thus same module)
@coppertop
def addOne(x: index) -> index:
    return x + 1

@coppertop
def eachAddOne(xs:pylist) -> pylist:
    answer = []
    for x in xs:
        answer.append(x >> addOne)
    return answer

@coppertop
def addTwo(x:index) -> index:
    return x + 2

from _ import addTwo

@coppertop
def eachAddTwo(xs:pylist) -> pylist:
    answer = []
    for x in xs:
        answer.append(x >> addTwo)
    return answer
