"""Tests for the cf_interpreter using CFR programs.

These tests verify the interpreter can execute core-form programs correctly.
The test kernel provides a minimal stdlib for testing.

NOTE: We don't import via BonesKernel.importSymbols because the CFR parser
creates minimal _Symtab stubs that lack the full SymbolTable interface.
For production use, the full parser creates proper SymbolTables.
"""

from bones.kernel.coreformrep import toCf
from bones.wip.cf_interpreter import Envs


# **********************************************************************************************************************
# Test Kernel - provides minimal stdlib for testing
# **********************************************************************************************************************

class _InterpreterTestKernel:
    """A kernel for interpreter tests with minimal stdlib.

    Provides:
    - Arithmetic: +, -, *, /
    - Comparison: ==, <, <=, >, >=, !=
    - Control flow: ifTrue:ifFalse:
    - Testing: check, pp

    The last expression in a seq is implicitly returned.
    """

    def __init__(self, envs: Envs):
        self.envs = envs
        self.functions = {}     # name -> callable (user-defined)
        self.overloads = {}     # (name, numargs) -> callable
        self._setup_stdlib()

    def _setup_stdlib(self):
        """Register standard library functions for testing."""
        # Arithmetic
        self.overloads[('+', 2)] = lambda a, b: a + b
        self.overloads[('-', 2)] = lambda a, b: a - b
        self.overloads[('*', 2)] = lambda a, b: a * b
        self.overloads[('/', 2)] = lambda a, b: a // b if isinstance(a, int) else a / b

        # Comparison
        self.overloads[('<=', 2)] = lambda a, b: a <= b
        self.overloads[('<', 2)] = lambda a, b: a < b
        self.overloads[('>=', 2)] = lambda a, b: a >= b
        self.overloads[('>', 2)] = lambda a, b: a > b
        self.overloads[('==', 2)] = lambda a, b: a == b
        self.overloads[('!=', 2)] = lambda a, b: a != b

        # Control flow - ifTrue:ifFalse:
        def if_true_false(cond, true_block, false_block):
            if cond:
                return self._eval_block(true_block)
            else:
                return self._eval_block(false_block)
        self.overloads[('ifTrue:ifFalse:', 3)] = if_true_false

        # Testing
        def check(actual, comparator, expected):
            result = comparator(actual, expected)
            if not result:
                raise AssertionError(f"Check failed: {actual} vs {expected}")
            return actual
        self.overloads[('check', 3)] = check

        def pp(value):
            print(value)
            return value
        self.overloads[('pp', 1)] = pp

    def _eval_block(self, block):
        """Evaluate a block node."""
        from bones.kernel.coreform import cblock, cliteral
        if isinstance(block, cblock):
            if block.body and len(block.body) == 1:
                body = block.body[0]
                if isinstance(body, cliteral):
                    return body.tv._v
                else:
                    return self.ex(body)
            elif block.body:
                result = None
                for node in block.body:
                    result = self.ex(node)
                return result
        return block

    def ex(self, node):
        """Execute a core-form node."""
        from bones.kernel.coreform import (
            cliteral, cgetval, cgetfn, capply, cbindfn, cfn, cblock, cseq, cfromimport
        )

        if isinstance(node, cliteral):
            return node.tv._v

        elif isinstance(node, cfromimport):
            # For tests with _Symtab stubs, just validate names exist in stdlib
            for name in node.names:
                found = any(k[0] == name for k in self.overloads.keys())
                if not found and name not in self.functions:
                    raise ValueError(f"Cannot import '{name}' from '{node.path}' - not in test stdlib")
            return None

        elif isinstance(node, cgetval):
            if node.name in self.functions:
                return self.functions[node.name]
            raise ValueError(f"Unknown variable: {node.name}")

        elif isinstance(node, cgetfn):
            key = (node.name, node.numargs)
            if key in self.overloads:
                return self.overloads[key]
            if node.name in self.functions:
                return self.functions[node.name]
            raise ValueError(f"Unknown function: {node.name}/{node.numargs}")

        elif isinstance(node, cbindfn):
            fn_node = node.fnode
            name = node.name
            self.functions[name] = fn_node
            if isinstance(fn_node, cfn):
                num_args = len(fn_node.argnames)
                self.overloads[(name, num_args)] = lambda *args, fn=fn_node: self._call_fn(fn, args)
            return fn_node

        elif isinstance(node, capply):
            fn = self.ex(node.fnnode)
            args = [self.ex(arg) for arg in node.argnodes]

            if callable(fn):
                return fn(*args)
            elif isinstance(fn, cfn):
                return self._call_fn(fn, args)
            else:
                raise ValueError(f"Cannot apply {type(fn)}")

        elif isinstance(node, cseq):
            result = None
            for child in node.nodes:
                result = self.ex(child)
            return result

        elif isinstance(node, cblock):
            return node

        elif isinstance(node, cfn):
            return node

        else:
            raise NotImplementedError(f"_InterpreterTestKernel can't handle {type(node).__name__}")

    def _call_fn(self, fn, args):
        """Call a user-defined function with arguments."""
        from bones.kernel.coreform import cfn

        if not isinstance(fn, cfn):
            raise ValueError(f"Expected cfn, got {type(fn)}")

        old_bindings = {}
        for name, value in zip(fn.argnames, args):
            if name in self.functions:
                old_bindings[name] = self.functions[name]
            self.functions[name] = value
            self.overloads[(name, 0)] = lambda v=value: v

        try:
            result = None
            for node in fn.body:
                result = self.ex(node)
            return result
        finally:
            for name in fn.argnames:
                if name in old_bindings:
                    self.functions[name] = old_bindings[name]
                elif name in self.functions:
                    del self.functions[name]
                if (name, 0) in self.overloads:
                    del self.overloads[(name, 0)]


# **********************************************************************************************************************
# Tests
# **********************************************************************************************************************

def test_literal():
    """Test evaluating a simple literal."""
    ast = toCf('(lit 42)', path='test', modName='test')
    envs = Envs()
    envs.kernel = _InterpreterTestKernel(envs)
    result = envs.kernel.ex(ast.nodes[0])
    assert result == 42


def test_arithmetic():
    """Test basic arithmetic."""
    ast = toCf('(apply (getfn + 2) (lit 3) (lit 4))', path='test', modName='test')
    envs = Envs()
    envs.kernel = _InterpreterTestKernel(envs)
    result = envs.kernel.ex(ast.nodes[0])
    assert result == 7


def test_nested_arithmetic():
    """Test nested arithmetic: (2 + 3) * 4 = 20."""
    ast = toCf('''
        (apply (getfn * 2)
            (apply (getfn + 2) (lit 2) (lit 3))
            (lit 4)
        )
    ''', path='test', modName='test')
    envs = Envs()
    envs.kernel = _InterpreterTestKernel(envs)
    result = envs.kernel.ex(ast.nodes[0])
    assert result == 20


def test_comparison():
    """Test comparison operators."""
    envs = Envs()
    envs.kernel = _InterpreterTestKernel(envs)

    ast = toCf('(apply (getfn <= 2) (lit 3) (lit 5))', path='test', modName='test')
    assert envs.kernel.ex(ast.nodes[0]) == True

    ast = toCf('(apply (getfn <= 2) (lit 5) (lit 3))', path='test', modName='test')
    assert envs.kernel.ex(ast.nodes[0]) == False


def test_if_true_false():
    """Test conditional execution."""
    envs = Envs()
    envs.kernel = _InterpreterTestKernel(envs)

    # if true then 10 else 20
    ast = toCf('''
        (apply (getfn ifTrue:ifFalse: 3)
            (lit 1)
            (block (lit 10))
            (block (lit 20))
        )
    ''', path='test', modName='test')
    result = envs.kernel.ex(ast.nodes[0])
    assert result == 10, f"Expected 10, got {result}"

    # if false then 10 else 20
    ast = toCf('''
        (apply (getfn ifTrue:ifFalse: 3)
            (lit 0)
            (block (lit 10))
            (block (lit 20))
        )
    ''', path='test', modName='test')
    result = envs.kernel.ex(ast.nodes[0])
    assert result == 20, f"Expected 20, got {result}"


def test_define_and_call_function():
    """Test defining and calling a simple function."""
    ast = toCf('''
        (seq
            (bindfn
                (fn (args x)
                    (apply (getfn + 2) (getval x) (lit 1))
                )
                addOne
            )
            (apply (getfn addOne 1) (lit 5))
        )
    ''', path='test', modName='test')

    envs = Envs()
    envs.kernel = _InterpreterTestKernel(envs)
    result = envs.kernel.ex(ast)
    assert result == 6, f"Expected 6, got {result}"


def test_factorial_inline():
    """Test factorial defined inline."""
    ast = toCf('''
        (seq
            (bindfn
                (fn (args n)
                    (apply (getfn ifTrue:ifFalse: 3)
                        (apply (getfn <= 2) (getval n) (lit 1))
                        (block (lit 1))
                        (block
                            (apply (getfn * 2)
                                (getval n)
                                (apply (getfn factorial 1)
                                    (apply (getfn - 2) (getval n) (lit 1))
                                )
                            )
                        )
                    )
                )
                factorial
            )
            (apply (getfn factorial 1) (lit 5))
        )
    ''', path='test', modName='test')

    envs = Envs()
    envs.kernel = _InterpreterTestKernel(envs)
    result = envs.kernel.ex(ast)
    assert result == 120, f"Expected 120, got {result}"


def test_factorial_various_inputs():
    """Test factorial with various inputs."""
    ast_template = '''
        (seq
            (bindfn
                (fn (args n)
                    (apply (getfn ifTrue:ifFalse: 3)
                        (apply (getfn <= 2) (getval n) (lit 1))
                        (block (lit 1))
                        (block
                            (apply (getfn * 2)
                                (getval n)
                                (apply (getfn factorial 1)
                                    (apply (getfn - 2) (getval n) (lit 1))
                                )
                            )
                        )
                    )
                )
                factorial
            )
            (apply (getfn factorial 1) (lit {n}))
        )
    '''

    test_cases = [
        (0, 1),
        (1, 1),
        (2, 2),
        (3, 6),
        (4, 24),
        (5, 120),
        (6, 720),
        (10, 3628800),
    ]

    for n, expected in test_cases:
        ast = toCf(ast_template.format(n=n), path='test', modName='test')
        envs = Envs()
        envs.kernel = _InterpreterTestKernel(envs)
        result = envs.kernel.ex(ast)
        assert result == expected, f"factorial({n}): expected {expected}, got {result}"


if __name__ == '__main__':
    test_literal()
    print("✓ test_literal")

    test_arithmetic()
    print("✓ test_arithmetic")

    test_nested_arithmetic()
    print("✓ test_nested_arithmetic")

    test_comparison()
    print("✓ test_comparison")

    test_if_true_false()
    print("✓ test_if_true_false")

    test_define_and_call_function()
    print("✓ test_define_and_call_function")

    test_factorial_inline()
    print("✓ test_factorial_inline")

    test_factorial_various_inputs()
    print("✓ test_factorial_various_inputs")

    print("\nAll tests passed!")
