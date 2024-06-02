from __future__ import annotations


import curses
import datetime
import time


from windows import WorldWindow, HaircuttingChairWindow, ControlsWindow, ChatWindow
from player import Player
from character import Character


class Game:

    TERMINAL_SIZE = (30, 100)

    FPS = 15
    GAMETIME_SECONDS_PER_FRAME = 60 / FPS  # seconds/frame

    def __init__(self) -> None:
        self.current_gametime = datetime.datetime(2024, 5, 1, 10, 0, 0)

        self.gametime_delta_per_frame = datetime.timedelta(seconds=self.GAMETIME_SECONDS_PER_FRAME)

        self.player = Player()
        self.characters: list[Character] = []

        self.current_view = 'world'

        self.current_fps = 10

    def on_haircut_chair_interact(self, character: Character):
        self.haircutting_chair.character = character
        self.current_view = 'haircutting_chair'

        self.haircutting_chair.refresh_needed = True

    def add_character(self, character: Character):
        self.characters.append(character)
    
    def iter_loop(self):
        self.controls.update()

        [character.update() for character in self.characters]

        self.draw()

    def draw(self):
        if self.current_view == 'world':
            self.world.draw()
        elif self.current_view == 'haircutting_chair':
            self.haircutting_chair.draw()
        self.controls.draw()
        self.chat.draw()
        #self.stdscr.refresh()

    def run(self, stdscr: curses.window):
        curses.resizeterm(*self.TERMINAL_SIZE)
        curses.noecho()
        curses.curs_set(0)

        SPF = 1/self.FPS
        self.stdscr = stdscr

        self.world = WorldWindow(self)
        self.controls = ControlsWindow(self)
        self.chat = ChatWindow(self)
        self.haircutting_chair = HaircuttingChairWindow(self)
        

        # DEBUG
        # Spawn character on haircutting_chair and open haircutting view
        # character = Character.new(self)
        # self.add_character(character)
        # character.position = self.world.haircutting_chairs.keys().__iter__().__next__()
        # self.world.haircutting_chairs[character.position] = character
        # character.pending_actions = []
        # self.on_haircut_chair_interact(character)
        # self.haircutting_chair.current_menu = '(c)ut'
        # self.haircutting_chair.chosen_tool = '(s)cissors'
        # self.haircutting_chair.tool_mode = self.haircutting_chair.LAST_TOOL_MODE[self.haircutting_chair.chosen_tool]

        self.running = True
        last_time = time.time()
        while self.running:
            self.iter_loop()

            time.sleep(max(SPF-time.time()+last_time, 0))
            self.current_fps = 1/(time.time() - last_time)
            last_time = time.time()

            self.current_gametime += self.gametime_delta_per_frame


game = Game()
curses.wrapper(game.run)
