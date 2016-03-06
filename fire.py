# -*- coding: utf-8 -*-

"""Défi de Clem (nov 2015)

Simulation d'un feu de forêt à l'aide de numpy et pygame.
"""

import numpy as np
import pygame


# ==========
# Variables
# ==========


BURNING_PROB = 0.6
FOREST_SIZE = 300
TREE_SIZE = 2
FRAMERATE = 60


# ======
# Go !!
# ======


pygame.init()

VERDANT = 0
BURNING = 1
ASHES = 2

VERDANT_COLOR = (0, 100, 0)
BURNING_COLOR = (100, 0, 0)
ASHES_COLOR = (0, 0, 0)
BLUE = (0, 0, 100)

my_clock = pygame.time.Clock()

forest = np.zeros((FOREST_SIZE, FOREST_SIZE), np.uint8)

# Conditions aux limites
forest[0, :] = forest[forest.shape[0]-1, :] = ASHES
forest[:, 0] = forest[:, forest.shape[1]-1] = ASHES
useless_ashes_count = np.count_nonzero(forest)

# Conditions initiales
x, y = first_burning = np.random.randint(1, FOREST_SIZE-1, 2)
forest[x, y] = BURNING

burning_trees = [first_burning]

# Affichage initial
screen = pygame.display.set_mode((FOREST_SIZE*TREE_SIZE, FOREST_SIZE*TREE_SIZE))
screen.fill(VERDANT_COLOR)
for x_edge, y_edge in zip(*np.where(forest == ASHES)):
    # Explications : np.where() -> ((x0, x1, ..., xn), (y0, y1, ..., yn)), d'où le "zip étoile"
    pygame.draw.rect(screen, BLUE, pygame.Rect(x_edge*TREE_SIZE, y_edge*TREE_SIZE, TREE_SIZE, TREE_SIZE))
for burning_tree in burning_trees:
    x, y = burning_tree
    pygame.draw.rect(screen, BURNING_COLOR, pygame.Rect(x*TREE_SIZE, y*TREE_SIZE, TREE_SIZE, TREE_SIZE))
pygame.display.flip()

# Boucle principale
while True:
    my_clock.tick(FRAMERATE)

    # RAZ
    burned_trees = []
    burning_neighboors = []

    for burning_tree in burning_trees:
        # Il a brûlé :'(
        x, y = burning_tree
        forest[x, y] = ASHES
        burned_trees.append(burning_tree)

        # Au tour des voisins de peut-être prendre feu
        neighboors = [
            burning_tree + np.array([0, 1]),
            burning_tree + np.array([0, -1]),
            burning_tree + np.array([-1, 0]),
            burning_tree + np.array([1, 0])
        ]
        for neighboor in neighboors:
            x, y = neighboor

            # Brûlera t'y ? Brûlera t'y pas ?
            if forest[x, y] == VERDANT and np.random.random() < BURNING_PROB:
                forest[x, y] = BURNING
                burning_neighboors.append(neighboor)

    burning_trees = burning_neighboors[:]

    # Affichage
    for burned_tree in burned_trees:
        x, y = burned_tree
        pygame.draw.rect(screen, ASHES_COLOR, pygame.Rect(x*TREE_SIZE, y*TREE_SIZE, TREE_SIZE, TREE_SIZE))
    for burning_tree in burning_trees:
        x, y = burning_tree
        pygame.draw.rect(screen, BURNING_COLOR, pygame.Rect(x*TREE_SIZE, y*TREE_SIZE, TREE_SIZE, TREE_SIZE))
    pygame.display.flip()

    # Plus aucun grand brûlé
    if not burned_trees:
        break

# Infos finales
ashes_count = np.count_nonzero(forest) - useless_ashes_count
trees_count = (FOREST_SIZE-2)**2
ashes_ratio = ashes_count / trees_count
print("grands brûlés =", ashes_count)
print("arbres avant incendie =", trees_count)
print("pourcentage de grands brûlés = {:.2%}".format(ashes_ratio))

pygame.time.wait(2000)
pygame.quit()

