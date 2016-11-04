# -*- coding: utf-8 -*-

"""Défi de Clem (fev 2016)

Implémentation des chiffrements et déchiffrements de César et de Vigenère.
"""

from sys import exit
from string import ascii_letters, ascii_uppercase
from itertools import cycle, repeat, product
from unicodedata import normalize
from collections import defaultdict
from functools import wraps
from argparse import ArgumentParser
from inspect import signature


def cipher_normalize(text):
    """Nomalise un texte.

    Les caractères français spéciaux (é, î, ç...) sont convertis en caractères non
    spéciaux (e, i, c...) et tout caractère ne correspondant pas à une lettre est
    viré. Le résultat est mis en majuscules.
    """
    # Décomposition du texte : partie un peu floue mais a priori un "é" est codé en
    # unicode (?) comme un "e" + un accent
    text = normalize("NFKD", text)

    # Mtnt que les caractères sont décomposés, on ne garde que les lettres. Du coup, les
    # chiffres, les espaces, la ponctuation, les accents... sont virés
    text = "".join(c for c in text if c in ascii_letters)

    return text.upper()


def check_ascii_parameters(*parameters):
    """Décorateur qui permet de vérifier que, pour la fonction décorée, les paramètres qui
    ont le même nom que des éléments de parameters sont des chaînes ASCII majuscules.
    """
    def decorator(func):
        sig = signature(func)

        @wraps(func)
        def new_func(*args, **kwargs):
            arguments = sig.bind(*args, **kwargs)

            for parameter in parameters:
                # parameter doit être un nom de paramètre valide => pas de try/catch
                for c in arguments.arguments[parameter]:
                    if c not in ascii_uppercase:
                        raise ValueError("{} contient des caractère non lettre ASCII majuscule".format(parameter))

            return func(*args, **kwargs)

        return new_func

    return decorator


@check_ascii_parameters("text")
def caesar_encipher(text, rotation):
    """Chiffre un texte selon le chiffrement de César.

    text est supposé être une string composée uniquement de lettres ASCII majuscules,
    rotation est un entier. cipher_normalize peut être utilisée pour convertir text dans un
    format valide. Renvoie la version chiffrée de text.
    """
    rotation = rotation % 26
    caesar_letters = ascii_uppercase[rotation:] + ascii_uppercase[:rotation]

    return text.translate(str.maketrans(ascii_uppercase, caesar_letters))


@check_ascii_parameters("text")
def caesar_decipher(text):
    """Déchiffre un texte chiffré à l'aide du chiffrement de César.

    text est supposé être une string composée uniquement de lettres ASCII majuscules. Le
    déchiffrement trouve la rotation utilisée pour le chiffrement en considérant que la
    lettre la plus présente dans text correspond à un "E". S'il y a plusieurs lettres les
    plus présentes, les différentes solutions possibles sont renvoyées.
    """
    letter_count = defaultdict(int)    # int() renvoie 0
    for c in text:
        letter_count[c] += 1

    most_used_letters = [letter for letter, count in letter_count.items() if count == max(letter_count.values())]

    results = []

    # On tente les différentes lettres les plus présentes
    for letter in most_used_letters:
        # La rotation utilisée au moment du chiffrement
        rotation = ord(letter) - ord("E")

        # Chiffrement = décalage de rotation, du coup déchiffrement = décalage de -rotation
        possibility = caesar_encipher(text, -rotation)

        results.append(possibility)

    return results


@check_ascii_parameters("text", "key")
def vigenere_encipher(text, key):
    """Chiffre un texte selon le chiffrement de Vigenère.

    text et key sont supposés être des strings composées uniquement de lettres ASCII majuscules.
    """
    return "".join(
        caesar_encipher(c, ord(k) - ord("A"))
        for c, k in zip(text, cycle(key))
    )


@check_ascii_parameters("text")
def vigenere_decipher(text):
    """Déchiffre un texte chiffré à l'aide du chiffrement de Vigenère.

    text est supposé être une string composée uniquement de lettres ASCII majuscules.
    """
    # Séparation en sous textes pour trouver la bonne taille de clé via
    # l'indice de coïncidence
    for step in range(1, len(text) + 1):
        subtexts = [text[start::step] for start in range(step)]

        # Indice de coïncidence
        Ic_sub = []
        for subtext in subtexts:
            # Occurences des lettres (defaultdict ne convient pas, il faut aussi
            # les lettres avec 0 occurence)
            letter_count = dict(zip(ascii_uppercase, repeat(0)))
            for c in subtext:
                letter_count[c] += 1

            Ic_sub.append(
                sum(count * (count - 1) for count in letter_count.values()) / (len(subtext) * (len(subtext) - 1))
            )
        Ic_mean = sum(Ic_sub) / len(Ic_sub)

        if Ic_mean > 0.074:
            # Bonne taille de clé
            break

    # Mtnt qu'on a la taille de la clé, on déchiffre les sous textes via
    # le déchiffrement de César (on ne prend que la première solution)
    sub_deciphered = [caesar_decipher(subtext)[0] for subtext in subtexts]

    # On recolle tous ces sous textes déchiffrés
    try:
        result = ""

        # Cette partie présente des noms de variables peu explicites... Et oui...
        for j, i in product(range(len(sub_deciphered[0])), range(len(sub_deciphered))):
            result += sub_deciphered[i][j]
    except IndexError:
        # Cas où les sous textes ne sont pas tous de la taille de sub_deciphered[0]
        pass

    return result


if __name__ == "__main__":
    parser = ArgumentParser(description="Chiffre ou déchiffre un message.")
    parser.add_argument(
        "message",
        help="message à chiffrer ou à déchiffrer"
    )
    parser.add_argument(
        "-a",
        dest="action",
        choices=["encipher", "decipher"],
        required=True,
        help="action à effectuer (chiffrer ou déchiffrer)"
    )
    parser.add_argument(
        "-m",
        dest="method",
        choices=["caesar", "vigenere"],
        required=True,
        help="méthode à utiliser"
    )
    parser.add_argument(
        "-cr",
        dest="caesar_rotation",
        type=int,
        help="décalage à appliquer pour le chiffrement de César"
    )
    parser.add_argument(
        "-vk",
        dest="vigenere_key",
        help="clé à utiliser pour le chiffrement de Vigenère"
    )
    args = parser.parse_args()

    # Toutes les actions possibles
    compute = {
        "encipher": {"caesar": caesar_encipher, "vigenere": vigenere_encipher},
        "decipher": {"caesar": caesar_decipher, "vigenere": vigenere_decipher},
    }

    cipher_args = []
    cipher_args.append(cipher_normalize(args.message))
    if args.action == "encipher":
        if args.method == "caesar":
            if args.caesar_rotation is not None:
                cipher_args.append(args.caesar_rotation)
            else:
                print("Rotation pour le chiffrement de César non fournie")
                exit()
        elif args.method == "vigenere":
            if args.vigenere_key is not None:
                cipher_args.append(cipher_normalize(args.vigenere_key))
            else:
                print("Clé pour le chiffrement de Vigenère non fournie")
                exit()

    r = compute[args.action][args.method](*cipher_args)

    print(r)

