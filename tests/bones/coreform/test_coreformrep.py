from pathlib import Path
from bones.kernel.coreformrep import toCf, toCfr


def test_parse_ex1_shape():
    test_dir = Path(__file__).parent
    cfr_path = test_dir / 'ex1.cfr'

    with open(cfr_path, 'r', encoding='utf-8') as f:
        ast = toCf(f.read(), path='ex1', modName='ex1')
    assert ast.__class__.__name__ == 'cseq'
    assert len(ast.nodes) == 3

    assert ast.nodes[0].__class__.__name__ == 'cfromimport'
    assert ast.nodes[1].__class__.__name__ == 'cbindfn'
    assert ast.nodes[2].__class__.__name__ == 'capply'


def test_toCfr_literal():
    ast = toCf('(lit 42)', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(lit 42)'


def test_toCfr_do_sequence():
    ast = toCf('(seq (lit 1) (lit 2) (lit 3))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(seq (lit 1) (lit 2) (lit 3))'


def test_toCfr_apply():
    ast = toCf('(apply (getfn + 2) (lit 1) (lit 2))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    # Single expression gets wrapped in cseq by toCf, but toCfr with compact=True
    # elides the do wrapper for single expressions
    assert cfr == '(apply (getfn + 2) (lit 1) (lit 2))'


def test_toCfr_getval():
    ast = toCf('(getval x)', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(getval x)'


def test_toCfr_bindval():
    ast = toCf('(bindval (lit 42) x)', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(bindval (lit 42) x)'


def test_toCfr_fromimport():
    ast = toCf('(fromimport test.utils (+ -))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(fromimport test.utils (+ -))'


def test_toCfr_fn():
    ast = toCf('(fn (args x) (apply (getfn + 2) (getval x) (lit 1)))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert '(fn (args x)' in cfr
    assert '(apply (getfn + 2) (getval x) (lit 1))' in cfr


def test_toCfr_bindfn():
    ast = toCf('(bindfn (fn (args x) (getval x)) myFn)', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert '(bindfn' in cfr
    assert 'myFn' in cfr


def test_toCfr_return():
    ast = toCf('(return (lit 42))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(return (lit 42))'


def test_toCfr_raise():
    ast = toCf('(raise (lit "error"))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(raise (lit "error"))'


def test_toCfr_signal():
    ast = toCf('(signal (lit "warning"))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(signal (lit "warning"))'


def test_toCfr_void():
    ast = toCf('(void)', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(void)'


def test_toCfr_roundtrip():
    """Test that parsing CFR and converting back produces equivalent output."""
    original = '(seq (fromimport test.utils (+ -)) (bindval (lit 42) x) (apply (getfn + 2) (getval x) (lit 1)))'
    ast = toCf(original, path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    # Parse again and convert again - should be stable
    ast2 = toCf(cfr, path='test', modName='test')
    cfr2 = toCfr(ast2, compact=True)
    assert cfr == cfr2


def test_toCfr_pretty_print():
    """Test pretty-printed output has proper indentation."""
    ast = toCf('(seq (lit 1) (lit 2))', path='test', modName='test')
    cfr = toCfr(ast, compact=False)
    assert '\n' in cfr
    assert '    (lit 1)' in cfr
    assert '    (lit 2)' in cfr


# **********************************************************************************************************************
# tuple tests - 1D and 2D
# **********************************************************************************************************************

def test_parse_tuple_1d():
    """Test parsing a 1D tuple."""
    ast = toCf('(tuple (lit 1) (lit 2) (lit 3))', path='test', modName='test')
    assert ast.__class__.__name__ == 'cseq'
    assert len(ast.nodes) == 1
    tupleNode = ast.nodes[0]
    assert tupleNode.__class__.__name__ == 'ctuple'
    assert len(tupleNode.tv) == 3


def test_toCfr_tuple_1d():
    """Test converting 1D tuple to CFR."""
    ast = toCf('(tuple (lit 1) (lit 2) (lit 3))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(tuple (lit 1) (lit 2) (lit 3))'


def test_tuple_1d_roundtrip():
    """Test 1D tuple roundtrip."""
    original = '(tuple (lit 1) (lit 2) (lit 3))'
    ast = toCf(original, path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    ast2 = toCf(cfr, path='test', modName='test')
    cfr2 = toCfr(ast2, compact=True)
    assert cfr == cfr2


def test_parse_tuple_2d():
    """Test parsing a 2D tuple."""
    ast = toCf('(tuple (row (lit 1) (lit 2)) (row (lit 3) (lit 4)))', path='test', modName='test')
    assert ast.__class__.__name__ == 'cseq'
    tupleNode = ast.nodes[0]
    assert tupleNode.__class__.__name__ == 'ctuple'
    assert len(tupleNode.tv) == 2  # 2 rows
    assert len(tupleNode.tv[0]) == 2  # 2 elements per row
    assert len(tupleNode.tv[1]) == 2


def test_toCfr_tuple_2d():
    """Test converting 2D tuple to CFR."""
    ast = toCf('(tuple (row (lit 1) (lit 2)) (row (lit 3) (lit 4)))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert cfr == '(tuple (row (lit 1) (lit 2)) (row (lit 3) (lit 4)))'


def test_tuple_2d_roundtrip():
    """Test 2D tuple roundtrip."""
    original = '(tuple (row (lit 1) (lit 2)) (row (lit 3) (lit 4)))'
    ast = toCf(original, path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    ast2 = toCf(cfr, path='test', modName='test')
    cfr2 = toCfr(ast2, compact=True)
    assert cfr == cfr2


def test_tuple_2d_with_expressions():
    """Test 2D tuple with complex expressions."""
    original = '(tuple (row (getval x) (apply (getfn + 2) (lit 1) (lit 2))) (row (lit 3) (lit 4)))'
    ast = toCf(original, path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert '(getval x)' in cfr
    assert '(apply (getfn + 2) (lit 1) (lit 2))' in cfr


# **********************************************************************************************************************
# block tests - 1D and 2D
# **********************************************************************************************************************

def test_parse_block_1d_no_args():
    """Test parsing a 1D block with no arguments."""
    ast = toCf('(block (lit 42))', path='test', modName='test')
    assert ast.__class__.__name__ == 'cseq'
    blockNode = ast.nodes[0]
    assert blockNode.__class__.__name__ == 'cblock'
    assert len(blockNode.argnames) == 0
    assert len(blockNode.body) == 1


def test_parse_block_1d_with_args():
    """Test parsing a 1D block with arguments."""
    ast = toCf('(block (args x y) (apply (getfn + 2) (getval x) (getval y)))', path='test', modName='test')
    blockNode = ast.nodes[0]
    assert blockNode.__class__.__name__ == 'cblock'
    assert blockNode.argnames == ['x', 'y']


def test_toCfr_block_1d_no_args():
    """Test converting 1D block with no args to CFR."""
    ast = toCf('(block (lit 42))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert '(block (args)' in cfr
    assert '(lit 42)' in cfr


def test_toCfr_block_1d_with_args():
    """Test converting 1D block with args to CFR."""
    ast = toCf('(block (args x y) (apply (getfn + 2) (getval x) (getval y)))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert '(block (args x y)' in cfr
    assert '(apply (getfn + 2) (getval x) (getval y))' in cfr


def test_block_1d_roundtrip():
    """Test 1D block roundtrip."""
    original = '(block (args x) (apply (getfn + 2) (getval x) (lit 1)))'
    ast = toCf(original, path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    ast2 = toCf(cfr, path='test', modName='test')
    cfr2 = toCfr(ast2, compact=True)
    assert cfr == cfr2


def test_parse_block_2d_no_args():
    """Test parsing a 2D block with no arguments."""
    ast = toCf('(block (row (lit 1) (lit 2)) (row (lit 3) (lit 4)))', path='test', modName='test')
    blockNode = ast.nodes[0]
    assert blockNode.__class__.__name__ == 'cblock'
    assert len(blockNode.argnames) == 0
    assert len(blockNode.body) == 2  # 2 rows


def test_parse_block_2d_with_args():
    """Test parsing a 2D block with arguments."""
    ast = toCf('(block (args x) (row (lit 1) (getval x)) (row (lit 2) (getval x)))', path='test', modName='test')
    blockNode = ast.nodes[0]
    assert blockNode.__class__.__name__ == 'cblock'
    assert blockNode.argnames == ['x']
    assert len(blockNode.body) == 2  # 2 rows


def test_toCfr_block_2d():
    """Test converting 2D block to CFR."""
    ast = toCf('(block (row (lit 1) (lit 2)) (row (lit 3) (lit 4)))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert '(block (args)' in cfr
    assert '(row (lit 1) (lit 2))' in cfr
    assert '(row (lit 3) (lit 4))' in cfr


def test_toCfr_block_2d_with_args():
    """Test converting 2D block with args to CFR."""
    ast = toCf('(block (args x) (row (lit 1) (getval x)) (row (lit 2) (getval x)))', path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    assert '(block (args x)' in cfr
    assert '(row (lit 1) (getval x))' in cfr


def test_block_2d_roundtrip():
    """Test 2D block roundtrip."""
    original = '(block (args x) (row (lit 1) (getval x)) (row (lit 2) (getval x)))'
    ast = toCf(original, path='test', modName='test')
    cfr = toCfr(ast, compact=True)
    ast2 = toCf(cfr, path='test', modName='test')
    cfr2 = toCfr(ast2, compact=True)
    assert cfr == cfr2


def test_block_2d_switch_pattern():
    """Test 2D block in switch-like pattern (label, sequence pairs)."""
    # This mimics the pattern from C-AST.txt for switch/goto
    original = '(block (row (lit "fred") (lit "answer is fred")) (row (lit "joe") (lit "answer is joe")))'
    ast = toCf(original, path='test', modName='test')
    blockNode = ast.nodes[0]
    assert len(blockNode.body) == 2
    assert len(blockNode.body[0]) == 2  # each row has 2 elements (pattern, result)
    cfr = toCfr(ast, compact=True)
    assert '(lit "fred")' in cfr
    assert '(lit "answer is fred")' in cfr



"""Quick helper to parse `ex1.cf` into a coreform AST and print a small summary.

Run (from repo root with correct PYTHONPATH):

    python -m bones.interpreter.parse_ex1

"""


def main():
    with open('bones/src/bones/interpreter/ex1.cf', 'r', encoding='utf-8') as f:
        ast = toCf(f.read(), path='ex1', modName='ex1')
    print(ast)
    for n in ast.nodes:
        print(' -', type(n).__name__, n)


if __name__ == '__main__':
    main()
