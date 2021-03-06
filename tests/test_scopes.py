import ast
import textwrap

from flaws.asttools import get_body_ast
from flaws.scopes import fill_scopes


def test_refer():
    @_debug_scope
    def tree():
        x = 1
        def f():
            return x

    assert _dump(tree.scope) == {
        'names': ['f', 'x'],
        'children': [{
            'name': 'FunctionDef f'
        }]
    }


def test_rebind():
    @_debug_scope
    def tree():
        x = 1
        def f():
            x = 2
            return x

    assert _dump(tree.scope) == {
        'names': ['f', 'x'],
        'children': [{
            'name': 'FunctionDef f',
            'names': ['x']
        }]
    }


def test_arg_shadow():
    @_debug_scope
    def tree():
        x = 1
        def f(x):
            return x

    assert _dump(tree.scope) == {
        'names': ['f', 'x'],
        'children': [{
            'name': 'FunctionDef f',
            'names': ['x']
        }]
    }


def test_vararg():
    @_debug_scope
    def tree():
        def f(x, y, *a, **kw):
            return a, kw

    assert _dump(tree.scope) == {
        'names': ['f'],
        'children': [{
            'name': 'FunctionDef f',
            'names': ['a', 'kw', 'x', 'y']
        }]
    }


def test_class():
    @_debug_scope
    def tree():
        class A:
            def f():
                return f

    assert _dump(tree.scope) == {
        'names': ['A'],
        'children': [{
            'name': 'ClassDef A',
            'names': ['f'],
            'children': [{
                'name': 'FunctionDef f',
                'names': ['f']
            }]
        }]
    }


def test_class_assign():
    @_debug_scope
    def tree():
        x = 42

        class A:
            x = x  # Read should refer to outer variable

    assert len(tree.scope.names['x']) == 2


def test_except():
    @_debug_scope
    def tree():
        try:
            pass
        except Exception as e:
            print(e)

    assert len(tree.scope.names['e']) == 2


# Testing utilities

def _debug_scope(func):
    tree = ast.Module(body=get_body_ast(func))
    fill_scopes(tree)
    # Only shown when test fails
    import astpp
    print(astpp.dump(tree))
    print(tree.scope)
    return tree

def _dump(scope):
    res = {}

    if not scope.is_module:
        res['name'] = scope.node.__class__.__name__
        if hasattr(scope.node, 'name'):
            res['name'] += ' ' + scope.node.name
    if scope.names:
        res['names'] = [name for name, _ in sorted(scope.names.items())]
    if scope.children:
        res['children'] = [_dump(c) for c in scope.children]

    return res


