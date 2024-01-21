from game_constants import *
from evt_obj import EvtObj
import time as t
import pygame as pg

"""
Generieke klasse Game die basisfunctionaliteiten voor een game beheert
Heeft niets te maken met de specifieke functionaliteiten zoals die van van een schaakspel
"""
class Game(EvtObj):
    def __init__(self, window, clock):
        EvtObj.__init__(self)
        self.win = window
        self.clock = clock
        self.keep_running = True
        self.last_cycle = t.time()
    def handle_events(self):
        """
        Deze functie zet pygame events om naar onze eigen handige routines
        Je kan dan bijvoorbeeld de functie self.MOUSEBUTTONDOWN(x, y) oproepen,
        zonder te weten hoe de pygame eventhandler dit opslaat.
        """
        # Keyboard Events are already filtered out
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.keep_running = False
            if event.type == pg.MOUSEWHEEL:
                self.MOUSEWHEEL(event.y)
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pg.mouse.get_pos()
                self.MOUSEBUTTONDOWN(mouse_x, mouse_y)
            if event.type == pg.MOUSEBUTTONUP:
                mouse_x, mouse_y = pg.mouse.get_pos()
                self.MOUSEBUTTONUP(mouse_x, mouse_y)
            if event.type == pg.MOUSEMOTION:
                mouse_x, mouse_y = pg.mouse.get_pos()
                self.MOUSEMOTION(mouse_x, mouse_y)

    def update_data(self):
        # whatever needs to changed (used for animation or special effects)
        pass

    def draw(self):
        # whatever needs to drawn happens here
        pass

    # execute_cycle is typically called from the main loop
    # execute_cycle can be called from 'background' routine like an AI-learning cycle
    # we can then play the game while the AI learns in the background
    def execute_cycle(self):
        self.last_cycle = t.time()
        self.handle_events()
        self.update_data()
        self.draw()
        return self.keep_running

    def execute(self):
        while self.execute_cycle():
            pg.display.update()
            self.clock.tick(FRAME_RATE)

    def execute_from_background(self):
        elapsed_time = t.time() - self.last_cycle
        if elapsed_time * FRAME_RATE > 1:
            self.execute_cycle()

