# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************


from coppertop.pipe import *
from coppertop.dm.testing import check, equals
from bones.core.test_utils import assertRaises
from coppertop.dm.core.types import pyint, txt

from coppertop._testing_.add_one_int import addOne

1 >> addOne >> typeOf >> check >> equals >> pyint

from coppertop._testing_.add_one_txt import addOne
'Two' >> addOne >> typeOf >> check >> equals >> txt
1 >> addOne >> typeOf >> check >> equals >> pyint

print('passed')
