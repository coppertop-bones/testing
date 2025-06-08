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


def test_misc():
    k = newKernel()
    group = oldgroup(_, k)
    group_ = oldgroup_(_, k)

    context.testcase = 'check no src works'
    '' >> group >> bb >> check >> equals >> ''


    context.testcase = 'check empty fn / struct throws'
    '{}' >> group_ >> check >> raises >> GroupError


    context.testcase = 'type not closed'
    '<:' >> group_ >> check >> raises >> GroupError


    context.testcase = 'empty parameters'
    '{[] x}' >> group_ >> check >> raises >> GroupError


    context.testcase = 'check keywords with same indent don\'t merge'
    '''
        a ifTrue: 1
        b do: 2
    ''' >> group >> bb >> check >> equals >> 'n (n, l). n (n, l)'


    context.testcase = 'ensure missing elements in tuples are captured - vital for partial syntax'
    '''
        ()
        // ("not a list)
        ( , )
        (,,)
        (;)
        (;;)
        [;,]
    ''' >> group >> bb >> check >> equals >> '(). (, ). (, , ). (; ). (; ; ). [; , ]'


    context.testcase = 'binary can\'t be a struct'
    '{{fred:1}}' >> group_ >> check >> raises >> GroupError


    context.testcase = 'fn returning a struct'
    '{ {fred:x} }' >> group >> bb >> check >> same >> stripSpace >> '{ {fred: n} }'   # OPEN: get function ppGroup should add space here


    context.testcase = 'binary returning a lit'
    '{{1}}' >> group >> bb >> check >> equals >> '{{l}}'


    context.testcase = 'illegal semi-colon in struct / fn'
    '{a ; b}' >> group_ >> check >> raises >> GroupError


    context.testcase = 'illegal comma in fn'
    '{1. , 2.}' >> group_ >> check >> raises >> GroupError


    context.testcase = 'simple optional terminator'
    '''
        a: 1
        b: 2
    ''' >> group >> bb >> check >> equals >> 'l {:a}. l {:b}'


    context.testcase = 'can\'t use <:...> for annotating parameters'
    '{[a <:int>, b <:float>] ^ z <:string>}' >> group_ >> check >> raises >> GroupError


    context.testcase = 'use : for annotating parameters'
    '{[a :int, b: float] ^ z <:string>}' >> group >> bb >> check >> equals >> '{[n:t, n:t] ^ n t}'


    context.testcase = 'handle R_ANGLE'
    '1 <:fred> < > 2 <:fred>' >> group >> bb >> check >> equals >> 'l t o {R_ANGLE} l t'


    context.testcase = 'ex - a switch case'
    '''
        x switch [
            1, [
                a: 1
                b: 2
            ];
            2, ( ,
            );
            3, 
                a: c * d
                a * d;
            ^^ "unhandled case" <:+err>
        ]
    ''' >> group >> bb >> check >> equals >> 'n n [l, [l {:a}. l {:b}]; l, (, ); l, n o n {:a}. n o n; ^^ l t]'


    context.testcase = 'left assign destructure'
    '(a,b): (1,2)' >> group >> bb >> check >> equals >> '(l, l) {:(a, b)}'


    context.testcase = 'right assign destructure'
    '(1,2) :(a,b)' >> group >> bb >> check >> equals >> '(l, l) {:(a, b)}'


    context.testcase = '???'
    '''
        a: (1,2,3; 4,5,6) collect {[x :count+index+offset, y : count, z: count, other:num] x + y}(,1,2,3)
        a collect {x*2} <:matrix> 
    ''' >> group >> bb >> check >> equals >> '(l, l, l; l, l, l) n {[n:t, n:t, n:t, n:t] n o n} (, l, l, l) {:a}. n n {n o l} t'


    context.testcase = "a: a was returning '{a:} (, n)' rather than '{a:} n'"
    'b: a. b: 2. b: 2 + a. a: 2 + 1. a' >> group >> bb >> check >> equals >> 'n {:b}. l {:b}. l o n {:b}. l o l {:a}. n'


    context.testcase = '???'
    '''
        {a: [expr *] -> [expr *]:b}         // post assigning to b is allowed but odd (maybe a warning?)
        a: getInt[] <:float>                // type coercion
        10 <:float> :x  <:int> :y * 2 :z
        fred: {[a:int, b :float] ^ z <:string>}
    ''' >> group >> bb >> check >> equals >> '{a: [n o] o [n o] {:b}}. n [] t {:a}. l t {:x} t {:y} o l {:z}. {[n:t, n:t] ^ n t} {:fred}'


    context.testcase = 'keys, assignment, type tagging, module scope, comments, continuation, blank lines, \n and ;'
    '''
        a: 2 // a comment

        a square \
            <:num> :b * 2 :c. c * 2
        d: c <:num>
    ''' >> group >> bb >> check >> equals >> 'l {:a}. n n t {:b} o l {:c}. n o l. n t {:d}'


    context.testcase = '3D list - 2D list of phrases with new line suggesting expr separation'
    '''
        [
            a: 1
            b: 2 , c:3. d:4 ; 1
            ;
        ]
    ''' >> group >> bb >> check >> equals >> '[l {:a}. l {:b}, l {:c}. l {:d}; l. ; ]'


    context.testcase = 'handle keyword names, descoping, function'
    '''
        a: fred joe
            sally
                ifTrue: [.b]
                ifFalse: {.c}
        1 + 1
    ''' >> group >> bb >> check >> equals >> 'n (n n n, [.n], {.n}) {:a}. l o l'


    context.testcase = 'functions and descoping <:DD2><:DD1>'
    '''
        (1,2,3) do: {[x] (x square * .a) + (x * .b) + .c}    // <:unary> is the default for functions
    ''' >> group >> bb >> check >> equals >> 'n ((l, l, l), {[n:t] (n n o .n) o (n o .n) o .n})'


    context.testcase = 'functions and descoping <:DD2><:DD1>'
    '''
        2 :a + 2 :b +2 :c    // i.e. a: 2; b: 4; c: 6
        b > 2 ifTrue: {
            b: 2   // we have a local b in the local scope here
            (.a * b, .a * .b)
        }
        (1,2,3) do: {[x] (x square * .a) + (x * .b) + .c}    // <:unary> is the default for functions
    ''' >> group >> bb


    context.testcase = '???'
    '''
        x switch[
            1, [a: 1 * c; b: 2 * c],
            2, [
                a: 2 * c
                b: 1 * c
            ],
            3, {
                a = 1
                .a
            }
        ]
    ''' >> group >> bb


    context.testcase = '???'
    '''
        x switch[
            1, [
                a: 1
                b: 2
            ];
            2, {
                a: 2
                b: 1
            };
            "Default val"
        ]
        (1,2,3) fold[seed=0, {[prior, e] prior + e}]
        a ifTrue: {a: false} else: {a: true}
        a ifTrue: [a: false] else: [a: true]
        a ifTrueIfFalse [
            a:true
            ,
            a: false
        ]
        a doThis 
            thenThat[with a arg] 
            thenSomethingElse[...] 
            finishingWith(aHat)
    ''' >> group >> bb


    context.testcase = '???'
    '''
        {fred:1 * 1 + .a}   // is a pointless function so is assumed to be struct
        {fred:1,joe:2}      // is an illegal function so is assumed to be a struct
        <:{age:num}>
        <:{age:num,name:txt}>
    ''' >> group >> bb >> check >> equals >> '{fred: l o l o .n}. {fred: l, joe: l}. t. t'


    context.testcase = '???'
    '''
        {
            b: 2   // we have a local b in the local scope here
            ^ ^^ (.a * b, .a * .b)
        }
    ''' >> group >> bb >> check >> equals >> '{l {:b}. ^ ^^ (.n o n, .n o .n)}'


    context.testcase = 'tuples on their own line'
    '''
        ()
        ("one thing")
    ''' >> group >> bb >> check >> equals >> '(). (l)'



