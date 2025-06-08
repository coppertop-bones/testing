# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *
from coppertop.dm.examples.cluedo.core import *
from coppertop.dm.examples.cluedo.core import one
from coppertop.dm.examples.cluedo.algos import createBag, figureKnown, processResponses, processSuggestions
from coppertop.dm.examples.cluedo.reports import rep1
from coppertop.dm.examples.cluedo.core import cluedo_bag
from coppertop.dm.pp import PP



@coppertop
def PP(bag:cluedo_bag) -> cluedo_bag:
    # this will just print a single line since we've not imported the PP from coppertop.dm.examples.cluedo.core
    bag.pad >> rep1(_, bag.handId) >> PP
    return bag


def test():
    Me = Pl
    events = [

        [Me, Gr, Re, Ba], [Gr, Ba],
        [Gr, Mu, Re, Ki], Or - one,
        [Or, Or, Ro, Lo], Pe - one,
        [Pe, Gr, Da, Co], [Me, Da],

        [Me, Or, Wr, Co], Gr, Or, [Pe, Or],
        [Gr, Sc, Ca, Ki], Or, Pe, [Me, Ca],
        [Or, Pe, Ro, Ba], Pe, Me, Gr - one,
        [Pe, Mu, Re, Co], Me, Gr, Or - one,

        #     [Me, Sc, Wr, Bi], [Gr, Bi],         # Sc, Wr, Co
        #     [Gr, Sc, Le, Ba], Or, Pe, [Me, Le],

        #     [Or, Pe, Re, Co], Pe, Me, Gr,   # won

    ]

    like = {0 :100, 1 :10, 2 :5, 3 :0}
    bag = createBag(Me, [Ki, Di, Le, Da, Ca], {Gr: 5, Or: 4, Pe: 4}) \
          >> figureKnown >> events >> processResponses >> events >> processSuggestions(_, _, like) >> events
    bag >> PP



def main():
    test()


if __name__ == '__main__':
    main()
    print('pass')
