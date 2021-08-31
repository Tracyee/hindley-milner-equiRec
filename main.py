from __future__ import print_function


# ==============================#
# Syntax: Expr := Id | lamda Id. Expr | Expr Expr | let Id = Expr in Expr
class Identifier:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name


class LambdaAbs:
    def __init__(self, id: Identifier, expr):
        self.id = id
        self.expr = expr

    def __str__(self):
        return "(fn {} => {})".format(self.id, self.expr)


class Application:
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        return "({} {})".format(self.expr1, self.expr2)


class LetBinding:
    def __init__(self, id: Identifier, expr1, expr2):
        self.id = id
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        return "(let {} = {} in {})".format(self.id, self.expr1, self.expr2)


# ==============================#
# Type variables and type operators
class TypeVariable:

    # class(static) variable that monotonically increases every time this class is instantiated
    uniqueId = 0

    def __init__(self):
        self.id = TypeVariable.uniqueId
        TypeVariable.uniqueId += 1
        self.__name = None

    # class(static) variable that monotonically increases every time a new instance of this class is printed
    uniqueName = "a"

    @property
    def name(self):
        if self.__name is None:
            self.__name = TypeVariable.uniqueName
            TypeVariable.uniqueName = chr(ord(TypeVariable.uniqueName) + 1)
        return self.__name

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self.id)

    def __hash__(self):
        return hash(repr(self))


class TypeOperator:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        # return "({} {} {})".format(str(self.types[0]), self.name, str(self.types[1]))
        return self.name

    def __eq__(self, other):
        if isinstance(other, TypeOperator):
            return self.name == other.name

    def __hash__(self):
        return hash(str(self))


# function type
Function = TypeOperator("->")
# product type
Product = TypeOperator("*")
# sum type
Sum = TypeOperator("+")


# Basic types are constructed with a nullary type constructor
Integer = TypeOperator("int")  # Basic integer
Boolean = TypeOperator("bool")  # Basic bool
Unit = TypeOperator("unit")  # unit type


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
    if n.set == None:
        return n
    else:
        n.set = find(n.set)
        return n.set


def union(m: Node, n: Node, non_generic):
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
        return False


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
    # else:
    #     raise ParseError("Undefined symbol {0}".format(name))


def freshType(t, non_generic):
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


def infer(expr, env, non_generic=None):
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
# Typing environment
var1 = Node(TypeVariable())
var2 = Node(TypeVariable())
var3 = Node(TypeVariable())
var4 = Node(TypeVariable())
var5 = Node(TypeVariable())
var6 = Node(TypeVariable())
var7 = Node(TypeVariable())
var8 = Node(TypeVariable())
var9 = Node(TypeVariable())
var10 = Node(TypeVariable())
var11 = Node(TypeVariable())
var12 = Node(TypeVariable())
var13 = Node(TypeVariable())
var14 = Node(TypeVariable())
var15 = Node(TypeVariable())
var16 = Node(TypeVariable())
var17 = Node(TypeVariable())
typingEnv = {
    "true": Node(Boolean),
    "false": Node(Boolean),
    "pair": Node(
        Function, var1, Node(Function, var2, Node(Product, var1, var2))
    ),  # forall a b. a -> b -> a * b
    "fst": Node(Function, Node(Product, var3, var4), var3),  # forall a b. a * b -> a
    "snd": Node(Function, Node(Product, var5, var6), var6),  # forall a b. a * b -> b
    "inl": Node(Function, var7, Node(Sum, var7, var8)),  # forall a b. b -> a + b
    "inr": Node(Function, var10, Node(Sum, var9, var10)),  # forall a b. a -> a + b
    "match": Node(
        Function,
        Node(Sum, var11, var12),
        Node(
            Function,
            Node(Function, var11, var13),
            Node(Function, Node(Function, var12, var13), var13),
        ),
    ),  # forall a b c. (a + b) -> (a -> c) -> (b -> c) -> c
    "unit": Node(Unit),
    "unitCase": Node(Function, Unit, var14),  #  forall a. 1 -> a
    "fix": Node(
        Function,
        Node(Function, Node(Function, var15, var16), Node(Function, var15, var16)),
        Node(Function, var15, var16),
    ),  # forall a b. ((a -> b) -> a -> b) -> a -> b
    "cond": Node(
        Function, Node(Boolean), Node(Function, var17, Node(Function, var17, var17))
    ),
    "zero": Node(Function, Node(Integer), Node(Boolean)),
    "pred": Node(Function, Node(Integer), Node(Integer)),
    "times": Node(
        Function, Node(Integer), Node(Function, Node(Integer), Node(Integer))
    ),
}


def main():
    expressions = [
        # factorial
        LetBinding(
            "factorial",  # let factorial =
            Application(
                Identifier("fix"),
                LambdaAbs(
                    "self",
                    LambdaAbs(
                        "n",  # fn n =>
                        Application(
                            Application(  # cond (zero n) 1
                                Application(
                                    Identifier("cond"),  # cond (zero n)
                                    Application(Identifier("zero"), Identifier("n")),
                                ),
                                Identifier("1"),
                            ),  # else
                            Application(  # times n
                                Application(Identifier("times"), Identifier("n")),
                                Application(
                                    Identifier("self"),
                                    Application(
                                        Identifier("pred"), Identifier("n")
                                    ),  # n - 1
                                ),
                            ),
                        ),
                    ),
                ),
            ),  # in factorical 5
            Application(Identifier("factorial"), Identifier("5")),
        ),
        # let f = (fn x => x) in ((pair (f 4)) (f true))
        LetBinding(
            "f",
            LambdaAbs("x", Identifier("x")),
            Application(
                Application(
                    Identifier("pair"), Application(Identifier("f"), Identifier("4"))
                ),
                Application(Identifier("f"), Identifier("true")),
            ),
        ),
        # let g = fn f => 5 in g g
        LetBinding(
            "g",
            LambdaAbs("f", Identifier("5")),
            Application(Identifier("g"), Identifier("g")),
        ),
        # example that demonstrates generic and non-generic variables:
        # fn g => let f = fn x => g in pair (f 3, f true)
        LambdaAbs(
            "g",
            LetBinding(
                "f",
                LambdaAbs("x", Identifier("g")),
                Application(
                    Application(
                        Identifier("pair"),
                        Application(Identifier("f"), Identifier("3")),
                    ),
                    Application(Identifier("f"), Identifier("true")),
                ),
            ),
        ),
        # Function composition
        # fn f (fn g (fn arg (f g arg)))
        LambdaAbs(
            "f",
            LambdaAbs(
                "g",
                LambdaAbs(
                    "arg",
                    Application(
                        Identifier("g"), Application(Identifier("f"), Identifier("arg"))
                    ),
                ),
            ),
        ),
    ]

    # for expression in expressions:
    #     print(str(expression) + " : ", end=" ")
    #     t = infer(expression, typingEnv)
    #     print(str(t))
    print(str(expressions[3]) + " : ", end=" ")
    t = infer(expressions[3], typingEnv)
    print(str(t))


if __name__ == "__main__":
    main()
