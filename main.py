from game_constants import *
from chess_game import ChessGame
import pygame as pg
pg.init()

#GAME SPECIFIC BLOCK
pg.display.set_caption("Hector Chess - Sint-Pieterscollege, Jette")
win = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pg.time.Clock()
theGame = ChessGame(win, clock)
theGame.execute()
pg.quit()
