from inference import *

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
