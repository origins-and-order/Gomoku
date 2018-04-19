#
#
#
#
#
#
#
#
import numpy as np


def max_monomial_length(size, state, color, numeric_board, neighboring_monomials):
    """

    :param size:
    :param state:
    :param color:
    :param numeric_board:
    :param neighboring_monomials:
    :return:
    """
    assert type(color) == str
    numeric_color = 1 if color == "black" else 2
    length = 0
    for count in range(1, 5):
        open_monomials = open_n(
            state, numeric_board, 5, size, neighboring_monomials, numeric_color, count
        )
        length_temp = len(open_monomials)
        if length_temp > 0 and count > length:
            length = count
    return length


def monomial_generator(numeric_board, coordinate, stride=5):
    """

    :param numeric_board:
    :param coordinate:
    :param stride:
    :return:
    """
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


def open_n(state, numeric_board, stride, size, neighboring_monomials, color, count=3):
    """

    :param state:
    :param numeric_board:
    :param stride:
    :param size:
    :param neighboring_monomials:
    :param color:
    :param count:
    :return:
    """
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
        if 0 in selection:
        # if 0 in selection and opponent not in selection:
            open_ns.append(filter_monomial)

    # return all unique monomials
    return list(set(map(tuple, map(sorted, map(list, open_ns)))))


def terminal_state(state, size, stride, numeric_board):
    """

    :param state:
    :param size:
    :param stride:
    :param numeric_board:
    :return:
    """
    for i in range(size):
        for j in range(size - stride + 1):

            row = state[i, j:j + stride]
            column = state[j:j + stride, i]

            if np.unique(row).size == 1 and np.unique(row)[0] != 0:
                return numeric_board[i, j:j + stride]
            elif np.unique(column).size == 1 and np.unique(column)[0] != 0:
                return numeric_board[j:j + stride, i]

    for i in range(size - stride + 1):
        for j in range(size - stride + 1):

            top_right = state[i:i + stride, j:j + stride].diagonal()
            top_left = np.fliplr(state)[i:i + stride, j:j + stride].diagonal()

            if np.unique(top_right).size == 1 and np.unique(top_right)[0] != 0:
                return numeric_board[i:i + stride, j:j + stride].diagonal()

            elif np.unique(top_left).size == 1 and np.unique(top_left)[0] != 0:
                return np.fliplr(numeric_board)[i:i + stride, j:j + stride].diagonal()

    return None


