# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

from coppertop.pipe import *
from coppertop.pipe import CoppertopError
from coppertop.dm.core.text import startsWith, endsWith
from coppertop.dm.utils.testing import assertRaises
from coppertop.dm.testing import check, equals
from bones import jones
from coppertop.dm.pp import NB


def prettyArgs(*args):
    ppArgs = []
    for arg in args:
        if isinstance(arg, (jones._unary, jones._binary, jones._ternary)):
            ppArgs.append(arg.name)
        elif isinstance(arg, (jones._punary, jones._pbinary, jones._pternary)):
            ppArgs.append(f'p{arg.name}{{{arg.o_tbc}}}')
        else:
            ppArgs.append(str(arg))
    return ', '.join(ppArgs)


@coppertop(style=nullary)
def nullary_0():
    return 'nullary_0'

@coppertop(style=nullary)
def nullary_1(a):
    return f'nullary_1({prettyArgs(a)})'

@coppertop(style=nullary)
def nullary_2(a, b):
    return f'nullary_2({prettyArgs(a, b)})'

@coppertop
def unary_1(a):
    return f'unary_1({prettyArgs(a)})'

@coppertop
def unary_2(a, b):
    return f'unary_2({prettyArgs(a, b)})'

@coppertop
def unary_3(a, b, c):
    return f'unary_3({prettyArgs(a, b, c)})'

@coppertop(style=binary)
def binary_2(a, b):
    return f'binary_2({prettyArgs(a, b)})'

@coppertop(style=binary)
def binary_3(a, b, c):
    return f'binary_3({prettyArgs(a, b, c)})'

@coppertop(style=ternary)
def ternary_3(a, b, c):
    return f'ternary_3({prettyArgs(a, b, c)})'



def testNullary():
    str(nullary_1(1)) >> check >> equals >> 'nullary_1(1)'
    # str(nullary_2(1, _)) >> check >> equals >> 'nullary_2(1, TBC{})'
    str(nullary_2(1, _)(2)) >> check >> equals >> 'nullary_2(1, 2)'

    with assertRaises(SyntaxError) as e:
        nullary_1(_)(1, 2)
    e.exceptionValue.args[0] >> check >> endsWith >> 'nullary_1 - %l expected, %l given'

    with assertRaises(SyntaxError) as e:
        2 >> nullary_2(1, _)
    e.exceptionValue.args[0] >> check >> startsWith >> 'Arguments cannot by piped into nullary style fn '


def testUnary():
    str(unary_1(1)) >> check >> equals >> 'unary_1(1)'
    # str(unary_2(1, _)) >> check >> equals >> 'unary_2(1, TBC{})'
    str(2 >> unary_2(1, _)) >> check >> equals >> 'unary_2(1, 2)'

    with assertRaises(SyntaxError) as e:
        unary_1(_)(1, 2)
    e.exceptionValue.args[0] >> check >> startsWith >> 'Wrong number of args to partial fn '

    with assertRaises(SyntaxError) as e:
        2 >> unary_3(1, _, _)
    e.exceptionValue.args[0] >> check >> endsWith >> 'unary_3 that needs a total of 2 more arguments'  # was'Fn "unary_3" is a unary and expects to have 1 args piped but the partial being piped has 2 free. E.g. `[1,2,3] >> take(_, 1)` should be `[1,2,3] >> take >> 1`'

    str(nullary_1(1) >> unary_1) >> check >> equals >> 'unary_1(nullary_1(1))'


def testBinary():
    # in python we can't stop partial binding of binaries as we don't have access to the parser
    str(binary_2(1, 2)) >> check >> equals >> 'binary_2(1, 2)'
    # str(1 >> binary_3(_, 2, _)) >> check >> equals >> 'binary_3(1, 2, TBC{})'
    str(1 >> binary_3(_, 2, _) >> 3) >> check >> equals >> 'binary_3(1, 2, 3)'
    str(1 >> binary_2 >> 2) >> check >> equals >> 'binary_2(1, 2)'
    # str(1 >> binary_2 >> unary_1) >> check >> equals >> 'binary_2(1, unary_1)'


def testTernary():
    # consider the following - it shows that binary, ternary overwrite any function as args r1 or r2
    str([1, 2] >> ternary_3 >> binary_2 >> [3, 4]) >> check >> equals >> 'ternary_3([1, 2], binary_2, [3, 4])'
    str([1, 2] >> ternary_3 >> binary_3(_, 2, _) >> [3, 4]) >> check >> equals >> 'ternary_3([1, 2], pbinary_3{(0, 2)}, [3, 4])'



def main():
    testNullary()
    testUnary()
    testBinary()
    testTernary()
    # testExamples()
    f"{__name__} - tests commented out" >> NB


if __name__ == '__main__':
    main()
    print('pass')


