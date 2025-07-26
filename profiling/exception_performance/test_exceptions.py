# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

import time

# Here we compare try:except: in Python with rich results. In conclusion, I suggest railway oriented programming is
# intrusive and really needs language support to be effective and that the try:except: is a faster way and more readable
# (since railway tracks don't need laying) way to handle errors in Python. Clearly good taste must prevail, e.g. errors
# should not be handled so far away that the code disconnects the handler from the error but result style should be
# avoided as a rule of thumb. This also reemphasises the benefits of contextual scope.

def dict_at(d, i):
    return d[i]

def dict_try(d, i):
    try:
        return d[i]
    except KeyError:
        return 0

def dict_if(d, i):
    if i in d:
        return d[i]
    else:
        return 0

def dict_get(d, i):
    return d.get(i, 0)

def dict_complex_get(d, i):
    if (res := d.get(i, None)) is None:
        return 0
    else:
        return res

def N_do_fn(N, fn, arg):
    for i in range(N):
        fn(arg, i) + 1

def N_do_tryFn(N, fn, arg):
    for i in range(N):
        try:
            fn(arg, i) + 1
        except KeyError:
            0 + 1


def test_dict_fn():
    N = 10_000

    d = {i: i * 2 for i in range(N)}
    t1 = time.perf_counter()
    N_do_fn(N, dict_try, d)
    try_happy_time = time.perf_counter() - t1

    d = {}
    t1 = time.perf_counter()
    N_do_fn(N, dict_try, d)
    try_unhappy_time = time.perf_counter() - t1

    d = {i: i * 2 for i in range(N)}
    t1 = time.perf_counter()
    N_do_fn(N, dict_get, d)
    get_happy_time = time.perf_counter() - t1

    d = {}
    t1 = time.perf_counter()
    N_do_fn(N, dict_get, d)
    get_unhappy_time = time.perf_counter() - t1

    d = {i: i * 2 for i in range(N)}
    t1 = time.perf_counter()
    N_do_fn(N, dict_complex_get, d)
    complexGet_happy_time = time.perf_counter() - t1

    d = {}
    t1 = time.perf_counter()
    N_do_fn(N, dict_complex_get, d)
    complexGet_unhappy_time = time.perf_counter() - t1

    d = {i: i * 2 for i in range(N)}
    t1 = time.perf_counter()
    N_do_fn(N, dict_if, d)
    if_happy_time = time.perf_counter() - t1

    d = {}
    t1 = time.perf_counter()
    N_do_fn(N, dict_if, d)
    if_unhappy_time = time.perf_counter() - t1

    d = {i: i * 2 for i in range(N)}
    t1 = time.perf_counter()
    N_do_tryFn(N, dict_at, d)
    at_happy_time = time.perf_counter() - t1

    d = {}
    t1 = time.perf_counter()
    N_do_tryFn(N, dict_at, d)
    at_unhappy_time = time.perf_counter() - t1


    # Show results
    print(f"Calling function with handling")
    print(f"At happy:               {at_happy_time * 1000:.2f}ms")
    print(f"At unhappy:             {at_unhappy_time * 1000:.2f}ms")
    print(f"Try happy:              {try_happy_time * 1000:.2f}ms")
    print(f"Try unhappy:            {try_unhappy_time * 1000:.2f}ms")
    print(f"Get happy:              {get_happy_time * 1000:.2f}ms")
    print(f"Get unhappy:            {get_unhappy_time * 1000:.2f}ms")
    print(f"If happy:               {if_happy_time * 1000:.2f}ms")
    print(f"If unhappy:             {if_unhappy_time * 1000:.2f}ms")
    print(f"Complex get happy:      {complexGet_happy_time * 1000:.2f}ms")
    print(f"Complex get unhappy:    {complexGet_unhappy_time * 1000:.2f}ms")
    print()
    print(f"get/try happy:          {get_happy_time / try_happy_time:.2f}x")
    print(f"try/get unhappy:        {try_unhappy_time / get_happy_time:.2f}x")
    print(f"happy/unhappy:          {(if_happy_time / try_happy_time) / (try_unhappy_time / if_unhappy_time):.2f}")
    print()
    print(f"complexGet/try happy:   {complexGet_happy_time / try_happy_time:.2f}x")
    print(f"try/complexGet unhappy: {try_unhappy_time / complexGet_unhappy_time:.2f}x")
    print(f"happy/unhappy:          {(complexGet_happy_time / try_happy_time) / (try_unhappy_time / complexGet_unhappy_time):.2f}")
    print()
    print(f"complexGet/at happy:    {complexGet_happy_time / at_happy_time:.2f}x")
    print(f"at/complexGet unhappy:  {at_unhappy_time / complexGet_unhappy_time:.2f}x")
    print(f"happy/unhappy:          {(complexGet_happy_time / at_happy_time) / (at_unhappy_time / complexGet_unhappy_time):.2f}")
    print()

    # Calling function with handling
    # Try happy:              0.54ms
    # Try unhappy:            1.52ms
    # Get happy:              0.61ms
    # Get unhappy:            0.49ms
    # If happy:               0.71ms
    # If unhappy:             0.46ms
    # Complex get happy:      0.67ms
    # Complex get unhappy:    0.55ms
    #
    # get/try happy:          1.13x
    # try/get unhappy:        2.49x
    # happy/unhappy:          0.39
    #
    # complexGet/try happy:   1.24x
    # try/complexGet unhappy: 2.76x
    # happy/unhappy:          0.45
    #
    # complexGet/at happy:    1.24x
    # at/complexGet unhappy:  0.98x
    # happy/unhappy:          0.32



def test_dict():
    N = 10_000

    def N_dict_try(N, d):
        for i in range(N):
            try:
                _ = d[i]
            except KeyError:
                _ = 0

    def N_dict_if(N, d):
        for i in range(N):
            if i in d:
                _ = d[i]
            else:
                _ = 0

    def N_dict_get(N, d):
        for i in range(N):
            _ = d.get(i, 0)

    def get_add_one(N, d):
        for i in range(N):
            _ = d.get(i, 0) + 1


    d = {i: i * 2 for i in range(N)}
    t1 = time.perf_counter()
    N_dict_try(N, d)
    try_happy_time = time.perf_counter() - t1

    d = {}
    t1 = time.perf_counter()
    N_dict_try(N, d)
    try_unhappy_time = time.perf_counter() - t1

    d = {i: i * 2 for i in range(N)}
    t1 = time.perf_counter()
    N_dict_if(N, d)
    if_happy_time = time.perf_counter() - t1

    d = {}
    t1 = time.perf_counter()
    N_dict_if(N, d)
    if_unhappy_time = time.perf_counter() - t1

    d = {i: i * 2 for i in range(N)}
    t1 = time.perf_counter()
    N_dict_get(N, d)
    get_happy_time = time.perf_counter() - t1

    d = {}
    t1 = time.perf_counter()
    N_dict_get(N, d)
    get_unhappy_time = time.perf_counter() - t1

    d = {i: i * 2 for i in range(N)}
    t1 = time.perf_counter()
    get_add_one(N, d)
    get_add_one_happy_time = time.perf_counter() - t1

    d = {}
    t1 = time.perf_counter()
    get_add_one(N, d)
    get_add_one_unhappy_time = time.perf_counter() - t1


    # Show results
    print(f"Dict accessing directly in code")
    print(f"Try happy:              {try_happy_time * 1000:.2f}ms")
    print(f"Try unhappy:            {try_unhappy_time * 1000:.2f}ms")
    print(f"Get happy:              {get_happy_time * 1000:.2f}ms")
    print(f"Get unhappy:            {get_unhappy_time * 1000:.2f}ms")
    print(f"If happy:               {if_happy_time * 1000:.2f}ms")
    print(f"If unhappy:             {if_unhappy_time * 1000:.2f}ms")
    print(f"Get add one happy:      {get_add_one_happy_time * 1000:.2f}ms")
    print(f"Get add one unhappy:    {get_add_one_unhappy_time * 1000:.2f}ms")
    print()
    print(f"get/try happy:          {get_happy_time / try_happy_time:.2f}x")
    print(f"try/get unhappy:        {try_unhappy_time / get_happy_time:.2f}x")
    print(f"happy/unhappy:          {(if_happy_time / try_happy_time) / (try_unhappy_time / if_unhappy_time):.2f}")
    print()

    # Dict accessing directly in code
    # Try happy:              0.26ms
    # Try unhappy:            1.29ms
    # Get happy:              0.32ms
    # Get unhappy:            0.27ms
    # If happy:               0.42ms
    # If unhappy:             0.22ms
    # Get add one happy:      0.41ms
    # Get add one unhappy:    0.30ms
    #
    # get/try happy:          1.27x
    # try/get unhappy:        3.98x
    # happy/unhappy:          0.28



if __name__ == "__main__":
    test_dict()
    test_dict_fn()
