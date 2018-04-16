import numpy as np

from matplotlib import pyplot as plt
from matplotlib import lines as lines
from random import choice


from .utils import monomial_generator
from .utils import max_monomial_length
from .utils import open_n
from .utils import terminal_state



class Gomoku:
    """Version 2, uses open player 3 policy."""

    def __init__(self, size=19, monomial_size=5, width=8, height=8):

        # draw the board
        self.__fig = plt.figure(figsize=[width, height])
        self.__fig.patch.set_facecolor((1, 1, .8))
        self.__ax = self.__fig.add_subplot(1, 1, 1)

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
        self.__scores = None

        self.__score_board = {
            "black": np.zeros((size, size), dtype=int),
            "white": np.zeros((size, size), dtype=int),
        }

        # hint at future move
        self.last_max_size = {
            "black": 0,
            "white": 0
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

            terminal_black = terminal_state(state, self.__numeric_board, "black")
            terminal_white = terminal_state(state, self.__numeric_board, "white")

            if terminal_white is not None:
                terminal_white = sorted(terminal_white)
                x = np.argwhere(self.__numeric_board == terminal_white[0])[0]
                y = np.argwhere(self.__numeric_board == terminal_white[-1])[0]
                self.render_line(x, y)
            elif terminal_black is not None:
                terminal_black = sorted(terminal_black)
                x = np.argwhere(self.__numeric_board == terminal_black[0])[0]
                y = np.argwhere(self.__numeric_board == terminal_black[-1])[0]
                self.render_line(x, y)

    def make_move(self, color, open_ns):
        """For AI move."""
        assert type(color) == str

        scores = []
        for open__ in open_ns:
            scores.append(np.sum(self.__score_board[color].flatten()[[open__]]))

        # TODO BREAKS HERE STAHP
        max_score = int(np.argmax(np.array(scores)))

        monomial_n = list(open_ns[max_score])

        # filter non zeros out
        zeros = np.argwhere(
            self.__available_moves.flatten()[[monomial_n]] == 0
        ).flatten()

        # convert non zeros to cells on the board
        non_zero_numbers = np.array(monomial_n)[zeros]

        # get the values from the respective score board
        score_board_values = self.__score_board[color].flatten()[non_zero_numbers]

        # get index of max score and get value from `non_zero_numbers` with that index
        max_number = non_zero_numbers[np.argmax(score_board_values)]

        # render piece
        x, y = np.argwhere(self.__numeric_board == max_number)[0]
        self.render_move([x, y], "black")

    def __ai_move(self):
        """Make move based on score boards."""
        state = self.__available_moves
        moves = self.__player_moves
        color = "black"

        monomial_length_black = max_monomial_length(
            size=self.__size,
            state=state,
            color="black",
            numeric_board=self.__numeric_board,
            neighboring_monomials=self.__neighboring_monomial,
        )

        monomial_length_white = max_monomial_length(
            size=self.__size,
            state=state,
            color="white",
            numeric_board=self.__numeric_board,
            neighboring_monomials=self.__neighboring_monomial,
        )

        length = monomial_length_black

        if self.last_max_size["black"] == 4 and self.last_max_size["white"] <= monomial_length_white:
            print('bkfst')
            pass
        elif monomial_length_white >= 3 and monomial_length_black < 4:
            color = "white"
            length = monomial_length_white

        color_number = 1 if color == "black" else 2

        open_ns = open_n(
            state=state,
            numeric_board=self.__numeric_board,
            stride=5,
            size=self.__size,
            neighboring_monomials=self.__neighboring_monomial,
            color=color_number,
            count=length,
        )

        self.make_move(color, open_ns)

        self.last_max_size["black"] = max_monomial_length(
            size=self.__size,
            state=state,
            color="black",
            numeric_board=self.__numeric_board,
            neighboring_monomials=self.__neighboring_monomial,
        )
        self.last_max_size["white"] = max_monomial_length(
            size=self.__size,
            state=state,
            color="white",
            numeric_board=self.__numeric_board,
            neighboring_monomials=self.__neighboring_monomial,
        )

        del state, moves

    def __update(self, coordinate, color, operation, start, weight=5, factor=1):
        """Subroutine to update player's score board."""
        inverted_operation = np.subtract if operation == np.add else np.add
        monomials_to_update = monomial_generator(self.__numeric_board, coordinate)
        a, b = coordinate
        number_coordinate = self.__numeric_board[a, b]
        for monomial in monomials_to_update:
            i = start
            monomial = sorted(monomial)
            monomial = monomial if monomial[0] == number_coordinate else monomial[::-1]
            for number in monomial:
                x, y = np.argwhere(self.__numeric_board == number)[0]
                self.__score_board[color][x, y] = operation(
                    self.__score_board[color][x, y], i * weight ** factor
                )
                i = inverted_operation(i, 1)

    def update_score(self, coordinate, color, weight=5):
        """Update player's score board."""
        self.__update(coordinate, color, np.add, 5, weight, 3)
        color = "white" if color == "black" else "white"
        self.__update(coordinate, color, np.subtract, 1, weight)

    def render_move(self, coordinate, color):
        """Render a players move."""
        x, y = coordinate
        self.update_score(coordinate, color)
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

    def render_line(self, p1, p2):
        """Render a line indicating a terminal state."""
        x = sorted([p1[0], p2[0]])
        y = sorted([p1[1], p2[1]])
        print(f'test: \nx: {x}\ny: {y}')
        self.__ax.add_line(lines.Line2D(x, y))
        self.__fig.canvas.draw()
