from __future__ import print_function

from syntax import Identifier, LambdaAbs, Application, LetBinding
from typeDefn import TypeVariable, TypeOperator
from exceptions import InferenceError, ParseError
from inference import *
from typingEnv import typingEnv


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
        # fn x => (pair(x(3) (x(true)))
        LambdaAbs(
            "x",
            Application(
                Application(
                    Identifier("pair"), Application(Identifier("x"), Identifier("3"))
                ),
                Application(Identifier("x"), Identifier("true")),
            ),
        ),
        # pair(f(3), f(true))
        Application(
            Application(
                Identifier("pair"), Application(Identifier("f"), Identifier("4"))
            ),
            Application(Identifier("f"), Identifier("true")),
        ),
        # nil: inl unit
        Application(Identifier("inl"), Identifier("unit")),
    ]

    for expression in expressions:
        print(str(expression) + " : ", end=" ")
        try:
            t = infer(expression, typingEnv)
            print(str(t))
        except (ParseError, InferenceError) as e:
            print(e)
    # print(str(expressions[3]) + " : ", end=" ")
    # t = infer(expressions[3], typingEnv)
    # print(str(t))


if __name__ == "__main__":
    main()
