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
