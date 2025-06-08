# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at 
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND, 
# either express or implied. See the License for the specific language governing permissions and limitations under the 
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from bones.lang._testing_.utils import group_ as oldgroup_, group as oldgroup, _
from bones.lang._testing_.utils import *


@coppertop
def getTupleType(x):
    return x.phrases[0][0].tupleType


def test_tuple_type():
    k = newKernel()
    group = oldgroup(_, k)
    group_ = oldgroup_(_, k)

    context.testcase = 'null tuple'
    '()' >> group >> check >> getTupleType >> equals >> TUPLE_NULL \
        >> check >> bb >> equals >> '()'
    

    context.testcase = 'tuple or paren'
    '(1 * 2)' >> group >> check >> getTupleType >> equals >> TUPLE_OR_PAREN \
        >> check >> bb >> equals >> '(l o l)'


    context.testcase = '0 emtpy slots'
    '(1 ! 2, 2*3)' >> group >> check >> getTupleType >> equals >> TUPLE_0_EMPTY \
        >> check >> bb >> equals >> '(l o l, l o l)'


    context.testcase = '2D tuple'
    '(1 ! 2; 2*3)' >> group >> check >> getTupleType >> equals >> TUPLE_2D \
        >> check >> bb >> equals >> '(l o l; l o l)'


    context.testcase = '1 empty slot'
    '(1 ! 2,)' >> group >> check >> getTupleType >> equals >> TUPLE_1_EMPTY \
        >> check >> bb >> equals >> '(l o l, )'


    context.testcase = '2 empty slots'
    '(1 ! 2,,)' >> group >> check >> getTupleType >> equals >> TUPLE_2_EMPTY \
        >> check >> bb >> equals >> '(l o l, , )'


    context.testcase = '3 empty slots'
    '(,1 ! 2,,)' >> group >> check >> getTupleType >> equals >> TUPLE_3_EMPTY \
        >> check >> bb >> equals >> '(, l o l, , )'


    context.testcase = '4 plus empty slots'
    '(,,1 ! 2,,)' >> group >> check >> getTupleType >> equals >> TUPLE_4_PLUS_EMPTY \
        >> check >> bb >> equals >> '(, , l o l, , )'


