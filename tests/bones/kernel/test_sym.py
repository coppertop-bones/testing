# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from bones.kernel.sym import SymManager


def test():
    symbols = SymManager()
    a = symbols.Sym("sally")
    b = symbols.Sym("joe")
    c = symbols.Sym("fred")
    d = symbols.Sym("arthur")

    assert a._id == 0
    assert b._id == 1
    assert c._id == 2
    assert d._id == 3

    assert not symbols._isSorted
    assert a > b
    assert b > c
    assert c > d
    assert symbols._isSorted

    e = symbols.Sym("sally2")
    f = symbols.Sym("joe2")
    g = symbols.Sym("fred2")
    h = symbols.Sym("arthur2")

    assert not symbols._isSorted
    assert e > a
    assert f > b
    assert g > c
    assert h > d
    assert symbols._isSorted

    a2 = symbols.Sym("sally")
    b2 = symbols.Sym("joe")
    c2 = symbols.Sym("fred")
    d2 = symbols.Sym("arthur")

    assert a2 is a
    assert b2 is b
    assert c2 is c
    assert d2 is d

    assert sorted((a,b,c,d)) == [d,c,b,a]



def main():
    test()


if __name__ == '__main__':
    main()
    print('pass')
