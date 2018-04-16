import numpy as np


def open_n(state, numeric_board, stride, size, neighboring_monomials, color, count=3):
    assert type(color) == int
    open_monomials = []
    for i in range(size):
        for j in range(size - stride + 1):
            if state[i, j:j + stride].tolist().count(color) >= count:
                open_monomials.append(numeric_board[i, j:j + stride].tolist())
            elif state[j:j + stride, i].tolist().count(color) >= count:
                open_monomials.append(numeric_board[j:j + stride, i].tolist())
    for i in range(size - stride + 1):
        for j in range(size - stride + 1):
            if state[i:i + stride, j:j + stride].diagonal().tolist().count(
                color
            ) >= count:
                open_monomials.append(
                    numeric_board[i:i + stride, j:j + stride].diagonal().tolist()
                )
            elif np.fliplr(state)[i:i + stride, j:j + stride].diagonal().tolist().count(
                color
            ) >= count:
                open_monomials.append(
                    np.fliplr(numeric_board)[
                        i:i + stride, j:j + stride
                    ].diagonal().tolist()
                )
    # find intersection
    possible_monomials = []
    for monomial in open_monomials:
        for number in monomial:
            possible_monomials += neighboring_monomials[number]
    possible_monomials = set(possible_monomials)

    filtered_monomials = []
    for monomial in possible_monomials:
        for open_monomial in open_monomials:
            if len(set(monomial).intersection(set(open_monomial))) >= count:
                filtered_monomials.append(monomial)
    open_ns = []
    for filter_monomial in filtered_monomials:
        selection = state.flatten()[list(filter_monomial)].tolist()
        opponent = 1 if color == 2 else 2
        if 0 in selection and opponent not in selection:
            open_ns.append(filter_monomial)

    return open_ns


def max_monomial_length(size, state, color, numeric_board, neighboring_monomials):
    """Get max open monomial length."""
    assert type(color) == str
    color = 1 if color == "black" else 2
    length = 0
    for count in range(1, 6):
        stuff = open_n(
            state, numeric_board, 5, size, neighboring_monomials, color, count
        )
        length_temp = len(stuff)
        if length_temp > 0 and count > length:
            length = count
    return length


def terminal_state(state, numeric_board, color, stride=5, size=19):
    # for rows and columns
    for i in range(size):
        for j in range(size - stride + 1):

            row = state[i, j:j + stride]
            column = state[j:j + stride, i]

            if np.unique(row).size == 1 and np.unique(row)[0] != 0:
                return numeric_board[i, j:j + stride]
            if np.unique(column).size == 1 and np.unique(column)[0] != 0:
                return numeric_board[j:j + stride, i]

    # for diagonals
    for i in range(size - stride + 1):
        for j in range(size - stride + 1):
            top_right = state[i:i + stride, j:j + stride].diagonal()
            top_left = np.fliplr(state)[i:i + stride, j:j + stride].diagonal()

            if np.unique(top_right).size == 1 and np.unique(top_right)[0] != 0:
                return numeric_board[i:i + stride, j:j + stride].diagonal()

            if np.unique(top_left).size == 1 and np.unique(top_left)[0] != 0:
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
