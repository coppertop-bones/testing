# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import pytest
xfail = pytest.mark.xfail
skip = pytest.mark.skip

from bones.lang._testing_.utils import newKernel
from coppertop.dm.testing import check, equals
from bones.lang.types import mem, cstruct
from bones.ts.metatypes import BType


@xfail
def test():
    k = newKernel()

    # create a C struct type, instantiate it, navigate it by name and index, free it - malloc and free for moment
    # simple object manager can malloc sizeof meta + sizeof struct and return a pointer to the struct
    tFred = BType('fred: {a: i8, b: f64} & cstruct in mem')
    fred = k.alloc(tFred)
    fred.a = 1
    fred.b = 2.0
    fred.a >> check >> equals >> 1
    fred.b >> check >> equals >> 2.0

    res = k.free(fred)



if __name__ == '__main__':
    test()
    print('pass')
