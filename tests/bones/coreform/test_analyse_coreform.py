# **********************************************************************************************************************
# Copyright 2025 David Briant, https://github.com/coppertop-bones. Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License. You may obtain a copy of the  License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY  KIND,
# either express or implied. See the License for the specific language governing permissions and limitations under the
# License. See the NOTICE file distributed with this work for additional information regarding copyright ownership.
# **********************************************************************************************************************

"""
Tests for the analyse_coreform module.

These tests verify that the Analyse phase correctly:
- Walks core-form AST nodes
- Resolves names to the correct symbol table and scope
- Annotates nodes with vmeta/fnmeta
- Creates VMeta/FnMeta entries as needed
"""

import pytest

from coppertop.utils import Missing

from bones.kernel._core import LOCAL_SCOPE, PARENT_SCOPE, MODULE_SCOPE
from bones.kernel.symbol_table import GlobalSymTab, ModSymTab, FnSymTab, VMeta, FnMeta
from bones.kernel.coreform import cseq, cbindval, cgetval, cfn, capply, cgetfamily, cliteral
from bones.kernel.analyse_coreform import (
    analyse_core_form, analyse_node, resolve_value_name, resolve_function_name,
    get_annotation, clear_annotations
)
from bones.lang.types import TBI
from bones.ts.metatypes import BTTuple


class MockKernel:
    """Minimal kernel mock for testing analysis without full kernel setup."""
    def importSymbols(self, path, names, symtab):
        pass


class MockToken:
    """Minimal token mock for creating test nodes."""
    def __init__(self, l1=1, c1=1, l2=1, c2=1):
        self.l1 = l1
        self.c1 = c1
        self.l2 = l2
        self.c2 = c2


def make_symtabs():
    """Create a test symbol table hierarchy: global -> module."""
    globalSt = GlobalSymTab('test_global')
    modSt = ModSymTab('test_module', globalSt)
    return globalSt, modSt


def make_fn_symtab(modSt):
    """Create a function symbol table under the given module."""
    globalSt = modSt.symtabFor(MODULE_SCOPE)._globalSymTab if hasattr(modSt.symtabFor(MODULE_SCOPE), '_globalSymTab') else modSt._globalSymTab
    return FnSymTab('test_fn', globalSt, modSt, modSt)


# **********************************************************************************************************************
# Test: resolve_value_name
# **********************************************************************************************************************

def test_resolve_value_name_local_found():
    """Value defined in local scope should be found."""
    _, modSt = make_symtabs()
    modSt.defVMeta('x', TBI, LOCAL_SCOPE)

    owningSymTab, vmeta, resolvedScope = resolve_value_name('x', modSt, LOCAL_SCOPE)

    assert vmeta is not Missing
    assert isinstance(vmeta, VMeta)
    assert resolvedScope == LOCAL_SCOPE
    assert owningSymTab is modSt


def test_resolve_value_name_local_not_found():
    """Value not defined should return Missing vmeta."""
    _, modSt = make_symtabs()

    owningSymTab, vmeta, resolvedScope = resolve_value_name('x', modSt, LOCAL_SCOPE)

    assert vmeta is Missing


def test_resolve_value_name_module_scope():
    """Explicit MODULE_SCOPE should look in module symtab."""
    _, modSt = make_symtabs()
    fnSt = make_fn_symtab(modSt)
    modSt.defVMeta('moduleVar', TBI, LOCAL_SCOPE)

    owningSymTab, vmeta, resolvedScope = resolve_value_name('moduleVar', fnSt, MODULE_SCOPE)

    assert vmeta is not Missing
    assert resolvedScope == MODULE_SCOPE
    assert owningSymTab is modSt


def test_resolve_value_name_values_dont_inherit():
    """Values should NOT inherit from parent (unlike functions)."""
    _, modSt = make_symtabs()
    fnSt = make_fn_symtab(modSt)
    modSt.defVMeta('moduleVar', TBI, LOCAL_SCOPE)

    # With LOCAL_SCOPE hint (or Missing), should NOT find module var
    owningSymTab, vmeta, resolvedScope = resolve_value_name('moduleVar', fnSt, LOCAL_SCOPE)

    assert vmeta is Missing, "Values should not inherit from module scope with LOCAL_SCOPE hint"


# **********************************************************************************************************************
# Test: resolve_function_name
# **********************************************************************************************************************

def test_resolve_function_name_local_found():
    """Function defined in local scope should be found."""
    _, modSt = make_symtabs()
    modSt.defFnMeta('myFunc', TBI, LOCAL_SCOPE)

    owningSymTab, fnmeta, resolvedScope, family = resolve_function_name('myFunc', modSt, LOCAL_SCOPE)

    assert fnmeta is not Missing
    assert isinstance(fnmeta, FnMeta)
    assert resolvedScope == LOCAL_SCOPE


def test_resolve_function_name_inherits_from_module():
    """Functions should inherit from module scope (unlike values)."""
    _, modSt = make_symtabs()
    fnSt = make_fn_symtab(modSt)
    modSt.defFnMeta('moduleFunc', TBI, LOCAL_SCOPE)

    # With LOCAL_SCOPE hint, should find module function via inheritance
    owningSymTab, fnmeta, resolvedScope, family = resolve_function_name('moduleFunc', fnSt, LOCAL_SCOPE)

    assert fnmeta is not Missing, "Functions should inherit from module scope"


# **********************************************************************************************************************
# Test: analyse_core_form with simple nodes
# **********************************************************************************************************************

def test_analyse_empty_seq():
    """Analysing an empty cseq should not raise."""
    _, modSt = make_symtabs()
    kernel = MockKernel()
    tok = MockToken()

    seq = cseq(tok, tok, modSt, [])

    result = analyse_core_form(seq, modSt, kernel)

    assert result is seq


def test_analyse_cbindval_creates_vmeta():
    """Analysing a cbindval should create a VMeta for the name."""
    clear_annotations()  # Clear any state from previous tests
    _, modSt = make_symtabs()
    kernel = MockKernel()
    tok = MockToken()

    # Create a literal node as the RHS
    from bones.lang.types import litint
    lit = cliteral(tok, modSt, litint(42))

    # Create cbindval: a: 42
    bindNode = cbindval(tok, tok, modSt, lit, LOCAL_SCOPE, 'a', [])
    seq = cseq(tok, tok, modSt, [bindNode])

    # Analyse
    analyse_core_form(seq, modSt, kernel)

    # Check that 'a' now has a VMeta in the module symtab
    assert modSt.hasV('a'), "VMeta for 'a' should be created"
    annotation = get_annotation(bindNode)
    assert annotation is not None, "bindNode should have annotation after analysis"
    assert annotation.vmeta is not Missing, "bindNode annotation should have vmeta"


def test_analyse_cgetval_after_bind():
    """Analysing a cgetval after cbindval should resolve to the same VMeta."""
    clear_annotations()  # Clear any state from previous tests
    _, modSt = make_symtabs()
    kernel = MockKernel()
    tok = MockToken()

    from bones.lang.types import litint
    lit = cliteral(tok, modSt, litint(42))

    bindNode = cbindval(tok, tok, modSt, lit, LOCAL_SCOPE, 'a', [])
    getNode = cgetval(tok, modSt, LOCAL_SCOPE, 'a', [])
    seq = cseq(tok, tok, modSt, [bindNode, getNode])

    analyse_core_form(seq, modSt, kernel)

    bindAnnotation = get_annotation(bindNode)
    getAnnotation = get_annotation(getNode)
    assert bindAnnotation is not None and bindAnnotation.vmeta is not Missing
    assert getAnnotation is not None and getAnnotation.vmeta is not Missing
    # Both should reference the same VMeta
    assert bindAnnotation.vmeta is getAnnotation.vmeta


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
