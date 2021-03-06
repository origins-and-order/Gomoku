#
#
#
#
#
#
#
#
import numpy as np

from functools import reduce
from matplotlib.offsetbox import AnnotationBbox
from matplotlib.offsetbox import OffsetImage
from matplotlib import pyplot as plt
from matplotlib import image
from matplotlib import lines as lines

from random import choice

from .utils import max_monomial_length
from .utils import monomial_generator
from .utils import open_n
from .utils import terminal_state


class Gomoku:
    """Version 2, uses open player 3 policy."""

    def __init__(self, size=19, monomial_size=5, width=8, height=8):
        """

        :param size:
        :param monomial_size:
        :param width:
        :param height:
        """

        # draw the board
        plt.rcParams['toolbar'] = 'None'

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

        # determine what move to use
        self.__score_board = {
            "black": np.zeros((size, size), dtype=int),
            "white": np.zeros((size, size), dtype=int),
        }

        # for future move
        self.last_max_size = {
            "black": 0,
            "white": 0
        }

        # for images
        self.stone_images = {
            "black": image.imread('./assets/black_stone.png'),
            "white": image.imread('./assets/white_stone.png'),
            "red": image.imread('./assets/red_stone.png')
        }

        self.stone_image_boxes = {
            "black": OffsetImage(self.stone_images["black"], zoom=.025),
            "white": OffsetImage(self.stone_images["white"], zoom=.025),
            "red": OffsetImage(self.stone_images["red"], zoom=.025),
        }

        # generate table for values associated with all the monomials they belong to
        self.__neighboring_monomial = None
        self.__generate_monomials_and_scores()

        # for number labels
        # for number in self.__numeric_board.flatten():
        #     self.__ax.annotate(
        #         str(number), np.argwhere(self.__numeric_board == number)[0]
        #     )

        # computer's first move
        # find max score in self.__score and use that coordinate for first move
        optimal_move = choice(np.argwhere(self.__scores == self.__scores.max()))

        # mark optimal move as taken in available moves and add it to `black` stones move list
        self.render_move(optimal_move, "black")

        # bind method to click
        self.__fig.canvas.mpl_connect("button_press_event", self.__button_press)

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

    def __button_press(self, event):
        """

        :param event:
        :return:
        """
        plot_x = int(round(event.xdata))
        plot_y = int(round(event.ydata))

        if self.__available_moves[plot_x, plot_y] not in [1, 2]:

            self.render_move([plot_x, plot_y], "white")
            self.__ai_move()

            # check for terminal states
            state = self.__available_moves
            size = self.__size
            stride = self.__monomial_size
            numeric_board = self.__numeric_board

            # check for terminal monomial
            terminal_monomial = terminal_state(state, size, stride, numeric_board)
            if terminal_monomial is not None:
                self.render_terminal_state(terminal_monomial)

                if self.__available_moves.flatten()[terminal_monomial][0] == 1:
                    print('Black is in terminal state.')
                else:
                    print('White is in terminal state.')

    def make_move(self, color, open_ns):
        """

        :param color:
        :param open_ns:
        :return:
        """
        assert type(color) == str
        # unique_cells = list(sorted(set(reduce(lambda a, b: a + b, map(list, open_ns)))))
        # count = {cell: 0 for cell in unique_cells}
        #
        # for open_n in open_ns:
        #     for number in open_n:
        #         count[number] += 1
        # max_count = max(count.values())
        # # print(f'max_count: {max_count}')
        #
        # keys = []
        # for key in count:
        #     if count[key] == max_count:
        #         keys.append(key)
        #         # keys.append({key: count[key]})
        #
        # ai_scores = []
        # player_scores = []
        #
        # for key in keys:
        #     ai_scores.append(self.__score_board["black"].flatten()[key])
        #     player_scores.append(self.__score_board["white"].flatten()[key])
        #
        # print(f'ai_scores: {ai_scores}')
        # print(f'player_scores: {player_scores}')
        #
        # # maximize ai score, minimize player score
        # # minimize player
        # # get max value from player
        # max_player = max(player_scores)
        # max_player_indices = []
        # for index, player_score in enumerate(player_scores):
        #     if player_score == max_player:
        #         max_player_indices.append(index)
        # print(f'max_player_indices: {max_player_indices}')
        # ai_scores = np.array(ai_scores)
        # ai_scores_from_player = ai_scores[max_player_indices]
        # max_ai_score = max(ai_scores_from_player)
        # max_ai_score_indices = np.argwhere(np.array(ai_scores_from_player) == max_ai_score).flatten()
        # max_indices = np.array(np.array(keys)[max_ai_score_indices]).tolist()
        # print(f'max_indices: {max_indices}')
        # print(f'ai_scores_from_player: {ai_scores_from_player}')

        scores = []
        for open__ in open_ns:
            # if len(set(open__).intersection(set(max_indices))) > 0:
            scores.append(np.sum(self.__score_board[color].flatten()[[open__]]))

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
        """

        :return:
        """
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

        # TODO redo this block
        if monomial_length_white >= 2:
            color = "white"
            length = monomial_length_white
        # if self.last_max_size["black"] == 4 and self.last_max_size["white"] <= monomial_length_white:
        #     length = self.last_max_size["black"]
        # elif monomial_length_white >= 3 and monomial_length_black < 4:
        #     color = "white"
        #     length = monomial_length_white

        self.last_max_size["black"] = monomial_length_black
        self.last_max_size["white"] = monomial_length_white

        color_number = 1 if color == "black" else 2
        test_dict1 = dict()
        for i in range(5):
            test_dict1[i+1] = open_n(state, self.__numeric_board, 5, self.__size, self.__neighboring_monomial, 1, i + 1)
        test_dict2 = dict()
        for i in range(5):
            test_dict2[i+1] = open_n(state, self.__numeric_board, 5, self.__size, self.__neighboring_monomial, 2, i + 1)

        print(f'for black')
        for i in range(5):
            print(f'number of open {i+1} monomials: {len(test_dict1[i+1])}')
        print(f'for white')
        for i in range(5):
            print(f'number of open {i+1} monomials: {len(test_dict2[i+1])}')

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

        print(f'for black')
        for i in range(5):
            print(f'number of open {i+1} monomials: {len(test_dict1[i+1])}')
        print(f'for white')
        for i in range(5):
            print(f'number of open {i+1} monomials: {len(test_dict2[i+1])}')


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
        """

        :param coordinate:
        :param color:
        :param weight:
        :return:
        """
        self.__update(coordinate, color, np.add, 5, weight)
        color = "white" if color == "black" else "white"
        self.__update(coordinate, color, np.subtract, 1, weight)

    def render_move(self, coordinate, color):
        """

        :param coordinate:
        :param color:
        :return:
        """
        x, y = coordinate
        self.update_score(coordinate, color)
        self.__available_moves[x, y] = 2 if color == "white" else 1
        self.__player_moves[color].append(coordinate)
        ab = AnnotationBbox(self.stone_image_boxes[color], coordinate, frameon=False)
        self.__ax.add_artist(ab)
        self.__fig.canvas.draw()

    def render_terminal_state(self, monomial):
        """

        :param monomial:
        :return:
        """

        for number in monomial:
            coordinate = np.argwhere(self.__numeric_board == number)[0]
            ab = AnnotationBbox(self.stone_image_boxes["red"], coordinate, frameon=False)
            self.__ax.add_artist(ab)
        self.__fig.canvas.draw()
