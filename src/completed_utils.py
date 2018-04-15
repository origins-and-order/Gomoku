import numpy as np


def all_neighboring_monomials(player_moves, numeric_board, neighboring_monomial, color):
    """
    Finds all monomials that can be played from color.
    Searches through all color's move, then find the number associated
    with the move's coordinate in `self.__numeric_board`
    then find all the monomials that contain the numeric representation
    of move's coordinates.

    :param color:
    :return: monomials that contain move's numeric representation
    """
    assert type(player_moves) == dict
    assert type(neighboring_monomial) == dict
    assert type(numeric_board) == np.ndarray
    assert type(color) == str

    possible_monomials = []
    for move in player_moves[color]:
        x, y = move
        number = int(numeric_board[x, y])
        assert type(number) == int
        possible_monomials += neighboring_monomial[number]
    return possible_monomials


# todo redo
def terminal_state(state, moves, color, stride=5, size=19):
    """
    Check if board is in terminal state.
    Terminal states are: winning or tie.
    :return: boolean True if in terminal state otherwise False
    """
    for move in moves[color]:

        # Unpack coordinates.
        x, y = move

        # Checks for winning state.
        if x + stride < size and y + stride < size:

            # Get row and column.
            row = state[x, y:y + stride]
            column = state[x:x + stride, y]

            # Get diagonals.
            diagonal = state[x:x + stride, y:y + stride]
            right_diagonal = diagonal.diagonal()
            left_diagonal = np.fliplr(diagonal).diagonal()

            # Put selections in a list to iterate over.
            selections = [row, column, right_diagonal, left_diagonal]

            # Check if any selection have 5 of the same elements
            for selection in selections:
                if np.unique(selection).size == 1 and selection[0] != 0:
                    del selections, selection
                    return True

    # check for tie state.
    if sorted(np.unique(state).tolist()) == [1, 2]:
        del moves
        return True

    # return false for non-terminal state.
    del moves
    return False


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


