# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************


from coppertop.pipe import *
from coppertop.dm.pp import PP

from coppertop._testing_ import take2
take2._take >> typeOf >> PP

from coppertop._testing_ import take1
take1._take >> typeOf >> PP

from coppertop._testing_.take1 import _take as fred    # pylist*T ^ pylist
fred >> typeOf >> PP

from coppertop._testing_.take2 import _take as joe    # pylist*T ^ pylist
joe >> typeOf >> PP

from coppertop._testing_.take1 import _take as sally    # pydict*T ^ pydict
sally >> typeOf >> PP

from coppertop._testing_.take2 import _take as sally    # pydict*T ^ pydict
sally >> typeOf >> PP

from coppertop._testing_.take1 import _take
_take >> typeOf >> PP

from coppertop._testing_.take2 import _take     # pydict*T ^ pydict
_take >> typeOf >> PP

