# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import pytest
type_system = pytest.mark.type_system

from coppertop.pipe import *
from bones.ts.metatypes import BType, BTAtom, BTStruct, weaken, updateSchemaVarsWith, fitsWithin as _fitsWithin
import bones.ts.metatypes
from coppertop.dm.testing import check, fitsWithin, doesNotFitWithin, equals
from coppertop.dm.core.types import index, count, num, txt, N,  T, T1, T2, T3, T4, num, pylist, pydict, litnum
from coppertop.dm.finance.types import ccy
from coppertop.dm.core.aggman import atAll


oldWeakenings = bones.ts.metatypes._weakenings

weaken(index, num)

tFred = BTAtom('fred')
tJoe = BTAtom('joe')
tSally = BTAtom('sally')




@type_system
def testSimple():
    # exact
    num >> check >> fitsWithin >> num
    num+txt >> check >> fitsWithin >> num+txt

    # T
    num >> check >> fitsWithin >> T
    num+txt >> check >> fitsWithin >> T
    num**num >> check >> fitsWithin >> T

    # union
    num >> check >> fitsWithin >> txt+num
    txt+num >> check >> doesNotFitWithin >> num

    # coercion via rules
    index >> check >> fitsWithin >> num
    index >> check >> fitsWithin >> index
    count >> check >> doesNotFitWithin >> index
    num >> check >> doesNotFitWithin >> index
    count >> check >> doesNotFitWithin >> num
    litnum >> check >> fitsWithin >> num
    # float >> check >> fitsWithin >> num


@type_system
def testNested():
    GBP = BType('GBP: GBP & ccy')
    USD = BType('USD: USD & ccy')
    weaken((index, num, index, num), (ccy[T], GBP, USD))

    index >> check >> fitsWithin >> GBP
    GBP >> check >> doesNotFitWithin >> index
    index >> check >> doesNotFitWithin >> ccy
    num >> check >> fitsWithin >> ccy[T]

    num*txt >> check >> fitsWithin >> (num+index)*(txt+GBP)
    BTStruct(a=num, b=num) >> check >> fitsWithin >> BTStruct(a=num)


@type_system
def test_schemaVars():
    fred = BTAtom('fred')
    num*fred >> check >> fitsWithin >> T*fred
    index*fred >> check >> fitsWithin >> T1*T2

    # simple wildcards
    (N ** fred)[pylist] >> check >> fitsWithin >> (N ** T1)[T2]
    (N ** fred)[pylist] >> check >> doesNotFitWithin >> (N ** T)[pydict]
    (txt ** fred)[pylist] >> check >> doesNotFitWithin >> (N ** T1)[pylist]
    (fred ** txt)[pylist] >> check >> fitsWithin >> (T1 ** T2)[pylist]
    (fred ** txt)[pylist] >> check >> fitsWithin >> (T1 ** T2)[T3]
    (fred ** txt)[pylist] >> check >> doesNotFitWithin >> (T1 ** T2)[pydict]
    (fred ** txt)[pylist] >> check >> doesNotFitWithin >> (T1 ** T1)[pylist]


@type_system
def test_schema():

    account = BType('account: account & txt')
    weaken(txt, account)

    positions = BType('positions: positions & (account**num) & pydict')
    accounts = (N**account)[pylist]

    t1, t2, t3 = account, num, positions

    schemaVars1, running = {}, 0
    schemaVars1, running = updateSchemaVarsWith(schemaVars1, running, r1 := positions >> fitsWithin >> (T1**T2)[pydict][T3]  )
    r2 = accounts >> fitsWithin >> (N ** T1)[pylist]
    schemaVars1, running = updateSchemaVarsWith(schemaVars1, running, r2 )
    schemaVars1, running = updateSchemaVarsWith(schemaVars1, running, r3 := num >> fitsWithin >> T2  )

    assert r1 and r2 and r3
    schemaVars1 >> atAll >> (T1, T2, T3) >> check >> equals >> [t1, t2, t3]


    schemaVars2, running2 = {}, 0
    schemaVars2, running2 = updateSchemaVarsWith(schemaVars2, running2, r4 := num >> fitsWithin >> T2  )
    schemaVars2, running2 = updateSchemaVarsWith(schemaVars2, running2, r5 := accounts >> fitsWithin >> (N**T1)[pylist]  )
    schemaVars2, running2 = updateSchemaVarsWith(schemaVars2, running2, r6 := positions >> fitsWithin >> (T1**T2)[pydict][T3]  )

    assert r4 and r5 and r6
    schemaVars2 >> atAll >> (T1, T2, T3) >> check >> equals >> [t1, t2, t3]


    schemaVars3, running3 = {}, 0
    schemaVars3, running3 = updateSchemaVarsWith(schemaVars3, running3, r7 := num >> fitsWithin >> T2)
    schemaVars3, running3 = updateSchemaVarsWith(schemaVars3, running3, r8 := accounts >> fitsWithin >> T1)
    schemaVars3, running3 = updateSchemaVarsWith(schemaVars3, running3, r9 := positions >> fitsWithin >> (T4 ** T2)[pydict][T3])

    assert r7 and r8 and r9
    schemaVars3 >> atAll >> (T1, T2, T3, T4) >> check >> equals >> [accounts, num, positions, account]



def main():
    testSimple()
    testNested()
    test_schemaVars()
    test_schema()


if __name__ == '__main__':
    main()
    print('pass')

bones.ts.metatypes._weakenings = oldWeakenings
