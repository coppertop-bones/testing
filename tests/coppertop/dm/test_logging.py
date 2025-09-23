# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import sys, io
from coppertop.dm.utils import logging
from coppertop.dm.utils.logging import getLogger, setLevel, setFfn, setFmt, setDtFmt
from coppertop.dm.testing import check, equals, identicalTo


def test_logging1():
    s = io.StringIO()

    l1 = logging.getLogger(__name__ + 'logging1')
    l2 = l1.setLevel(logging.DEBUG)
    h1 = l2.setFfn(s)
    h2 = h1.setFmt('%(asctime)s-%(levelname)s-%(name)s>>%(funcName)s:%(lineno)d:  %(message)s')
    h3 = h2.setDtFmt('%Y-%m-%d %H:%M:%S')

    l2 >> check >> identicalTo >> l1
    h2 >> getLogger >> check >> identicalTo >> l1
    h3 >> getLogger >> check >> identicalTo >> l1

    'fred' >> l1.info >> check >> equals >> 'fred'
    h1 >> getLogger >> check >> identicalTo >> l1
    h2 >> getLogger >> check >> identicalTo >> l1
    h3 >> getLogger >> check >> identicalTo >> l1

    s.getvalue()[-5:] >> check >> equals >> 'fred\n'


def test_logging2():
    s = io.StringIO()

    l1 = (__name__ + 'logging2') >> logging.getLogger
    l2 = l1 >> setLevel >> logging.INFO
    h1 = l2 >> setFfn >> s
    h2 = h1 >> setFmt >> '%(asctime)s-%(levelname)s-%(name)s>>%(funcName)s:%(lineno)d:  %(message)s'
    h3 = h2 >> setDtFmt >> '%Y-%m-%d %H:%M:%S'

    l2 >> check >> identicalTo >> l1
    h2 >> getLogger >> check >> identicalTo >> l1
    h3 >> getLogger >> check >> identicalTo >> l1

    'fred' >> l1.info >> check >> equals >> 'fred'
    h1 >> getLogger >> check >> identicalTo >> l1
    h2 >> getLogger >> check >> identicalTo >> l1
    h3 >> getLogger >> check >> identicalTo >> l1

    s.getvalue()[-5:] >> check >> equals >> 'fred\n'


def main():
    test_logging1()
    test_logging2()


if __name__ == '__main__':
    main()
    print('pass')

