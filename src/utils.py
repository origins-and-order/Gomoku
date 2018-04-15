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
    # monomials = []
    # for stride in range(1, 6):  # 1-5
    for count in range(1, 6):  # 1-4
        stuff = open_n(state, numeric_board, 5, size, neighboring_monomials, color, count)
        length_temp = len(stuff)
        if length_temp > 0 and length_temp > length:
            length = count
            # break
    return length
