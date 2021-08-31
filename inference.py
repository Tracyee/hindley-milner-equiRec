from syntax import Identifier, LambdaAbs, Application, LetBinding
from typing import TypeVariable, TypeOperator
from exceptions import InferenceError, ParseError


# function type
Function = TypeOperator("->")
# product type
Product = TypeOperator("*")
# sum type
Sum = TypeOperator("+")


Integer = TypeOperator("int")  # integer
Boolean = TypeOperator("bool")  # bool
Unit = TypeOperator("unit")  # unit type


def infer(expr, env, non_generic=None):
    """
    Four inference rules for four expressions.
    """
    if non_generic is None:
        non_generic = set()

    if isinstance(expr, Identifier):
        return get_type(expr.name, env, non_generic)
    elif isinstance(expr, Application):
        expr1Type = infer(expr.expr1, env, non_generic)
        expr2Type = infer(expr.expr2, env, non_generic)
        appType = Node(TypeVariable())
        unify(Node(Function, expr2Type, appType), expr1Type, non_generic)
        return find(appType)
    elif isinstance(expr, LambdaAbs):
        idType = Node(TypeVariable())
        new_env = env.copy()
        new_env[expr.id] = idType
        new_non_generic = non_generic.copy()
        new_non_generic.add(idType)
        exprType = infer(expr.expr, new_env, new_non_generic)
        return Node(Function, idType, exprType)
    elif isinstance(expr, LetBinding):
        expr1Type = infer(expr.expr1, env, non_generic)
        new_env = env.copy()
        new_env[expr.id] = expr1Type
        return infer(expr.expr2, new_env, non_generic)


# ==============================#
# Node in a type graph
class Node:
    def __init__(self, type=None, left=None, right=None):
        self.type = type  # can be a type variable, a type operator, or a basic type
        self.left = left
        self.right = right
        self.set = None  # to maintain the sets of equivalent nodes, can be a Node pointer or None

    def __eq__(self, other):
        if isinstance(other, Node):
            if self.set is None and other.set is None:
                return self.__hash__() == other.__hash__()
            # the nodes self and other are equal if their representative nodes are in the same equivalence class
            return self.set == other.set

    def __str__(self):
        """If the representative node is not itself, call __str__() recursively."""
        if self.set is None:
            if self.is_basic_type():
                return str(self.type)
            if self.is_variable() or self.is_basic_type():
                return str(self.type)
            else:
                return "({} {} {})".format(
                    str(self.left), str(self.type), str(self.right)
                )
        else:
            return str(self.set)

    def __key(self):
        return (self.type, self.left, self.right)

    def __hash__(self):
        return hash(self.__key())

    def is_variable(self):
        return isinstance(self.type, TypeVariable)

    def is_basic_type(self):
        return (
            self.type.name == "int"
            or self.type.name == "bool"
            or self.type.name == "unit"
        )


def find(n: Node) -> Node:
    """Find with path splitting for better performance"""
    if n.set == None:
        return n
    else:
        n.set = find(n.set)
        return n.set


def union(m: Node, n: Node, non_generic):
    """
    Naive union.
    Note that the union has direction.
    Non-variables and non-generic variables should be the parent in any case.
    """
    mRoot = find(m)
    nRoot = find(n)

    if not mRoot.is_variable() and nRoot.is_variable():
        nRoot.set = mRoot
    elif not nRoot.is_variable() and mRoot.is_variable():
        mRoot.set = nRoot
    elif mRoot.is_variable() and nRoot.is_variable():
        if not is_generic(mRoot, non_generic):
            nRoot.set = mRoot
        else:
            mRoot.set = nRoot
    else:
        mRoot.set = nRoot


def unify(m: Node, n: Node, non_generic) -> bool:
    """
    Unification algorithm.
    Reference: Aho, Alfred V., et al. Compilers: principles, techniques and tools. 2020. pp. 396-398
    """
    s = find(m)
    t = find(n)
    # The representative nodes s and t are equal if m and n are in the same equivalence class
    if s == t:
        return True
    # s or t represents a variable
    elif s.is_variable() or t.is_variable():
        union(s, t, non_generic)
        return True
    elif s.type == t.type:
        # If s and t represent the same basic type
        if s.is_basic_type():
            return True
        else:
            union(s, t, non_generic)
            return unify(s.left, t.left, non_generic) and unify(
                s.right, t.right, non_generic
            )
    else:
        raise InferenceError("Type mismatch: {} != {}".format(str(s), str(t)))


def is_integer_literal(name):
    result = True
    try:
        int(name)
    except ValueError:
        result = False
    return result


def get_type(name, env, non_generic):
    if name in env:
        return freshType(env[name], non_generic)
    elif is_integer_literal(name):
        return Node(Integer)
    else:
        raise ParseError("Undefined symbol {0}".format(name))


def freshType(t, non_generic):
    """
    Copy the given type t.
    Note that only generic types are copied, while non-generic types are shared.
    """
    mappings = {}  # A mapping of TypeVariable nodes to TypeVariables nodes

    def freshrec(tp):
        p = find(tp)
        if p.is_basic_type():
            return p
        elif p.is_variable():
            if is_generic(p, non_generic):
                if p not in mappings:
                    mappings[p] = Node(TypeVariable())
                return mappings[p]
            else:
                return p
        else:
            return Node(p.type, freshrec(p.left), freshrec(p.right))

    return freshrec(t)


def is_generic(v, non_generic):
    return v not in non_generic
