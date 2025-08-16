# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************


from coppertop.pipe import *
from coppertop.utils import assertRaises
from coppertop.dm.testing import check, equals
from coppertop.dm.core.text_report import display_table, join
from coppertop.dm.core import matrix
from coppertop.dm.linalg.core import to
from coppertop.dm.pp import PP



def test_basic_join():
    with assertRaises(ValueError):
        display_table([])

    with assertRaises(ValueError):
        display_table(['1 ', '2'])

    display_table(['1 ', '2 ', '3 ']) >> join >> display_table(['A', 'B', 'C']) >> check >> equals >> \
        display_table(['1 A', '2 B', '3 C'])

    display_table(['1 ', '2 ', '3 ']) >> join >> display_table(['B']) >> check >> equals >> \
        display_table(['1  ', '2 B', '3  '])

    display_table(['2 ']) >> join >> display_table(['A', 'B', 'C']) >> check >> equals >> \
        display_table(['  A', '2 B', '  C'])


def test_numpy():
    matrix([[1,2,3], [4,5,6], [7,8,9]]) >> to >> display_table >> check >> equals >> \
        display_table(['[[1 2 3] ', ' [4 5 6] ', ' [7 8 9]]'])


def test_join_with_options():
    pass


if __name__ == '__main__':
    test_basic_join()
    test_numpy()
    test_join_with_options()
    'passed' >> PP

