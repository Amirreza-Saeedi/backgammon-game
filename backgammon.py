import random
import time
import webbrowser
from mttkinter import mtTkinter as tk
from tkinter import font, CENTER, messagebox
from typing import List
import sys
import commands as cmd
from client import send_to_server

# 0 = player 1; 1 = player 2 / PC
turn = 0
dice = []
piece_image = []
list_btn_option = []
stats_label_list = []
global background, game
global dice_image
global image, image1, image2
global label_mini_list
global roll_button

# XXX <
to_be_destroyed = []
main_frame = None
conn = None
my_id = None
server_conn = None
# XXX >

class Game:

    def __init__(self, window, main_frame, player1, player2) -> None:
        """
        This method acts as the class constructor. The main purpose is to initialise and start the game.

        :param window: the window in which we see and play the game, used for displaying widgets
        :param main_frame: the frame attached to the window where we put the widgets
        :param player1: the name of the player that starts the game (always "player 1")
        :param player2: the name of the other player (either "player 2", either "PC")
        """
        self.clicked = []
        self.window = window
        self.main_frame = main_frame
        self.name = [player1, player2]
        self.stats = [[0, 0], [0, 0]]
        self.color = self.color_choosing()
        self.label_list = self.show_player_info(main_frame, self.name, self.color)
        self.show_player_stats(main_frame, self.stats)
        self.board = self.init_board(main_frame)

    @staticmethod
    def show_player_info(main_frame, player, color):
        """
        Here we create labels with the name of the players, prepare labels to show their statuses and display each
        player color.
        The eliminated pieces label keeps track of the pieces 'eaten' by the opponent, while taken out pieces keeps
        track of the pieces that are taken out from the player's house.

        :param main_frame: the frame attached to the window where we put the widgets
        :param player: the list that contains players name, can be either ["player 1", "player 2"], either
        ["player 1", "PC"]
        :param color: list containing the path for the piece color for each player, looks like:
        ["assets/color1.png", "assets/color2.png"]
        :return: None
        """
        label_id = 0
        global label_mini_list
        label_mini_list = []

        text_font = font.Font(size=17)

        label_mini_list.append(tk.Label(main_frame, text=player[0], fg='#80ff80', bg='#655f6a', font=text_font))
        label_mini_list[label_id].place(x=15, y=50)
        label_id += 1

        label_mini_list.append(tk.Label(main_frame, text=player[1], fg='white', bg='#3c353b', font=text_font))
        if player[1] == "player 2":
            label_mini_list[label_id].place(x=1100, y=50)
        else:
            label_mini_list[label_id].place(x=1130, y=50)
        label_id += 1

        text_font = font.Font(size=9)

        label_mini_list.append(
            tk.Label(main_frame, text='#eliminated\npieces', fg='white', bg='#655f6a', font=text_font))
        label_mini_list[label_id].place(x=5, y=300)
        label_id += 1

        label_mini_list.append(
            tk.Label(main_frame, text='#taken out\npieces', fg='white', bg='#655f6a', font=text_font))
        label_mini_list[label_id].place(x=10, y=500)
        label_id += 1

        label_mini_list.append(
            tk.Label(main_frame, text='#eliminated\npieces', fg='white', bg='#3c353b', font=text_font))
        label_mini_list[label_id].place(x=1125, y=300)
        label_id += 1

        label_mini_list.append(
            tk.Label(main_frame, text='#taken out\npieces', fg='white', bg='#3c353b', font=text_font))
        label_mini_list[label_id].place(x=1125, y=500)
        label_id += 1

        global image1
        image1 = tk.PhotoImage(file=color[0])
        label_mini_list.append(tk.Label(main_frame, image=image1, bg=None))
        label_mini_list[label_id].place(x=25, y=700)
        label_id += 1

        global image2
        image2 = tk.PhotoImage(file=color[1])
        label_mini_list.append(tk.Label(main_frame, image=image2, bg=None))
        label_mini_list[label_id].place(x=1110, y=700)
        label_id += 1

        global piece_image
        piece_image = [image1, image2]

        return label_mini_list

    @staticmethod
    def show_player_stats(main_frame, player_stats):
        """
        In this method the statistics about players are updated. If they were not yet shown on the screen, then it is
        done so and if they are already on the screen, when needed this method will destroy the latest label with the
        statistics and create new ones which are added in maine_frame.

        :param main_frame: the frame attached to the window where we put the widgets
        :param player_stats: list where player info is stored; the list looks like:
        [[eliminated_pieces_player1, taken_out_pieces_player1], [eliminated_pieces_player2, taken_out_pieces_player2]]
        :return: None
        """
        global stats_label_list
        stats_label_id = 0

        n = len(stats_label_list)
        if n > 0:
            for label in stats_label_list:
                label.destroy()
            for index in range(0, len(stats_label_list)):
                stats_label_list.pop()

        text_font = font.Font(size=14)

        # for player 1:

        stats_label_list.append(tk.Label(main_frame, text=player_stats[0][0], fg='white', bg='#655f6a',
                                         font=text_font))
        stats_label_list[stats_label_id].place(x=30, y=250)
        stats_label_id += 1

        stats_label_list.append(tk.Label(main_frame, text=player_stats[0][1], fg='white', bg='#655f6a',
                                         font=text_font))
        stats_label_list[stats_label_id].place(x=30, y=450)
        stats_label_id += 1

        # for player 2:

        stats_label_list.append(tk.Label(main_frame, text=player_stats[1][0], fg='white', bg='#3c353b',
                                         font=text_font))
        stats_label_list[stats_label_id].place(x=1150, y=250)
        stats_label_id += 1

        stats_label_list.append(tk.Label(main_frame, text=player_stats[1][1], fg='white', bg='#3c353b',
                                         font=text_font))
        stats_label_list[stats_label_id].place(x=1150, y=450)
        stats_label_id += 1

    @staticmethod
    def color_choosing():
        """
        Here will be generated 2 random colors which represent the color that each player will have for
        the current game.
        Before returning the colors, this method checks to see if the players have different colors.

        :return: a list with the path to the piece image with the corresponding color to those generated
        """
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        while b == a or (a == 1 and b == 2) or (a == 2 and b == 3) or (a == 2 and b == 1) or (a == 3 and b == 2):
            b = random.randint(1, 9)

        if a == 1:
            path_a = "assets/blue.png"
        elif a == 2:
            path_a = "assets/light-blue.png"
        elif a == 3:
            path_a = "assets/grey.png"
        elif a == 4:
            path_a = "assets/black.png"
        elif a == 5:
            path_a = "assets/brown.png"
        elif a == 6:
            path_a = "assets/green.png"
        elif a == 7:
            path_a = "assets/purple.png"
        elif a == 8:
            path_a = "assets/red.png"
        else:
            path_a = "assets/white.png"

        if b == 1:
            path_b = "assets/blue.png"
        elif b == 2:
            path_b = "assets/light-blue.png"
        elif b == 3:
            path_b = "assets/grey.png"
        elif b == 4:
            path_b = "assets/black.png"
        elif b == 5:
            path_b = "assets/brown.png"
        elif b == 6:
            path_b = "assets/green.png"
        elif b == 7:
            path_b = "assets/purple.png"
        elif b == 8:
            path_b = "assets/red.png"
        else:
            path_b = "assets/white.png"

        color_path = [path_a, path_b]
        return color_path

    def init_board_player(self, main_frame, piece, coord_a, coord_b, poz, player_id):
        """
        This method creates a list for a player that contains 24 lists representing data about each column on the table
        for the respective player.
        A column is represented as a list and contains 3 elements: a list with pieces, and 2 coordinates: the x and y.
        The list with pieces contains tk.Button elements which are the pieces on that column.
        The method centers around creating those 24 columns and adding them to the player board.
        After the list was created, the buttons are placed on the screen for the player to see.
        Because this method is called only twice (once for each player), the buttons won't overlay on top of each other.

        :param main_frame: the frame attached to the window where we put the widgets
        :param piece: the path to the piece color for the current player
        :param coord_a: the y coordinates that shows if the player piece is on the upper or lower spots / columns.
        :param coord_b: the y coordinates that shows if the player piece is on the upper or lower spots / columns.
        :param poz: the list that contains spacing between pieces info; it is 65 if the pieces are on the upper spots
        and -65 on the lower spots; this list is needed for the function used to place the pieces on the board
        :param player_id: the id of the player (either 0 or 1), as the elements in a list
        :return: the board with pieces for the current player
        """
        board_player = []
        column = [[], 970, coord_a]
        board_player.append(column)
        column = [[], 900, coord_a]
        board_player.append(column)
        column = [[], 830, coord_a]
        board_player.append(column)
        column = [[], 760, coord_a]
        board_player.append(column)
        column = [[], 690, coord_a]
        board_player.append(column)
        column = [[], 620, coord_a]
        board_player.append(column)
        column = [[], 525, coord_a]
        board_player.append(column)
        column = [[], 455, coord_a]
        board_player.append(column)
        column = [[], 385, coord_a]
        board_player.append(column)
        column = [[], 315, coord_a]
        board_player.append(column)
        column = [[], 245, coord_a]
        board_player.append(column)
        column = [[], 170, coord_a]
        board_player.append(column)
        column = [[], 170, coord_b]
        board_player.append(column)
        column = [[], 245, coord_b]
        board_player.append(column)
        column = [[], 315, coord_b]
        board_player.append(column)
        column = [[], 385, coord_b]
        board_player.append(column)
        column = [[], 455, coord_b]
        board_player.append(column)
        column = [[], 525, coord_b]
        board_player.append(column)
        column = [[], 620, coord_b]
        board_player.append(column)
        column = [[], 690, coord_b]
        board_player.append(column)
        column = [[], 760, coord_b]
        board_player.append(column)
        column = [[], 830, coord_b]
        board_player.append(column)
        column = [[], 900, coord_b]
        board_player.append(column)
        column = [[], 970, coord_b]
        board_player.append(column)

        board_player[5][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 5, 0)))
        board_player[5][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 5, 1)))
        board_player[5][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 5, 2)))
        board_player[5][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 5, 3)))
        board_player[5][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 5, 4)))

        board_player[7][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 7, 0)))
        board_player[7][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 7, 1)))
        board_player[7][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 7, 2)))

        board_player[12][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 12, 0)))
        board_player[12][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 12, 1)))
        board_player[12][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 12, 2)))
        board_player[12][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 12, 3)))
        board_player[12][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 12, 4)))

        board_player[23][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 23, 0)))
        board_player[23][0].append(tk.Button(main_frame, image=piece, command=lambda: self.move(player_id, 23, 1)))

        for i in range(0, len(board_player)):
            for j in range(0, len(board_player[i][0])):
                if i <= 11:
                    board_player[i][0][j].place(x=board_player[i][1], y=(board_player[i][2] + poz[0] * j))
                elif i > 11:
                    board_player[i][0][j].place(x=board_player[i][1], y=(board_player[i][2] + poz[1] * j))

        return board_player

    def init_board(self, main_frame):
        """
        This method calls init_board_player for each player and creates the board list containing most of the game
        information.

        :param main_frame: the frame attached to the window where we put the widgets
        :return: the board represented as a list
        """
        board_1 = self.init_board_player(main_frame, piece_image[0], 15, 730, [65, -65], 0)
        board_2 = self.init_board_player(main_frame, piece_image[1], 730, 15, [-65, 65], 1)

        board = [board_1, board_2]
        return board

    @staticmethod
    def replace_piece(column, id_column, replace_type):
        """
        This method rearranges pies on the column so that they won't overlap with pieces from other player and won't
        go on top of the dices, or the option button or any other widget.

        :param column: the player board
        :param id_column: the column to be rearranged
        :param replace_type: 0 - more than 5 pieces, need to be placed according to a ratio (pieces will overlap but
        aesthetically) or 1 - less than 5 pieces, can stay one after the other
        :return: None
        """
        global turn
        if replace_type == 0:
            if turn == 1:
                poz_id = [-1, 1]
            else:
                poz_id = [1, -1]

            dist = 350 / len(column[0])

            poz_id[0] *= dist
            poz_id[1] *= dist

            for index in range(0, len(column[0])):
                if id_column <= 11:
                    column[0][index].place(x=column[1], y=(column[2] + poz_id[0] * index))
                elif id_column > 11:
                    column[0][index].place(x=column[1], y=(column[2] + poz_id[1] * index))
        elif replace_type == 1:
            if turn == 1:
                poz_id = [-65, 65]
            else:
                poz_id = [65, -65]

            for index in range(0, len(column[0])):
                if id_column <= 11:
                    column[0][index].place(x=column[1], y=(column[2] + poz_id[0] * index))
                elif id_column > 11:
                    column[0][index].place(x=column[1], y=(column[2] + poz_id[1] * index))

    def exist_move(self, player_id):
        """
        Here we check if the player has any move disposable with any of its pieces.
        Two scenarios were taken: with all pieces in the house, and with pieces scattered all over the board.

        :param player_id: the player id as index for board list
        :return: True / False (if the player has any move left)
        """
        if player_id == 1:
            enemy = 0
        else:
            enemy = 1
        count = 0
        if not self.all_in_house(player_id):
            if len(dice) > 0:
                for zar in dice:
                    for index in range(0, 24):
                        if len(self.board[player_id][index][0]) > 0:
                            column = index - zar
                            if 0 <= column < 24 and len(self.board[enemy][23 - column][0]) < 2:
                                count += 1
                                break
                    if count != 0:
                        break
        else:
            if len(dice) > 0:
                for zar in dice:
                    if len(self.board[player_id][zar - 1][0]) > 0:
                        count += 1
                    else:
                        count_null = 0
                        for i in range(zar - 1, 6):
                            if len(self.board[player_id][i][0]) == 0:
                                count_null += 1
                        if count_null == 7 - zar:
                            count += 1
                    for index in range(0, 24):
                        if len(self.board[player_id][index][0]) > 0:
                            column = index - zar
                            if 0 <= column < 24 and len(self.board[enemy][23 - column][0]) < 2:
                                count += 1
                                break

        if count == 0:
            return False
        else:
            return True

    def all_in_house(self, player_id):
        """
        This method checks if the pieces of a player are all in his house.

        :param player_id: the player id as it is in the board list (0 - player 1; 1 - player 2 / PC)
        :return: True / False (answer if the pieces of a player are all in his house)
        """
        count = 0
        if self.stats[player_id][0] == 0:
            for column in range(6, 24):
                count += len(self.board[player_id][column][0])
        if count == 0:
            return True
        else:
            return False

    def end_piece_life(self, player_id, x, y):
        """
        This method is the same as 'piece_next_place' but for the case when the piece can be removed because the player
        has all it's pieces inside the house.
        Besides what 'piece_next_place' does, this method will insert in the list position for the pieces that can be
        taken out like [-5, 0], where -5 is a code that indicates that the piece will be taken out and 0 means that it
        will not be replaced on the board.

        :param player_id: the player id as index for board list
        :param x: column id based on which player turn it is
        :param y: coordinates to know if the column is on top or on bottom of the game board
        :return: list containing next position possible for one piece based on the dice rolled
        """
        next_pos = []
        if player_id == 0:
            if len(dice) == 2:
                for index in range(0, len(dice)):
                    column = x - dice[index]
                    if column < 12:
                        coord_y = 15
                    else:
                        coord_y = 730

                    coord = 23 - column
                    if 0 <= coord <= 23:
                        if len(self.board[1][coord][0]) < 2 and column >= 0:
                            next_pos.append([column, coord_y])
                    elif column < 0:
                        verify_last_column = 1
                        if column == -1:
                            next_pos.append([-5, 0])
                        else:
                            for i in range(0, 6):
                                if len(self.board[player_id][i][0]) > 0:
                                    dist = i - dice[index]
                                    if 0 > dist > column:
                                        verify_last_column = 0
                                    elif dist >= 0:
                                        verify_last_column = 0

                            if verify_last_column == 1:
                                next_pos.append([-5, 0])
            else:
                column = x - dice[0]
                if column < 12:
                    coord_y = 15
                else:
                    coord_y = 730

                coord = 23 - column
                if 0 <= coord <= 23:
                    if len(self.board[1][coord][0]) < 2 and column >= 0:
                        next_pos.append([column, coord_y])
                elif column < 0:
                    verify_last_column = 1
                    if column == -1:
                        next_pos.append([-5, 0])
                    else:
                        for i in range(0, 6):
                            if len(self.board[player_id][i][0]) > 0:
                                dist = i - dice[0]
                                if 0 > dist > column:
                                    verify_last_column = 0
                                elif dist >= 0:
                                    verify_last_column = 0

                        if verify_last_column == 1:
                            next_pos.append([-5, 0])
        else:
            if len(dice) == 2:
                for index in range(0, len(dice)):
                    column = x - dice[index]
                    if column < 12:
                        coord_y = 730
                    else:
                        coord_y = 15

                    coord = 23 - column
                    if 0 <= coord <= 23:
                        if len(self.board[0][coord][0]) < 2 and column >= 0:
                            next_pos.append([column, coord_y])
                    elif column < 0:
                        verify_last_column = 1
                        if column == -1:
                            next_pos.append([-5, 0])
                        else:
                            for i in range(0, 6):
                                if len(self.board[player_id][i][0]) > 0:
                                    dist = i - dice[index]
                                    if 0 > dist > column:
                                        verify_last_column = 0
                                    elif dist >= 0:
                                        verify_last_column = 0

                            if verify_last_column == 1:
                                next_pos.append([-5, 0])

            else:
                column = x - dice[0]
                if column < 12:
                    coord_y = 730
                else:
                    coord_y = 15

                coord = 23 - column
                if 0 <= coord <= 23:
                    if len(self.board[0][coord][0]) < 2 and column >= 0:
                        next_pos.append([column, coord_y])
                elif column < 0:
                    verify_last_column = 1
                    if column == -1:
                        next_pos.append([-5, 0])
                    else:
                        for i in range(0, 6):
                            if len(self.board[player_id][i][0]) > 0:
                                dist = i - dice[0]
                                if 0 > dist > column:
                                    verify_last_column = 0
                                elif dist >= 0:
                                    verify_last_column = 0

                        if verify_last_column == 1:
                            next_pos.append([-5, 0])

        if len(next_pos) == 0 and y > 0 and self.name[player_id] != "PC":
            messagebox.showerror("Backgammon!!", "You don't have where to move this piece")

        return next_pos

    def piece_next_place(self, player_id, x, y):
        """
        This method starts with an empty list that will end up being populated by the next position where the piece
        selected can be moved to.
        Basically this method will calculate where a piece should be moved with all dice values available
        and then check if the column is available. If it is, the the coordinates are then inserted into the list.

        :param player_id: the player id as index for board list
        :param x: column id based on which player turn it is
        :param y: coordinates to know if the column is on top or on bottom of the game board
        :return: list containing next position possible for one piece based on the dice rolled
        """
        next_pos = []
        if player_id == 0:
            if len(dice) == 2:
                for index in range(0, len(dice)):
                    column = x - dice[index]
                    if column < 12:
                        coord_y = 15
                    else:
                        coord_y = 730

                    coord = 23 - column
                    if 0 <= coord <= 23:
                        if len(self.board[1][coord][0]) < 2 and column >= 0:
                            next_pos.append([column, coord_y])

            else:
                column = x - dice[0]
                if column < 12:
                    coord_y = 15
                else:
                    coord_y = 730

                coord = 23 - column
                if 0 <= coord <= 23:
                    if len(self.board[1][coord][0]) < 2 and column >= 0:
                        next_pos.append([column, coord_y])

        else:
            if len(dice) == 2:
                for index in range(0, len(dice)):
                    column = x - dice[index]
                    if column < 12:
                        coord_y = 730
                    else:
                        coord_y = 15

                    coord = 23 - column
                    if 0 <= coord <= 23:
                        if len(self.board[0][coord][0]) < 2 and column >= 0:
                            next_pos.append([column, coord_y])

            else:
                column = x - dice[0]
                if column < 12:
                    coord_y = 730
                else:
                    coord_y = 15

                coord = 23 - column
                if 0 <= coord <= 23:
                    if len(self.board[0][coord][0]) < 2 and column >= 0:
                        next_pos.append([column, coord_y])

        if len(next_pos) == 0 and y > 0 and self.name[player_id] != "PC":
            messagebox.showerror("Backgammon!!", "You don't have where to move this piece")

        return next_pos

    def update_board(self, player_id, column_taken, column_pus):  
        
        # XXX <
        global turn
        global conn, my_id
        # move and send
        if my_id == turn:
            send_to_p2p(f'{cmd.MOVE} {player_id} {column_taken} {column_pus}')
        # XXX >

        """
        Based on the player that moved, first will be set the enemy and a poz_id list that helps with placing the
        buttons for the pieces on the board.

        First it is checked if the piece was moved from a column to another (such that the piece was not taken out).
        The piece is then destroyed and placed somewhere else on the board and in the board list.
        Based on how many pieces are already on that column the call for rearranging the pieces will be done in 2 ways
        (more info in 'replace_piece' method). This applies for both columns (the one that was taken from and the one
        to which the piece was moved).
        If the player has all pieces in house, then the piece will only be destroyed and the dice value removed.

        In the end it is checked if the column on which the piece was put had any of the enemy's pieces. In this case
        the enemy piece will get 'eaten', destroyed and the statistics updated.

        :param player_id: the player id as index for board list
        :param column_taken: the column from which a piece was taken
        :param column_pus: the column to which a piece was moved
        :return: None
        """
        if player_id == 1:
            enemy = 0
            poz_id = [-65, 65]
        else:
            enemy = 1
            poz_id = [65, -65]

        if column_taken != -5:
            self.board[player_id][column_taken][0][-1].destroy()
            self.board[player_id][column_taken][0].pop()
            if len(self.board[player_id][column_taken][0]) > 5:
                self.replace_piece(self.board[player_id][column_taken], column_taken, 0)
            else:
                self.replace_piece(self.board[player_id][column_taken], column_taken, 1)

            poz = len(self.board[player_id][column_pus][0]) + 1
            self.board[player_id][column_pus][0].append(tk.Button(self.main_frame, image=piece_image[player_id],
                                                                  command=lambda: self.move(player_id, column_pus,
                                                                                            poz)))

            if column_pus <= 11:
                self.board[player_id][column_pus][0][-1].place(x=self.board[player_id][column_pus][1],
                                                               y=(self.board[player_id][column_pus][2] + poz_id[0] * (
                                                                       len(self.board[player_id][column_pus][0]) - 1)))
                if len(self.board[player_id][column_pus][0]) > 5:
                    self.replace_piece(self.board[player_id][column_pus], column_pus, 0)
                else:
                    self.replace_piece(self.board[player_id][column_pus], column_pus, 1)
            elif column_pus > 11:
                self.board[player_id][column_pus][0][-1].place(x=self.board[player_id][column_pus][1],
                                                               y=(self.board[player_id][column_pus][2] + poz_id[1] * (
                                                                       len(self.board[player_id][column_pus][0]) - 1)))
                if len(self.board[player_id][column_pus][0]) > 5:
                    self.replace_piece(self.board[player_id][column_pus], column_pus, 0)
                else:
                    self.replace_piece(self.board[player_id][column_pus], column_pus, 1)

            column_enemy = 23 - column_pus

        else:

            poz = len(self.board[player_id][23 - column_pus][0]) + 1
            self.board[player_id][23 - column_pus][0].append(tk.Button(self.main_frame, image=piece_image[player_id],
                                                                       command=lambda: self.move(player_id,
                                                                                                 23 - column_pus, poz)))

            if column_pus <= 11:
                self.board[player_id][23 - column_pus][0][-1].place(x=self.board[player_id][23 - column_pus][1],
                                                                    y=(self.board[player_id][23 - column_pus][2] +
                                                                       poz_id[
                                                                           0] * (-1) * (
                                                                               len(self.board[player_id][
                                                                                       23 - column_pus][
                                                                                       0]) - 1)))
                if len(self.board[player_id][23 - column_pus][0]) > 5:
                    self.replace_piece(self.board[player_id][23 - column_pus], 23 - column_pus, 0)
                else:
                    self.replace_piece(self.board[player_id][23 - column_pus], 23 - column_pus, 1)

            column_enemy = column_pus

        if 0 <= column_enemy <= 23 and len(self.board[enemy][column_enemy][0]) == 1:
            self.board[enemy][column_enemy][0][-1].destroy()
            self.board[enemy][column_enemy][0].pop()
            self.stats[enemy][0] += 1
            self.show_player_stats(self.main_frame, self.stats)

    def move_piece(self, player_id, column, taken):
        """
        This method will move the pieces around. First the option buttons will be removed from the board and destroyed
        so the board is kept clean. Then the board is updated using the 'update_board' method.

        Then it is searched for the dice value that lead up to this move and once it is found, it will be deleted from
        the dice list.

        In the end the game prepares itself for the turn of the next player.

        :param player_id: the player id as index for board list
        :param column: the column where the piece will be moved
        :param taken: the column from which the piece was taken
        :return: None
        """
        global list_btn_option
        for btn in list_btn_option:
            btn.destroy()
        list_btn_option = []

        self.update_board(player_id, taken, column)

        if taken != -5:
            val_zar = taken - column
            dice.remove(val_zar)
        else:
            val_zar = column + 1
            dice.remove(val_zar)
            self.stats[player_id][0] -= 1
            self.show_player_stats(self.main_frame, self.stats)
            if self.stats[player_id][0] > 0 and len(dice) > 0:
                self.revive(player_id)

        global turn
        if len(dice) == 0:

            if turn == 0:
                # turn = 1
                self.set_turn(1)
                # label_mini_list[0].config(fg="white")
                # label_mini_list[1].config(fg="#80ff80")
            else:
                # turn = 0
                self.set_turn(0)
                # label_mini_list[1].config(fg="white")
                # label_mini_list[0].config(fg="#80ff80")
            
            roll_button.config(state="normal")

    def options(self, player_id, x, y):
        """
        Ths method takes the options where one can move a selected piece and shows them which they are.
        First it is checked if the player has clicked on another piece before without moving it. If he done so then he
        will receive an information box that the piece previously selected will be deselected.

        If there are any moves possible then: it is checked if the pieces are all in house or not.
        If the pieces are not all in house then buttons over some columns will pop up indicating the column on which
        the selected piece can be moved to. If the pieces are all in house, besides showing where they can be moved
        further, there is a chance for a button "Take out" to pop up. This button will appear on the bottom of the side
        of the respective player.

        Then the scene is prepared for the next player's turn.

        :param player_id: the player id as index for board list
        :param x: column id based on which player turn it is
        :param y: coordinates to know if the column is on top or on bottom of the game board
        :return: None
        """
        global list_btn_option, turn, dice
        if len(list_btn_option) > 0:
            messagebox.showinfo("Backgammon!!", "The piece selected previously will be deselected")
            for btn in list_btn_option:
                btn.destroy()
            list_btn_option = []

        if self.exist_move(player_id):
            if len(dice) > 0:
                if not self.all_in_house(player_id):
                    next_pos = self.piece_next_place(player_id, x, y)
                    for i in range(0, len(next_pos)):
                        if next_pos[i][1] == 15:
                            list_btn_option.append(tk.Button(self.main_frame, text=" ^ "))
                            list_btn_option[i].place(x=(17 + self.board[player_id][next_pos[i][0]][1]), y=350)
                        else:
                            list_btn_option.append(tk.Button(self.main_frame, text=" v "))
                            list_btn_option[i].place(x=(17 + self.board[player_id][next_pos[i][0]][1]), y=430)

                    if len(list_btn_option) > 0:
                        list_btn_option[0].config(command=lambda: self.move_piece(player_id, next_pos[0][0], x))
                        if len(list_btn_option) == 2:
                            list_btn_option[1].config(command=lambda: self.move_piece(player_id, next_pos[1][0], x))
                else:
                    next_pos = self.end_piece_life(player_id, x, y)
                    if self.exist_move(player_id):
                        if len(dice) > 0:
                            for i in range(0, len(next_pos)):
                                if next_pos[i][1] == 15:
                                    list_btn_option.append(tk.Button(self.main_frame, text=" ^ "))
                                    list_btn_option[i].place(x=(17 + self.board[player_id][next_pos[i][0]][1]), y=350)
                                elif next_pos[i][1] == 730:
                                    list_btn_option.append(tk.Button(self.main_frame, text=" v "))
                                    list_btn_option[i].place(x=(17 + self.board[player_id][next_pos[i][0]][1]), y=430)
                                else:
                                    list_btn_option.append(tk.Button(self.main_frame, text="Take out"))
                                    if player_id == 0:
                                        list_btn_option[i].place(x=12, y=560)
                                    else:
                                        list_btn_option[i].place(x=1133, y=560)

                            if len(list_btn_option) > 0:
                                if list_btn_option[0]["text"] == "Take out":
                                    list_btn_option[0].config(command=lambda: self.remove_piece(player_id, x))
                                else:
                                    list_btn_option[0].config(
                                        command=lambda: self.move_piece(player_id, next_pos[0][0], x))

                                if len(list_btn_option) == 2:
                                    if list_btn_option[1]["text"] == "Take out":
                                        list_btn_option[1].config(command=lambda: self.remove_piece(player_id, x))
                                    else:
                                        list_btn_option[1].config(
                                            command=lambda: self.move_piece(player_id, next_pos[1][0], x))
            else:
                dice = []

                if turn == 0:
                    # turn = 1
                    self.set_turn(1)
                    # label_mini_list[0].config(fg="white")
                    # label_mini_list[1].config(fg="#80ff80")
                else:
                    # turn = 0
                    self.set_turn(0)
                    # label_mini_list[1].config(fg="white")
                    # label_mini_list[0].config(fg="#80ff80")
                
                roll_button.config(state="normal")
        else:
            dice = []

            if turn == 0:
                # turn = 1
                self.set_turn(1)
                # label_mini_list[0].config(fg="white")
                # label_mini_list[1].config(fg="#80ff80")
            else:
                # turn = 0
                self.set_turn(0)
                # label_mini_list[1].config(fg="white")
                # label_mini_list[0].config(fg="#80ff80")

            roll_button.config(state="normal")

    def remove_piece(self, player_id, column):
        """
        This method addresses only to the pieces "eaten" by the other player.
        When a piece gets eaten, it will be removed from board and the count for eliminated pieces for that player
        will go up.
        After the piece gets eliminated we need to find what number on the dice led to this move so we can remove it.
        Then we destroy the option buttons that showed the player where he could move the piece selected.
        The statistics are updated on the screen.
        It is then checked if either of the players won the game.
        The if the numbers on the dice were all used up the game will be prepared for the next player.

        :param player_id: the player id as index for board list
        :param column: column number to know from where the piece is removed
        :return: None
        """
        self.board[player_id][column][0][-1].destroy()
        self.board[player_id][column][0].pop()
        self.stats[player_id][1] += 1

        verify_taken_out = 0
        for index in range(0, len(dice)):
            if column + 1 == dice[index]:
                dice.remove(column + 1)
                verify_taken_out = 1
                break

        if verify_taken_out == 0:
            okay = 0
            for i in range(1, 6):
                if okay == 0:
                    for index in range(0, len(dice)):
                        if i + column == dice[index]:
                            dice.remove(dice[index])
                            okay = 1
                            break

        global list_btn_option, roll_button
        for index in list_btn_option:
            index.destroy()
        for index in range(0, len(list_btn_option)):
            list_btn_option.pop()

        self.show_player_stats(self.main_frame, self.stats)

        winner = who_won(self)
        if winner > 0:
            show_winner(self.window, winner, self)

        if len(dice) == 0:
            global turn
            roll_button.config(state="normal")

            if player_id == 0:
                # turn = 1
                self.set_turn(1)
                # label_mini_list[0].config(fg="white")
                # label_mini_list[1].config(fg="#80ff80")
            else:
                # turn = 0
                self.set_turn(0)
                # label_mini_list[1].config(fg="white")
                # label_mini_list[0].config(fg="#80ff80")

    def revive(self, player_id):
        """
        This method takes the player id to get to know which player it should "revive".
        Depending on which player turn's it is, this method will generate some coordinates based on which it will
        place the piece on the board.

        Based on what dice the player rolled, this method will suggest to the player which columns he can use to put
        his piece on.

        When clicked, the button will call 'move_piece' method that will move the piece to the designated column.
        More info about how moving pieces works at 'move_piece' method.

        :param player_id: the id of the player as it is stored in the board list (0 - player 1; 1 - player 2 / PC)
        :return: None
        """
        if player_id == 1:
            other_player = 0
            coord_y = 15
        else:
            other_player = 1
            coord_y = 730

        possible_position = []
        global dice, turn

        if len(dice) == 2:
            for zar in dice:
                if len(self.board[other_player][zar - 1][0]) < 2:
                    possible_position.append([zar - 1, coord_y])
        else:
            if len(self.board[other_player][dice[0] - 1][0]) < 2:
                possible_position.append([dice[0] - 1, coord_y])

        if len(possible_position) == 0:
            roll_button.config(state="normal")
            dice = []
        else:
            global list_btn_option

            for i in range(0, len(possible_position)):
                if possible_position[i][1] == 15:
                    list_btn_option.append(tk.Button(self.main_frame, text=" ^ "))
                    list_btn_option[i].place(x=(17 + self.board[player_id][possible_position[i][0]][1]), y=350)
                else:
                    list_btn_option.append(tk.Button(self.main_frame, text=" v "))
                    list_btn_option[i].place(x=(17 + self.board[player_id][possible_position[i][0]][1]), y=430)

            if len(list_btn_option) > 0:
                list_btn_option[0].config(command=lambda: self.move_piece(player_id, possible_position[0][0], -5))
                if len(list_btn_option) == 2:
                    list_btn_option[1].config(command=lambda: self.move_piece(player_id, possible_position[1][0], -5))

            if self.name[player_id] == "PC":
                choice = random.randrange(0, len(list_btn_option))
                list_btn_option[choice].invoke()


    def move(self, player_id, x, y):
        """
        This method will call the methods needed for playing the actual turn, but before that it will run some
        verification based on which it may show some 'error' or 'info' boxes, both with informational purposes.
        :param player_id: the id of the player as it is stored in the board list (0 - player 1; 1 - player 2 / PC)
        :param x: column id based on which player turn it is
        :param y: coordinates to know if the column is on top or on bottom of the game board
        :return: None
        """
        global turn, dice
        # XXX <
        global my_id
        # XXX >

        if turn == 0 and len(dice) > 0:
            if player_id != my_id:  # XXX
                messagebox.showerror("Backgammon!!", "Not your piece")
            else:
                if self.stats[player_id][0] == 0:
                    self.options(player_id, x, y)
                else:
                    messagebox.showinfo("Backgammon!!",
                                        "You can't move pieces.\nYou have to get the eliminated ones "
                                        "on the board first.")

        elif turn == 1 and len(dice) > 0:
            if player_id != my_id:
                messagebox.showerror("Backgammon!!", "Not your piece")
            else:
                if self.stats[player_id][0] == 0:
                    self.options(player_id, x, y)
                else:
                    messagebox.showinfo("Backgammon!!",
                                        "You can't move pieces.\nYou have to get the eliminated ones "
                                        "on the board first.")

        else:
            messagebox.showerror("Backgammon!!", "You must roll the dice first")

    # XXX
    def set_turn(self, val: int, both:bool=True):
        '''
            set turn for players
            recolor names
        '''
        global turn
        turn = val
        c0, c1 = ['white', '#80ff80'] if val == 1 else ['#80ff80', 'white']
        label_mini_list[0].config(fg=c0)
        label_mini_list[1].config(fg=c1)
        if both:
            send_to_p2p(cmd.TURN + ' ' + str(val))










# END CLASS


def who_won(player):
    """
    This method check if any of the players took out 15 pieces. If not then 0 is returned meaning no player has yet won.
    If a player took out 15 pieces it will return 1 or 2 based on which player won.

    :param player: object of type Game that holds the game information
    :type player: Game
    :return: a code number for the player that won (1 - player 1; 2 - player 2 / PC; 0 - none )
    """
    if player.stats[0][1] == 15:
        return 1
    elif player.stats[1][1] == 15:
        return 2
    else:
        return 0


def get_roll_dice_from_server():
    global my_id
    if turn == my_id:
        send_to_server(server_conn, cmd.ROLL)
    else: # XXX
        messagebox.showerror("Backgammon!!", "Not your turn")







def roll_dice(zar1,zar2):
    global my_id  # XXX
    global image, turn ,main_frame,game

    # time.sleep(0.5)
    global dice
    if zar1 == zar2:
        dice.append(zar1)
        dice.append(zar1)
        dice.append(zar1)
        dice.append(zar1)
    else:
        dice.append(zar1)
        dice.append(zar2)

    img1 = tk.PhotoImage(file="assets/dice1.png")
    img2 = tk.PhotoImage(file="assets/dice2.png")
    img3 = tk.PhotoImage(file="assets/dice3.png")
    img4 = tk.PhotoImage(file="assets/dice4.png")
    img5 = tk.PhotoImage(file="assets/dice5.png")
    img6 = tk.PhotoImage(file="assets/dice6.png")
    image = [img1, img2, img3, img4, img5, img6]

    if len(dice_image) <= 0:
        dice_image.append(tk.Label(main_frame, image=image[zar1 - 1]))
        dice_image[0].place(x=780, y=380)

        dice_image.append(tk.Label(main_frame, image=image[zar2 - 1]))
        dice_image[1].place(x=830, y=380)
    else:
        dice_image[0].configure(image=image[zar1 - 1])
        dice_image[0].place(x=780, y=380)

        dice_image[1].configure(image=image[zar2 - 1])
        dice_image[1].place(x=830, y=380)

    roll_button.config(state="disabled")
    if game.stats[turn][0] > 0:
        game.revive(turn)
        if len(dice) == 0:

            if turn == 0:
                # turn = 1
                game.set_turn(1)
                # label_mini_list[0].config(fg="white")
                # label_mini_list[1].config(fg="#80ff80")
            else:
                # turn = 0
                game.set_turn(0)
                # label_mini_list[1].config(fg="white")
                # label_mini_list[0].config(fg="#80ff80")

    if not game.exist_move(turn):
        roll_button.config(state="normal")



def show_winner(window, id_player, player):
    roll_button.config(state="disabled")
    if id_player == 1:
        text = player.name[0]
    else:
        text = player.name[1]

    canvas = tk.Canvas(window, width=600, height=400, bg="#000000")
    canvas.place(x=600, y=400, anchor=CENTER)

    color_codes = ["#fb1239", "#aa40ff", "#f0851b", "#0033cc", "#ffa97e", "#FFE133", "#64FF33", "#FF0D0D", "#0DB7FF",
                   "#FF2DB6"]
    max_fireworks = random.randrange(10, 15)

    color = 0

    for i in range(0, max_fireworks):
        x = random.randrange(0, 600)
        y = random.randrange(0, 400)
        color = random.randrange(0, 9)
        dim = random.randrange(75, 225)
        canvas.create_oval(x, y, x + dim, y + dim, fill=color_codes[color])

    canvas.create_oval(200, 100, 400, 300, fill=color_codes[color])
    text = text + " won!!"
    text_font = font.Font(size=20)
    label_winner = tk.Label(canvas, text=text, fg="#000000", bg=color_codes[color], font=text_font)
    canvas.create_window(300, 200, window=label_winner)

    #TODO
      # Schedule cleanup after 5 seconds
    # window.after(5000, lambda: cleanup(window))

def cleanup(window):
    """Clean up all windows and exit the application."""
    # exit()
    global to_be_destroyed, main_frame, game
    
    # Destroy specific widgets
    for w in to_be_destroyed:
        try:
            w.destroy()
        except Exception:
            pass
    to_be_destroyed = []

    # Destroy main frame and game-related widgets
    try:
        if main_frame:
            main_frame.destroy()
        if game and hasattr(game, 'window'):
            game.window.destroy()
        if game and hasattr(game, 'main_frame'):
            game.main_frame.destroy()
    except Exception:
        pass
    

    # window.mainloop


def player_gui_init(window):
    """
    This method initialises the game between 2 players.
    It creates a frame on top of the window in which will put as background the board for the game.
    On top of the background will be added the 'Roll' button and from here the actual playable game will be done via
    Game class.

    :param window: the window in which we see and play the game, used for displaying widgets
    :return: None
    """
    global main_frame
    main_frame = tk.Frame(window, width=1200, height=800)
    main_frame.pack(side="top", expand=False, fill="both")
    
    global background, game, dice_image, roll_button
    background = tk.PhotoImage(file="assets/board2.png")
    label_background = tk.Label(main_frame, image=background)
    label_background.place(x=-3, y=-2)

    game = Game(window, main_frame, "player 1", "player 2")

    dice_image = []
    text_font = font.Font(size=14)
    roll_button = tk.Button(main_frame, text="Roll", font=text_font, bg='#4e555f', fg='white', border=2,
                            command=lambda: get_roll_dice_from_server())
    roll_button.place(x=360, y=380)


def main_menu(window):
    def player_callback(main_window):
        main_window.destroy()
        new_window = create_window()
        player_gui_init(new_window)

    player_callback(window)
    window.mainloop()


def create_window():
    """
    Here we will create the window for the game with the proper name and icon.

    :return: the window in which will be displayed the game
    """

    window = tk.Tk()
    window.title(f'PLAYER {my_id + 1}')

    window.configure(width=1200, height=800)
    window.resizable(False, False)

    icon = tk.PhotoImage(file="assets/icon.png")
    window.iconphoto(False, icon)

    window.eval('tk::PlaceWindow . center')
    # XXX <
    global to_be_destroyed
    to_be_destroyed.append(window)
    # Bind the close event to the custom function
    window.protocol("WM_DELETE_WINDOW", on_close_game)
    # XXX >
    return window


class NoDevSupport:
    """
    This class is supposed to do nothing and contains a single method doing just than.
    It is used to stop the printing of errors and traceback messages in the console.
    """

    def write(self, msg):
        """
        This method does nothing much.

        :param msg: a message
        :return: None
        """
        pass

def reset_globals():
    global game, main_frame, conn, server_conn, dice, label_mini_list, roll_button
    game = None
    main_frame = None
    conn = None
    server_conn = None
    dice = []
    label_mini_list = []
    roll_button = None


def on_close_game():
    """
    Handle the game window close event.
    Ensures cleanup and stops any background processes or threads.
    """
    if messagebox.askokcancel("Quit Game", "Are you sure you want to quit the game?"):
        print("Performing cleanup...")
        
        # Perform game-specific cleanup
        # cleanup()  # Call your existing cleanup function
        
        # Destroy the Tkinter window
        if game and hasattr(game, 'window'):
            game.window.destroy()

        reset_globals()

        # Exit the program
        sys.exit(0)  # Optional: Exit the entire program


def main(p2p_conn1, id , server_conn1):
    # XXX <
    global conn, my_id, game,server_conn
    my_id = id
    conn = p2p_conn1
    server_conn = server_conn1
    # XXX >
    sys.stderr = NoDevSupport()
    window = create_window()
    main_menu(window)
    window.mainloop()


if __name__ == '__main__':
    main()

# XXX my funcs
def send_to_p2p(msg: str):
    global conn
    conn.sendall(msg.strip().encode())

