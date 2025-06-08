# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from bones import jones
from coppertop.dm.utils.testing import assertRaises

# important - in Python even if only one function we have to select in order to type check, so we only need a multi-function and not a dispatcher


class TBC: pass
_ = TBC()


def dispatcher(*args):
    return args


def tests():
    # the purpose here is to collate the arguments - it's the dispatchers job to figure if there is a match


    # fnname, bmod, d, TBCSentinel
    fn = jones._nullary('fn', '', dispatcher, _)
    count = jones._unary('count', '', dispatcher, _)
    add = jones._binary('add', '', dispatcher, _)
    both = jones._ternary('both', '', dispatcher, _)


    # nullary
    with assertRaises(SyntaxError):
        fn >> 1
    with assertRaises(SyntaxError):
        1 >> fn
    assert fn() == ()
    assert fn(1,2) == (1,2)
    assert fn(1,_)(2) == (1,2)
    # assert repr(fn) == '<jones._nullary <root>.fn(...)>'


    # unary
    with assertRaises(SyntaxError):
        count()
    with assertRaises(SyntaxError):
        count >> 1
    assert count(1) == (1, )
    assert count(1, 2) == (1, 2)
    assert 1 >> count == (1, )
    assert 1 >> count(_, 2) == (1, 2)
    assert 2 >> count(1, _) == (1, 2)
    assert count(_, 2)(1) == (1, 2)
    # assert repr(fn) == '<jones._unary <root>.count(...)>'


    # binary
    with assertRaises(SyntaxError):
        add()
    with assertRaises(SyntaxError):
        add(1)
    with assertRaises(SyntaxError):
        add >> 1
    with assertRaises(SyntaxError):
        1 >> add(1, _)
    assert add(1, 2) == (1, 2)
    assert add(1, _)(2) == (1, 2)
    assert 1 >> add >> 2 == (1, 2)
    assert 1 >> add(_, _, 3) >> 2 == (1, 2, 3)
    assert 2 >> add(1, _, _) >> 3 == (1, 2, 3)
    assert 2 >> add(1, _, _, _)(_, 3, _) >> 4 == (1, 2, 3, 4)
    # assert repr(add) == '<jones._binary <root>.add(...)>'


    # ternary
    with assertRaises(SyntaxError):
        both()
    with assertRaises(SyntaxError):
        both(1)
    with assertRaises(SyntaxError):
        both >> 1
    with assertRaises(SyntaxError):
        both(1, _)
    assert [1] >> both >> add >> [2] == ([1], add, [2])
    assert [1] >> both(1,_,_,_) >> add >> [2] == (1, [1], add, [2])


if __name__ == '__main__':
    tests()
    print('pass')
