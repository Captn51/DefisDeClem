# -*- coding: utf-8 -*-

"""Défi de Clem (oct 2015)

Implémentation d'une calculatrice polonaise.
"""

from sys import exit
from re import fullmatch
from operator import add, sub, mul, truediv


LINE = r"{num} {num} {op}( {num} {op})*".format(num=r"[\+\-]?\d+(.\d+)?", op=r"[\+\-\*\/]")
END_WORD = "BYE"


def read_input():
    """Lit l'entrée utilisateur et renvoie les mots rentrés sous forme de liste.

    "" ou "bye" sont renvoyés tels quels. Dans tous les autres cas, une
    RuntimeError est générée.
    """
    user_line = input("PC ---> ")
    if fullmatch(LINE, user_line):
        return user_line.split()
    elif user_line.strip().upper() in [END_WORD, ""]:
        return user_line.strip().upper()
    else:
        raise RuntimeError("Erreur dans le format de la ligne")


def compute(words):
    """Calcule le résultat de l'opération demandée d'après la liste words.

    words n'est supposée contenir que des nombres convertibles en nombres
    réels ou des opérateurs.
    """
    stack = []
    operation = {"+": add, "-": sub, "*": mul, "/": truediv}

    for w in words:
        if w in operation.keys():
            op1 = stack.pop()
            op2 = stack.pop()
            res = operation[w](op2, op1)
            stack.append(res)
        else:
            stack.append(float(w))

    return stack.pop()


def run():
    """Lance la boucle d'exécution.
    """
    while True:
        try:
            words = read_input()
            if not words:
                continue
            elif words == END_WORD:
                exit()

            res = compute(words)

            print(res)
        except RuntimeError as e:
            print(e)
        except (EOFError, KeyboardInterrupt):
            exit()


if __name__ == "__main__":
    run()

