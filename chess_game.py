from game_constants import *
from colors import *
from game import Game
from chess_area_game import GameAreaChessBoard
from chess_area_history import GameAreaHistory
from chess_area_players import GameAreaPlayers
from chess_area_controls import GameAreaControls
from chess_board import ChessBoard

"""
   Dit is het game object dat alles van het 
   Het is afgeleid van de basis klasse Game die de algemene spelflow controleert
"""


class ChessGame(Game):
    def __init__(self, window, clock):
        Game.__init__(self, window, clock)
        # We definieren de verschillende delen van het scherm, die elk weten hoe ze zich moeten tekenen.
        self.chessboard_area = GameAreaChessBoard(self, GAME_RECT)
        self.history_area = GameAreaHistory(self, HIST_RECT)
        self.player_area = GameAreaPlayers(self, PLAYER_RECT)
        self.control_area = GameAreaControls(self, CONTROL_RECT)

        # We definieren de datastructuren van ons spel
        self.chess_board = ChessBoard()

    def update_data(self):
        # whatever needs to change (animation,...)
        pass

    def clear_window(self):
        # Omdat verschillende delen de clip rect kunnen verzetten, resetten we de clip rect tot het volledige venster
        # Zo zijn we niet afhankelijk van slordigheden
        self.win.set_clip((0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        self.win.fill(GAME_BG_COLOR)

    def draw(self):
        self.clear_window()
        self.chessboard_area.draw()
        self.history_area.draw()
        self.player_area.draw()
        self.control_area.draw()

    """
    Voorbeeld hoe event functies doorgegeven worden naar lager niveau
    """
    def MOUSEBUTTONDOWN(self, mouse_x, mouse_y):
        self.chessboard_area.MOUSEBUTTONDOWN(mouse_x, mouse_y)
        self.history_area.MOUSEBUTTONDOWN(mouse_x, mouse_y)
        self.player_area.MOUSEBUTTONDOWN(mouse_x, mouse_y)
        self.control_area.MOUSEBUTTONDOWN(mouse_x, mouse_y)


