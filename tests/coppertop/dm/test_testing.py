# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.dm.core import count, pyeval_
from coppertop.dm.testing import check, same, equals, raises


def test_testing():
    [1,2,3] >> check >> same >> len >> {'a':1,'b':2,'c':3}
    '1/0' >> pyeval_ >> check >> raises >> ZeroDivisionError
    10 >> check >> equals >> 100 / 10


def main():
    test_testing()


if __name__ == '__main__':
    main()
    print('pass')

