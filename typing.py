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
