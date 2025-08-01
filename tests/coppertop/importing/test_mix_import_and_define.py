# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************


import polars as pl
from coppertop.pipe import *
from coppertop.dm.core import diffRows
from coppertop.dm.pp import PP


sig1 = diffRows >> sig >> PP

@coppertop
def diffRows(f: pl.DataFrame) -> pl.DataFrame:
    numericColNames = [cn for cn, t in f.schema.items() if t.is_numeric()]
    return f.with_columns(pl.col(numericColNames) - pl.col(numericColNames).shift(1))[1:]

sig2 = diffRows >> sig >> PP

assert len(sig2) > len(sig1)

