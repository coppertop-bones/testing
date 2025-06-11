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


def test_group_load():
    k = newKernel()
    group = oldgroup(_, k)
    group_ = oldgroup_(_, k)

    context.testcase = 'load'
    '''
    load 
        dm.core
    ''' >> group >> bb >> check >> equals >> '{L}'
    
    
    context.testcase = 'load #2'
    '''
        load a
        load a
        5
    ''' >> group >> bb >> check >> equals >> '{L}. {L}. l'
    
    
    context.testcase = 'load #3'
    '''
        load a, fred.sally,
          joe,
          arthur. load stuff,
                      nancy,
                    sid
        load a, b. load c, d.e
        5
    ''' >> group >> bb >> check >> equals >> '{L}. {L}. {L}. {L}. l'
    
    
    context.testcase = 'missing name'
    '''
    load
        dm.core,
    fred
    ''' >> group_ >> check >> raises >> GroupError
    
    
    context.testcase = 'nothing specified to load in the phrase'
    'load' >> group_ >> check >> raises >> GroupError
    
    
    context.testcase = 'trailing comma causes the error in load #1'
    '''
        load 
            dm.core,        // the trailing comma causes the error
    ''' >> group_ >> check >> raises >> GroupError
    
    
    context.testcase = 'load #4'
    '''
        from x import y
        difficulty: 1
    ''' >> group >> bb >> check >> equals >> '{FI}. l {:difficulty}'
    
    
    context.testcase = 'trailing comma causes the error in load #2'
    '''
        load 
            my_first_bones.conversions, 
            constants             // constants added to stretch the load parsing
        from my_first_bones.lang import ...       // defines op+, op-, op*, op/, tNum, tStr, fUnary, fBinary in global scope
        from std_bones.bones.stdio import stdout :cout, cerr: stderr
        stdout << "Hello " "world!"
        a: 1
        2 :b + a my_first_bones.conversions.intToStr :c
        stdout << c

        stderr << (1.0 :fred / constants.zero)          // what are we going to do about this?
    ''' >> group >> bb >> check >> equals >> '{L}. {FI}. {FI}. n o l l. l {:a}. l {:b} o n n {:c}. n o n. n o (l {:fred} o n)'
