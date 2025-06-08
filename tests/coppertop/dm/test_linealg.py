# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *
from coppertop.dm.core import to, shape
from coppertop.dm.utils.testing import assertRaises
from coppertop.dm.core.types import matrix, darray
from coppertop.dm.testing import check, equals
from coppertop.dm.core.conv import to
from coppertop.dm.pp import PP


def test():
    A = [[1, 2], [3, 5]] >> to >> (matrix&darray)
    b = [1, 2] >> to >> (matrix&darray) >> PP
    A @ b >> shape >> check >> equals >> (2,1)
    with assertRaises(Exception) as e:
        b @ A



def main():
    test()


if __name__ == '__main__':
    main()
    print('pass')
