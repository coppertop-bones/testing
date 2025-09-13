# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import sys


# sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

import types, typing
from coppertop.utils import Missing, assertRaises

MissingType = type(Missing)

class Fred: pass
class Joe: pass
class Sally: pass


def test_Missing():

    assert repr(MissingType) == 'MissingType'
    assert isinstance(MissingType, type)

    # Python special cases None so int | None is considered and optional, see typing.py,
    # but it is somewhat inconsistent, i.e.
    isinstance(None, None | int)                # works
    with assertRaises(TypeError):
        isinstance(None, None)                  # does not work

    # We can't special case Missing so we have had to make it a type
    assert isinstance(Missing, MissingType)
    assert isinstance(Missing, type)

    assert isinstance(1, int | Missing)
    assert isinstance(Missing, int | Missing)
    assert isinstance(Missing, Missing)         # this is also unusual but at least more consistent

    assert Missing is Missing
    assert Missing == Missing
    assert repr(Missing) == 'Missing'
    assert str(Missing) == 'Missing'

    # types.UnionType or typing.Union?
    u1 = int | str | Missing
    u2 = int | Missing | str
    u2b = int | bool | Missing | str
    u3 = Missing | str | int
    u4 = int | str
    u5 = typing.Union[int, str]
    assert u1 == u2 and u2 == u3
    assert u4 == u5

    # here we have rather inconsistent behaviour! UnionType creates a _UnionGenericAlias and types.UnionType | Missing -> types.UnionType
    assert type(u1) is types.UnionType
    assert type(u2) is type(u5)
    assert type(u2b) is types.UnionType
    assert type(u3) is type(u5)
    assert type(u4) is types.UnionType
    assert type(u5) is type(u5)

    assert isinstance(1, u1)
    assert isinstance(1, u2)
    assert isinstance(1, u2b)
    assert isinstance(1, u3)
    assert isinstance(1, u4)
    assert isinstance(1, u5)

    assert isinstance(Missing, u1)
    assert isinstance(Missing, u2)
    assert isinstance(Missing, u2b)
    assert isinstance(Missing, u3)

    assert int | str == typing.Union[int, str]
    assert isinstance(1, str | int)
    assert isinstance(1, str | int | Missing)

    with assertRaises(TypeError):
        assert isinstance([1], list[int])       # unfortunately this is not possible with Python

    with assertRaises(TypeError):
        types.UnionType(str, int)               # raises TypeError: cannot create 'types.UnionType' instances

    assert typing.Union[Fred, typing.Union[Joe, Sally]] == typing.Union[Fred, Joe, Sally]
    assert int | (str | list) == (int | str) | list

    assert typing.get_origin(str | int) is types.UnionType
    assert typing.get_origin(Missing | int) is typing.Union


    # https://stackoverflow.com/questions/45957615/how-to-check-a-variable-against-union-type-during-runtime

    assert isinstance(1, Missing | int)
    assert isinstance(1, int | Missing)

    assert isinstance(1, typing.Union[Missing, int])
    assert isinstance(Missing, typing.Union[Missing, int])

    assert isinstance(Missing, Missing | int)
    assert isinstance(Missing, int | Missing)



def main():
    test_Missing()


if __name__ == '__main__':
    main()
    print('pass')

