from game_area import GameArea

"""
   Dit is de game area waar alle spelerinformatie wordt getoond 
   player1: name, type, timer, ...
   player2: name, type, timer, ...
"""
class GameAreaPlayers(GameArea):
    def __init__(self, game, r):
        GameArea.__init__(self, game, r)

    def draw(self):
        GameArea.draw(self)