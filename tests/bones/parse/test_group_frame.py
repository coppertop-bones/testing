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


def test_group_frame():
    k = newKernel()
    group = oldgroup(_, k)
    group_ = oldgroup_(_, k)

    '''
        ([]
            s0: (0.95;0.2) <:probs>                 // missing comma
            s1: (0.05;0.8) <:probs>
        )
    ''' >> forcase >> 'frame - missing comma' >> group_ >> check >> raises >> GroupError

    '''
        ([]
            s0: (0.95;0.2) <:probs>,
            s1: (0.05;0.8) <:probs>
        )
    ''' >> forcase >> 'frame' >> group >> bb >> check >> equals >> '([] (l; l) t {:s0}, (l; l) t {:s1})'

    '''
        (
            [G:`gA`gB`gC`gA`gB`gC L:`l0`l0`l0`l1`l1`l1]   // missing comma, should be `gC, L:`l0
            P: (0.10;0.40;0.99;0.90;0.60;0.01)<:probs>
        )
    ''' >> forcase >> 'keyed frame - missing comma' >> group_ >> check >> raises >> GroupError

    '''
        (
            [G:`gA`gB`gC`gA`gB`gC, L:`l0`l0`l0`l1`l1`l1] 
            P: (0.10;0.40;0.99;0.90;0.60;0.01)<:probs>
        )
    ''' >> forcase >> 'example frame no keys' >> group >> bb >> check >> equals >> '([l {:G}, l {:L}] (l; l; l; l; l; l) t {:P})'

    '''
        ([]
            s0: (0.95;0.2) <:probs>,
            s1: (0.05;0.8) <:probs>
        )
    ''' >> forcase >> 'frame' >> group >> bb >> check >> equals >> '([] (l; l) t {:s0}, (l; l) t {:s1})'

    '''
        ([int: `i0`i1]
            s0: (0.95;0.2) <:probs>,
            s1: (0.05;0.8) <:probs>
        )
    ''' >> forcase >> 'keyed frame' >> group >> bb >> check >> equals >> '([l {:int}] (l; l) t {:s0}, (l; l) t {:s1})'


