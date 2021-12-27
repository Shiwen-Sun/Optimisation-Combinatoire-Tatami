from __future__ import annotations

import click
import facile
import matplotlib.pyplot as plt


def tatami_solve(xmax: int, ymax: int) -> list[facile.Solution]:
    """Solves the tatami problem.

    The variables in the solve_all must be passed in order:
    - x coordinates;
    - y coordinates;
    - xs the size of the tatami on the x axis (1: vertical, 2: horizontal);
    - other variables
    """

    if (xmax * ymax) & 1 == 1:
        raise ValueError(f"The room area must be an even number: {xmax * ymax}")
    n = xmax * ymax // 2  # noqa: F841

    # 1. Variables
    # coordonnées en x du point inférieur gauche
    x_1 = [facile.variable(range(0, xmax)) for i in range(n)]
    # coordonnées en y du point inférieur gauche
    y_1 = [facile.variable(range(0, ymax)) for i in range(n)]
    # orientation du tatami : sa dimension selon x
    xs = [facile.variable(range(1, 3)) for i in range(n)]

    # 2. Variables auxiliaires
    # coordonnée en x du coin supérieur droit
    x_2 = [x_1[i] + xs[i] for i in range(n)]
    # coordonnée en y du coin supérieur droit
    y_2 = [y_1[i] + 3 - xs[i] for i in range(n)]

    # 3. Contraintes sur les limites de la pièce
    for i in range(n):
        # le coin supérieur droit n'est pas à droite des limites de la salle
        facile.constraint(x_2[i] <= xmax)
        # le coin supérieur droit n'est pas au dessus des limites de la salle
        facile.constraint(y_2[i] <= ymax)

    # 4. Contraintes du overlapping
    for i in range(n - 1):
        for j in range(i + 1, n):
            # le tatami j est à gauche du tatami i sans superposition
            is_left = x_2[j] <= x_1[i]
            # le tatami j est à droite du tatami i sans superposition
            is_right = x_1[j] >= x_2[i]
            # le tatami j est au-dessus du tatami i sans superposition
            is_above = y_1[j] >= y_2[i]
            # le tatami j est en-dessous du tatami i sans superposition
            is_below = y_2[j] <= y_1[i]
            facile.constraint((is_left | is_right) | (is_above | is_below))

    # 5. Casser la symétrie de permutation
    for i in range(n - 1):
        # on numérote en priorité selon x_1 croissant
        x_smaller = x_1[i] < x_1[i + 1]
        # à x_1 égal, on numérote selon y_1 croissant
        y_smaller = (x_1[i] == x_1[i + 1]) & (y_1[i] < y_1[i + 1])
        # on contraint la solution à être ordonnée de cette façon
        facile.constraint(x_smaller | y_smaller)

    # 6. Empêcher 4 tatamis de partager un sommet
    for i in range(n - 1):
        for j in range(i + 1, n):
            # les deux points ont des coordonnées en x différentes
            x_not_equal = x_2[i] - x_1[j] != 0
            # les deux points ont des coordonnées en y différentes
            y_not_equal = y_2[i] - y_1[j] != 0
            # les deux points ne coïncident pas
            facile.constraint(x_not_equal | y_not_equal)

    # 7. Empêcher la symétrie en cas de pièce carrée
    if xmax == ymax:  # si la pièce est carrée
        # le deuxième tatami est nécessairement au-dessus du premier
        facile.constraint(x_1[0] == x_1[1])

    # On impose la position du premier tatami
    facile.constraint(x_1[0] == 0)
    facile.constraint(y_1[0] == 0)
    # On impose la position du dernier tatami
    facile.constraint(x_2[n - 1] == xmax)
    facile.constraint(y_2[n - 1] == ymax)

    # start with a "simple" solve(), then comment the line when things work
    # return [facile.solve(x_1 + y_1 + xs, backtrack=True)]
    # the evaluation process expects that you return *all* solutions
    return facile.solve_all(x_1 + y_1 + xs, backtrack=True)


@click.command()
@click.argument("xmax", type=int, default=4)
@click.argument("ymax", type=int, default=3)
def main(xmax: int, ymax: int):
    sol = tatami_solve(xmax, ymax)
    for i, solution in enumerate(sol):
        # for solution in sol:
        print(solution)

        if solution.solution is None:
            continue

        n = len(solution.solution) // 3
        x = solution.solution[:n]
        y = solution.solution[n : 2 * n]
        xs = solution.solution[2 * n :]

        fig, ax = plt.subplots()

        for (xi, yi, xsi) in zip(x, y, xs):
            ysi = 3 - xsi
            ax.fill([xi, xi, xi + xsi, xi + xsi], [yi, yi + ysi, yi + ysi, yi])

        ax.set_xlim((0, xmax))
        ax.set_ylim((0, ymax))
        ax.set_aspect(1)
        ax.set_xticks(range(xmax + 1))
        ax.set_yticks(range(ymax + 1))

        # à cacher
        # fig.savefig(f"/mnt/c/Users/ymyca/Desktop/results/output_{i}.png")

        plt.show()


if __name__ == "__main__":
    main()
