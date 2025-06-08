# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import sys, itertools, pytest

from coppertop.pipe import *

from bones import jones
from bones.core.sentinels import Missing
from bones.core.errors import NotYetImplemented

from coppertop.dm.core.types import pylist, pytuple
from coppertop.dm.testing import check, raises, equals, gt, different
from coppertop.dm.pp import PP


@coppertop(style=binary)
def apply_(fn, arg):
    return lambda : fn(arg)

@coppertop(style=binary)
def apply_(fn, args:pylist+pytuple):
    return lambda : fn(*args)


@pytest.mark.xfail
def test_em():
    k = jones.Kernel()
    em = k.em

    e = em.enum('excl', 'mem')
    e.id >> check >> equals >> 1
    em.enum('excl', 'mem').id  >> check >> equals >> 1

    e = em.setEnumTo('excl', 'ccy', 2)
    e.id >> check >> equals >> 2
    em.enum('excl', 'ccy').id  >> check >> equals >> 2

    e = em.enum('fred', 'mem')
    e.id >> check >> equals >> 1
    em.enum('fred', 'mem').id >> check >> equals >> 1

    em.setEnumTo(['fred', 'mem', 1]).id >> check >> equals >> 1
    em.setEnumTo >> apply_ >> ('fred', 'mem', 2) >> check >> raises >> ValueError

    return "test_em passed"



def main():
    test_em() >> PP



if __name__ == '__main__':
    main()
    'passed' >> PP

