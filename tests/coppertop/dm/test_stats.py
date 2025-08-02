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

import pytest
skip = pytest.mark.skip
import numpy as np

from coppertop.pipe import *
from coppertop.dm.testing import check
from coppertop.dm.core import mean, std
from coppertop.dm.core.comparisons import equals, closeTo
from coppertop.dm.core.types import num



def test():
    np.array([1,2,3,4,5,6]) >> mean >> check >> closeTo >> 3.5
    np.array([1,2,3,4,5,6]) >> mean >> typeOf >> check >> equals >> num
    np.array([1,2,3,4,5,6]) >> std >> typeOf >> check >> equals >> num



if __name__ == '__main__':
    test()
    print('Passed')
