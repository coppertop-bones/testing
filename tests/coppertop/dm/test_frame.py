# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *
from bones.core.sentinels import Missing
from coppertop.dm.testing import check, equals
from coppertop.dm.core.misc import asideDo
from bones.ts.metatypes import BTStruct
from coppertop.dm.core.frame import sortBy, collect, byRow, total_, mean_, first_, last_, count_, by_, take, collect_, by, \
    gather, where, shape
from coppertop.dm.core.types import dframe, count, txt



def test_sortBy():
    context.testcase = 'dframe sorting'
    a = dframe(a=[1,2,1,2,1,2],b=[2,2,2,1,1,1],c=['a','b','c','d','e','f'])
    r = a >> sortBy >> ['b', 'a']


def test_construction():
    context.testcase = 'dframe construction - no type + kwargs'
    dframe(a=[1, 2, 1, 2, 1, 2], b=[2, 2, 2, 1, 1, 1], c=['a', 'b', 'c', 'd', 'e', 'f']) \
        >> asideDo >> (lambda f: f >> typeOf >> check >> equals >> dframe) \
        >> asideDo >> (lambda f: f >> shape >> check >> equals >> (6, 3))

    context.testcase = 'dframe construction - type + kwargs'
    dframe(BTStruct(a=count,b=count, c=txt), a=[1, 2, 1, 2, 1, 2], b=[2, 2, 2, 1, 1, 1], c=['a', 'b', 'c', 'd', 'e', 'f']) \
        >> asideDo >> (lambda f: f >> typeOf >> check >> fitsWithin >> BTStruct(a=count,b=count, c=txt)[dframe]) \
        >> asideDo >> (lambda f: f >> shape >> check >> equals >> (6, 3))

    context.testcase = 'dframe construction - type no data'
    dframe(BTStruct(a=count,b=count, c=txt)) \
        >> asideDo >> (lambda f: f >> typeOf >> check >> fitsWithin >> BTStruct(a=count,b=count, c=txt)[dframe]) \
        >> asideDo >> (lambda f: f >> shape >> check >> equals >> (0, 3))



def test_sql_style():
    context.testcase = 'collect using byRow and whole table'
    f = dframe(a=[1,2,1,2,1,2], b=[2,2,2,1,1,1], c=['a','b','c','d','e','f'])
    f >> collect >> [
        'a',
        'b',
        {'c' : (lambda r: r['a'] + r['b']) >> byRow,
         'd' :  lambda t: [a * b for (a,b) in zip(f['A'] + f['B'])]}
    ] >> check >> equals >> dframe(
        a=[1,2,1,2,1,2],
        b=[2,2,2,1,1,1],
        c=[3,4,3,3,2,3],
        d=[2,4,2,2,1,2]
    )

    context.testcase = 'by & collect, both eager and deferred with gather, and some deferred reducers'
    f >> by >> 'a' >> collect >> ['a', total_('a'), mean_('b'), first_('c'), last_('c'), count_('d')] \
        >> take >> 't1' >> check >> equals >> (f >> by_ >> 'a' >> collect_ >> total_('a') >> gather)


    context.testcase = 'where'
    f >> where >> byRow(lambda r: r['a'] == 1)




def main():
    with context(testcase=Missing):
        test_construction()
        test_sql_style()
        test_sortBy()


if __name__ == '__main__':
    main()
    print('pass')




