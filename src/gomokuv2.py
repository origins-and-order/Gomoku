import numpy as np
from matplotlib import pyplot as plt

from .completed_utils import monomial_generator
from .completed_utils import terminal_state

from .utils import max_monomial_length
from .utils import open_n

from random import choice


class Gomoku:
    """Version 2, uses open player 3 policy."""

    def __init__(self, size=19, monomial_size=5, width=8, height=8):

        # draw the board
        self.__fig = plt.figure(figsize=[width, height])
        self.__fig.patch.set_facecolor((1, 1, .8))
        self.__ax = self.__fig.add_subplot(111)

        for i in range(size):
            self.__ax.plot([i, i], [0, size - 1], "k")
            self.__ax.plot([0, size - 1], [i, i], "k")

        # scale the axis area to fill the whole figure
        self.__ax.set_position([0, 0, 1, 1])

        # get rid of axes and everything (the figure background will show through)
        self.__ax.set_axis_off()

        # scale the plot area conveniently (the board is in 0,0..18,18)
        self.__ax.set_xlim(-1, size)
        self.__ax.set_ylim(-1, size)

        # parameters for the board
        self.__size = size
        self.__monomial_size = monomial_size

        # for keeping track of player moves
        self.__player_moves = {"black": [], "white": []}

        # for keeping track of available moves on the board
        self.__available_moves = np.zeros((size, size), dtype=int)

        # to display board with numeric values 0..size ^ 2 - 1
        self.__numeric_board = np.arange(size ** 2).reshape((size, size))

        # generate monomial bank and scores
        self.__monomial_bank = None
        self.__scores = None

        self.__score_board = {
            "black": np.zeros((size, size), dtype=int),
            "white": np.zeros((size, size), dtype=int),
        }

        # generate table for values associated with all the monomials they belong to
        self.__neighboring_monomial = None
        self.__generate_monomials_and_scores()

        # for number labels
        for number in self.__numeric_board.flatten():
            self.__ax.annotate(
                str(number), np.argwhere(self.__numeric_board == number)[0]
            )

        # computer's first move
        # find max score in self.__score and use that coordinate for first move
        optimal_move = choice(np.argwhere(self.__scores == self.__scores.max()))

        # mark optimal move as taken in available moves and add it to `black` stones move list
        self.render_move(optimal_move, "black")

        # bind method to click
        self.__fig.canvas.mpl_connect("button_press_event", self.__click)

    def __generate_monomials_and_scores(self):
        """
        Generate bank of all monomials based on
        dimensions of board and monomial size.
        :return:
        """

        # prepare containers
        neighbors = {i: [] for i in range(self.__size ** 2)}
        monomials = []
        scores = np.zeros(self.__size ** 2, dtype=int)

        # generate all monomials
        for x in range(self.__size):
            for y in range(self.__size):
                monomials += monomial_generator(self.__numeric_board, (x, y))

        # find all unique monomials
        monomials = set(map(tuple, map(sorted, monomials)))

        # reduce time searching for monomials that contain `number`
        for monomial in monomials:
            for number in monomial:
                scores[number] += 1
                neighbors[number].append(monomial)

        for i in range(self.__size ** 2):
            assert len(neighbors[i]) == scores[i]

        self.__monomial_bank = monomials
        self.__scores = scores.reshape((self.__size, self.__size))
        self.__neighboring_monomial = neighbors

        # release memory
        del monomials, scores, neighbors

    def __click(self, event):
        plot_x = int(round(event.xdata))
        plot_y = int(round(event.ydata))
        if self.__available_moves[plot_x, plot_y] in [1, 2]:
            print("Cannot place piece here.")
        else:
            self.render_move([plot_x, plot_y], "white")
            self.__ai_move()

            # check for terminal states
            state = self.__available_moves
            moves = self.__player_moves

            terminal_black = terminal_state(state, moves, "black")
            terminal_white = terminal_state(state, moves, "white")
            # todo redo terminal state sucks at evaluating
            if terminal_black:
                print("Black is in terminal state.")
            if terminal_white:
                print("White is in terminal state.")

    def make_move(self, color, open_ns):
        assert type(color) == str
        # print(f'length of open_ns {len(open_ns)}')
        # score open ns
        scores = []
        for open__ in open_ns:
            scores.append(sum(self.__score_board[color].flatten()[[open__]]))

        # TODO BREAKS HERE STAHP
        max_score = int(np.argmax(np.array(scores)))

        monomial_n = list(open_ns[max_score])

        # print(f'monomial_n: {monomial_n}')
        # find adjacent piece
        # TODO pick a monomial from the player to block that also benefits the ai
        """for i in range(len(monomial_n)):
            available_move = np.argwhere(self.__numeric_board == monomial_n[i])[0]
            x, y = available_move
            if self.__available_moves[x, y] == 0:
                unavailable_move = np.argwhere(self.__numeric_board == monomial_n[i])[0]
                a, b = unavailable_move"""

        # filter non zeros out
        zeros = np.argwhere(self.__available_moves.flatten()[[monomial_n]] == 0)

        # figure which zero has a greater score
        max_zero = int(zeros[0][0])

        # find max value of opponent board
        for zero in zeros[1:]:
            value_1 = self.__score_board[color].flatten()[monomial_n[zero[0]]]
            value_2 = self.__score_board[color].flatten()[monomial_n[max_zero]]
            if value_1 > value_2:
                max_zero = int(zero)

        # todo get rid of this if statement block, looks like crap
        if type(max_zero) == list:
            max_number = monomial_n[max_zero[0]]
        else:
            max_number = monomial_n[max_zero]

        # render piece
        x, y = np.argwhere(self.__numeric_board == max_number)[0]
        self.render_move([x, y], "black")

    def __ai_move(self):
        """Make a move."""
        state = np.copy(self.__available_moves)
        moves = self.__player_moves
        color = "black"

        monomial_length_black = max_monomial_length(
            self.__size,
            state,
            "black",
            self.__numeric_board,
            self.__neighboring_monomial,
        )
        monomial_length_white = max_monomial_length(
            self.__size,
            state,
            "white",
            self.__numeric_board,
            self.__neighboring_monomial,
        )
        length = monomial_length_black

        # print(f'max open for black is: {monomial_length_black}')
        # print(f'max open for white is: {monomial_length_white}')

        condition_1 = monomial_length_white >= 3

        if condition_1:
            # print('changed to defense')
            color = "white"
            length = monomial_length_white

        color = 1 if color == "black" else 2
        open_ns = open_n(
            state=state,
            numeric_board=self.__numeric_board,
            stride=5,
            size=self.__size,
            neighboring_monomials=self.__neighboring_monomial,
            color=color,
            count=length,
        )
        color = "black" if color == 1 else "white"
        self.make_move(color, open_ns)

        del state, moves

    # TODO merge both update and decrease score

    def update_score(self, coordinate, color, weight=5):
        monomials_to_update = monomial_generator(self.__numeric_board, coordinate)
        a, b = coordinate
        number_coordinate = self.__numeric_board[a, b]
        for monomial in monomials_to_update:
            i = 5
            monomial = sorted(monomial)
            monomial = monomial if monomial[0] == number_coordinate else monomial[::-1]
            for number in monomial:
                x, y = np.argwhere(self.__numeric_board == number)[0]
                self.__score_board[color][
                    x, y
                ] += i * weight ** 2  # todo no idea but this works lmao
                i -= 1

    def decrease_score(self, coordinate, color, weight=5):
        color = "white" if color == "black" else "white"
        a, b = coordinate
        number_coordinate = self.__numeric_board[a, b]
        monomials_to_update = monomial_generator(self.__numeric_board, coordinate)
        for monomial in monomials_to_update:
            i = 1
            monomial = sorted(monomial)
            monomial = monomial if monomial[0] == number_coordinate else monomial[::-1]
            for number in monomial:
                x, y = np.argwhere(self.__numeric_board == number)[0]
                self.__score_board[color][x, y] -= i * weight ** 2
                i += 1

    def render_move(self, coordinate, color):
        x, y = coordinate
        self.update_score(coordinate, color)
        self.decrease_score(coordinate, color)
        self.__available_moves[x, y] = 2 if color == "white" else 1
        self.__player_moves[color].append(coordinate)
        self.__ax.plot(
            *coordinate,
            "o",
            markersize=28,
            markeredgecolor=(0, 0, 0),
            markerfacecolor="green" if color == "black" else "w",
            markeredgewidth=1
        )
        self.__fig.canvas.draw()
