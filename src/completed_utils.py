import numpy as np


def terminal_state(state, numeric_board, color, stride=5, size=19):
    # for rows and columns
    for i in range(size):
        for j in range(size - stride + 1):
            if np.unique(state[i, j:j + stride]).size == 1 and np.unique(
                state[i, j:j + stride]
            )[
                0
            ] != 0:
                return numeric_board[i, j:j + stride]

            elif np.unique(state[j:j + stride, i]).size == 1 and np.unique(
                state[j:j + stride, i]
            )[
                0
            ] != 0:
                return numeric_board[j:j + stride, i]

    # for diagonals
    for i in range(size - stride + 1):
        for j in range(size - stride + 1):
            if np.unique(
                state[i:i + stride, j:j + stride].diagonal()
            ).size == 1 and np.unique(
                state[i:i + stride, j:j + stride].diagonal()
            )[
                0
            ] != 0:
                return numeric_board[i:i + stride, j:j + stride].diagonal()

            elif np.unique(
                np.fliplr(state)[i:i + stride, j:j + stride].diagonal()
            ).size == 1 and np.unique(
                np.fliplr(state)[i:i + stride, j:j + stride].diagonal()
            )[
                0
            ] != 0:
                return np.fliplr(numeric_board)[i:i + stride, j:j + stride].diagonal()

    return None


def monomial_generator(numeric_board, coordinate, stride=5):
    x, y = coordinate
    monomials = [
        numeric_board[x - stride + 1:x + 1, y],
        numeric_board[x:x + stride, y],
        numeric_board[x, y:y + stride],
        numeric_board[x, y - stride + 1:y + 1],
        numeric_board[x - stride + 1:x + 1, y - stride + 1:y + 1].diagonal(),
        numeric_board[x:x + stride, y:y + stride].diagonal(),
        np.fliplr(numeric_board[x - stride + 1:x + 1, y:y + stride]).diagonal(),
        np.fliplr(numeric_board[x:x + stride, y - stride + 1:y + 1]).diagonal(),
    ]

    return list(
        map(lambda a: a.tolist(), filter(lambda a: len(a) == stride, monomials))
    )
