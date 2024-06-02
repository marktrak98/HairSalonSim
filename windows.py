from __future__ import annotations
import curses
from math import floor, ceil
import textwrap
from sys import platform

from utils import log, only_alnum
from vector import Vector2
from character import Character
from hair import HairSection


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import Game

MAIN_WINDOW_HEIGHT = 0.8
MAIN_WINDOW_WIDTH = 0.6
CONTROLS_WINDOW_HEIGHT = 1 - MAIN_WINDOW_HEIGHT
CHAT_WINDOW_WIDTH = 1 - MAIN_WINDOW_WIDTH


if platform == 'win32':
    MAN = 'X'
    WOMAN = 'Y'

else:
    MAN = '👨'
    WOMAN = '👩'


class WorldWindow:
    
    SALON = r'''


  ┌─────────┬────────────────────┬─────────┐
  │         └────────────────────┘    [--] │
  │                                  ┌────┐│
  │             [__]      [__]       └────┘│
  │                                        │
  │                                        │
  │                                        │
  │ ┌__──__──__┐              ┌__──__──__┐ │
  │ └──────────┘   \      /   └──────────┘ │
  └─────────────────┘    └─────────────────┘
'''[1:-1].split('\n')
    WALLS = r'┌┐└┘│─\/'
    WAITING_CHAIRS = [Vector2(6, 10), Vector2(10, 10), Vector2(14, 10),
                    Vector2(32, 10), Vector2(36, 10), Vector2(40, 10)]
    HAIRCUTTING_CHAIRS = [Vector2(18, 6), Vector2(28, 6)]
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.window = curses.newwin(ceil(curses.LINES*MAIN_WINDOW_HEIGHT), ceil(curses.COLS*MAIN_WINDOW_WIDTH), 
                                    0, 0)
        
        self.waiting_chairs: dict[Vector2, None|Character] = {pos: None for pos in self.WAITING_CHAIRS}
        self.haircutting_chairs: dict[Vector2, None|Character] = {pos: None for pos in self.HAIRCUTTING_CHAIRS}

        self.needs_refresh = True

    def draw(self):
        if self.needs_refresh:
            self.window.clear()

            self.window.border()
            self.window.addstr(0, 1, 'World')

            for i, line in enumerate(self.SALON):
                self.window.addstr(1+i, 1, line)

            self.window.addch(self.game.player.position.y, self.game.player.position.x, MAN)
            for character in self.game.characters:
                self.window.addch(character.position.y, character.position.x, WOMAN)

            self.window.refresh()
            self.needs_refresh = False

    def is_traversable(self, x, y):
        if y>0 and y-1 < len(self.SALON) and x>0 and x-1 < len(self.SALON[y-1]):
            return self.SALON[y-1][x-1] not in self.WALLS and self.SALON[y-1][x] not in self.WALLS
        else:
            return True
        

class HaircuttingChairWindow:
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.world = self.game.world
        self.chat = self.game.chat
        self.character: Character = None # type: ignore

        self.window = curses.newwin(ceil(curses.LINES*MAIN_WINDOW_HEIGHT), ceil(curses.COLS*MAIN_WINDOW_WIDTH), 
                                    0, 0)

        self.text_window = curses.newwin(ceil(curses.LINES*MAIN_WINDOW_HEIGHT)-2, ceil(curses.COLS*MAIN_WINDOW_WIDTH)-4, 
                                    1, 2)

        self.window.nodelay(True)

        self.current_menu = 'category'
        self.chosen_tool: str = None # type: ignore
        self.tool_mode: list[int] = None # type: ignore

        self.refresh_needed = False

        self.menu_selection_position = Vector2(2, 2)

    MENU_SELECTION = {'p': '(p)rep', 'c': '(c)ut', 'f': '(f)inish'}

    MENU_SUBSELECTION = {
        '(p)rep': {'w': '(w)ash', 'n': '(n)eck roll', 'c': '(c)ape', 'b': '(b)rush', 'x': '(x)back'},
        '(c)ut': {'p': 's(p)ray', 'e': 's(e)ction', 's': '(s)cissors', 'c': '(c)lippers', 'r':'(r)azor', 'x': '(x)back'},
        '(f)inish': {'c': '(c)lean', 'b': '(b)low dry', 'f': '(f)ree', 's': '(s)end off', 'x': '(x)back'},
    }

    LAST_TOOL_MODE = {
        's(p)ray': [0],
        '(s)cissors': [0, 0],
        '(c)lippers': [0, 0],
        '(r)azor': [0]
    }

    TOOL_MODES = {
        's(p)ray': (['precise', 'wide', 'bulk']),
        '(s)cissors': (['precise', 'wide', 'bulk'], [f'{2**i} inch' for i in range(5)]),
        '(c)lippers': (['precise', 'wide', 'bulk'], ['guardless'] + [f'N{i} guard' for i in range(1, 9)]),
        '(r)azor': (['precise', 'wide', 'bulk'])
    }

    def get_tool_mode(self) -> list[str]:
        return [i[j] for i, j in zip(self.TOOL_MODES[self.chosen_tool], self.tool_mode)]

    def on_key_press(self, key: str):
        if self.current_menu == 'category':
            if key in self.MENU_SELECTION:
                self.current_menu = self.MENU_SELECTION[key]
                self.refresh_needed = True

        elif self.chosen_tool == None:
            if key in self.MENU_SUBSELECTION[self.current_menu]:
                chosen = self.MENU_SUBSELECTION[self.current_menu][key]
                if chosen == '(x)back':
                    self.current_menu = 'category'

                elif chosen == '(w)ash':
                    self.chat.add_dialogue(f'You wash {self.character.name}\'s hair under a sink.')
                    self.character.hair.on_wash()

                elif chosen == '(n)eck roll':
                    if self.character.has_neck_roll:
                        self.chat.add_dialogue(f'You remove the neckroll from {self.character.name}\'s neck.')
                        
                    else:
                        self.chat.add_dialogue(f'You wrap a neck roll around {self.character.name}\'s neck.')

                    self.character.has_neck_roll = not self.character.has_neck_roll

                elif chosen == '(c)ape':
                    if self.character.has_cape:
                        self.chat.add_dialogue(f'You uncape {self.character.name}.')
                        
                    else:
                        self.chat.add_dialogue(f'You cover {self.character.name}\'s with a cape.')

                    self.character.has_cape = not self.character.has_cape

                elif chosen == '(b)rush':
                    self.chat.add_dialogue(f'You brush out {self.character.name}\'s hair.')

                elif chosen == '(c)lean':
                    if self.character.has_cape:
                        self.chat.add_dialogue(f'You clean up {self.character.name}\'s cape of cut hair.')
                    else:
                        self.chat.add_dialogue(f'You clean up {self.character.name}\'s dress of cut hair.')

                elif chosen == '(b)low dry':
                    self.chat.add_dialogue(f'You blow dry {self.character.name}\'s hair.')
                    self.character.hair.on_blow_dry()

                elif chosen == '(f)ree':
                    if self.character.has_cape and self.character.has_neck_roll:
                        self.chat.add_dialogue(f'You uncape {self.character.name} and also remove the neckroll from her neck.')
                        self.character.has_neck_roll = False
                        self.character.has_cape = False
                    elif self.character.has_cape:
                        self.chat.add_dialogue(f'You uncape {self.character.name}.')
                        self.character.has_cape = False
                    elif self.character.has_neck_roll:
                        self.chat.add_dialogue(f'You remove the neckroll from {self.character.name}\'s neck.')
                        self.character.has_neck_roll = False
                    else:
                        self.chat.add_dialogue(f'{self.character.name} is not caped nor does she have a neck roll on.')
                    
                elif chosen == '(s)end off':
                    if self.character.has_cape and self.character.has_neck_roll:
                        self.chat.add_dialogue(f'Remove the cape and neck roll from {self.character.name} before you send her off.')
                    
                    elif self.character.has_cape:
                        self.chat.add_dialogue(f'Remove the cape from {self.character.name} before you send her off.')
                    
                    elif self.character.has_neck_roll:
                        self.chat.add_dialogue(f'Remove the neck roll from {self.character.name} before you send her off.')
                    
                    else:
                        self.chat.add_dialogue(f'{self.character.name} gets up from the chair.')
                        self.character.add_action('plan', 'walk out')
                        self.game.current_view = 'world'

                elif chosen in self.LAST_TOOL_MODE:
                        self.chosen_tool = chosen
                        self.tool_mode = self.LAST_TOOL_MODE[chosen]
                else:
                    return
                
                self.refresh_needed = True

        else:
            if key == 'x':
                self.chosen_tool = None # type: ignore

            elif key == 'r':
                self.tool_mode[0] = min(self.tool_mode[0]+1, len(self.TOOL_MODES[self.chosen_tool][0])-1)

            elif key == 'f':
                self.tool_mode[0] = max(self.tool_mode[0]-1, 0)

            elif key == 't' and len(self.tool_mode) > 1:
                self.tool_mode[1] = min(self.tool_mode[1]+1, len(self.TOOL_MODES[self.chosen_tool][1])-1)

            elif key == 'g' and len(self.tool_mode) > 1:
                self.tool_mode[1] = max(self.tool_mode[1]-1, 0)

            elif key in 'wasd':
                x, y = self.menu_selection_position

                if key == 'w':
                    y -= 1
                    if not 0 <= y <= 4 or self.character.hair.sections_by_position[y][x] == None:
                        y += 1

                elif key == 'a':
                    x -= 1
                    if not 0 <= x <= 3 or self.character.hair.sections_by_position[y][x] == None:
                        x += 1

                elif key == 's':
                    y += 1
                    if not 0 <= y <= 4 or self.character.hair.sections_by_position[y][x] == None:
                        y -= 1

                elif key == 'd':
                    x += 1
                    if not 0 <= x <= 3 or self.character.hair.sections_by_position[y][x] == None:
                        x -= 1

                self.menu_selection_position = Vector2(x, y)

            elif key in ('\n', '\r'): 
                x, y = self.menu_selection_position
                hair_section: HairSection = self.character.hair.sections_by_position[y][x] # type: ignore
                if self.chosen_tool == 's(p)ray':
                    hair_section._wetness += 0.5
                    self.chat.add_dialogue(f'You wet {self.character.name}\'s {hair_section.region_name}.')

                elif self.chosen_tool == '(s)cissors':
                    length_cut = int(self.get_tool_mode()[1].strip(' inch'))
                    hair_section._length = max(hair_section._length-length_cut, 1)
                    self.chat.add_dialogue(f'You cut {length_cut} inches of {self.character.name}\'s hair from her {hair_section.region_name}.')

                elif self.chosen_tool == '(c)lippers':
                    val = self.get_tool_mode()[1]
                    if val == 'guardless':
                        hair_section._length = 0
                        self.chat.add_dialogue(f'You plough the guardless clippers over {self.character.name}\'s {hair_section.region_name}, revealing her bare scalp.')
                    else:
                        length_remaining = int(self.get_tool_mode()[1].strip('N').strip(' guard'))/8
                        hair_section._length = length_remaining
                        self.chat.add_dialogue(f'You plough through {self.character.name}\'s {hair_section.region_name}, leaving behind a {length_remaining} inch stubble.')

                elif self.chosen_tool == '(r)azor':
                    pass

                self.character.hair.evaluate_description()
            
            self.refresh_needed = True

    MENU_START_Y = 10
    def draw(self):
        if self.refresh_needed:
            window = self.window
            text_window = self.text_window
            character = self.character

            window.clear()
            window.border()
            window.addstr(0, 1, 'Haircut')

            text_window.clear()

            text_window.addstr(1, 0, f'Name: {self.character.name}   Age: {self.character.age}   Mood: {self.character.mood}')
            
            hair_description = 'Hair: ' + self.character.hair.description
            for i, line in enumerate(textwrap.wrap(hair_description, width=text_window.getmaxyx()[1])):
                self.text_window.addstr(i+3, 0, line)

            if self.character.has_cape and self.character.has_neck_roll:
                self.text_window.addstr(self.MENU_START_Y-2, 0, 'Caped with neck roll.')

            elif self.character.has_cape and not self.character.has_neck_roll:
                self.text_window.addstr(self.MENU_START_Y-2, 0, 'Caped.')

            elif not self.character.has_cape and self.character.has_neck_roll:
                self.text_window.addstr(self.MENU_START_Y-2, 0, 'Has neck roll.')
            
            else:
                self.text_window.addstr(self.MENU_START_Y-2, 0, 'Uncaped.')

            # Shows line numbers
            #for i in range(0, text_window.getmaxyx()[0]): text_window.addstr(i, 0, str(i))

            if self.current_menu == 'category':
                text_window.addstr(self.MENU_START_Y, 2, 'Category:')
                for i, cat in enumerate(self.MENU_SELECTION.values()):
                    text_window.addstr(self.MENU_START_Y+i+1, 4, cat)

            elif self.chosen_tool == None:
                text_window.addstr(self.MENU_START_Y, 2, f'Category: {only_alnum(self.current_menu)}')
                for i, sel in enumerate(self.MENU_SUBSELECTION[self.current_menu].values()):
                    text_window.addstr(self.MENU_START_Y+i+1, 4, sel)

            else:
                text_window.addstr(self.MENU_START_Y, 2, f'Category: {only_alnum(self.current_menu)} - {only_alnum(self.chosen_tool)}')
                text_window.addstr(self.MENU_START_Y+2, 5, f'{"[r]":^12}')
                text_window.addstr(self.MENU_START_Y+3, 5, f'{self.TOOL_MODES[self.chosen_tool][0][self.tool_mode[0]]:^12}')
                text_window.addstr(self.MENU_START_Y+4, 5, f'{"[f]":^12}')
                
                if len(self.tool_mode) > 1:
                    text_window.addstr(self.MENU_START_Y+2, 39, f'{"[t]":^12}')
                    text_window.addstr(self.MENU_START_Y+3, 39, f'{self.TOOL_MODES[self.chosen_tool][1][self.tool_mode[1]]:^12}')
                    text_window.addstr(self.MENU_START_Y+4, 39, f'{"[g]":^12}')

                hair_sections_display = []
                max_hair_section_length = [0] * 4
                for row in character.hair.sections_by_position:
                    hair_sections_display.append([])
                    for x, section in enumerate(row):
                        to_display = section.region_name if section else ''
                        to_display = self.character.hair.REGION_NAMES_SHORTENED[to_display] + '  '
                        max_hair_section_length[x] = max(max_hair_section_length[x], len(to_display))
                        hair_sections_display[-1].append(to_display)

                for y, row in enumerate(hair_sections_display):
                    for x, to_display in enumerate(row):
                        if Vector2(x, y)==self.menu_selection_position:
                            text_window.addstr(self.MENU_START_Y+6+y, 3+sum(max_hair_section_length[:x]), f'{to_display:^{max_hair_section_length[x]}}', curses.A_STANDOUT)
                        else:
                            text_window.addstr(self.MENU_START_Y+6+y, 3+sum(max_hair_section_length[:x]), f'{to_display:^{max_hair_section_length[x]}}', 0)
            #text_window.addstr(6, 3, 'Tool:')

            window.refresh()
            text_window.refresh()
            self.refresh_needed = False


class ControlsWindow:
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.world = self.game.world
        self.player = self.game.player

        self.window = curses.newwin(curses.LINES-ceil(curses.LINES*MAIN_WINDOW_HEIGHT), ceil(curses.COLS*MAIN_WINDOW_WIDTH), 
                                    ceil(curses.LINES*MAIN_WINDOW_HEIGHT), 0)
        self.window.border()
        self.window.addstr(0, 1, 'Controls')

        self.window.nodelay(True)

    def draw(self):
        fps_text = f"FPS:{self.game.current_fps:4.1f}"
        self.window.addstr(1, self.window.getmaxyx()[1]-len(fps_text)-1, fps_text)
        position_text = f'Pos:{self.player.position.x}x{self.player.position.y}'
        self.window.addstr(2, self.window.getmaxyx()[1]-len(position_text)-1, position_text)

        self.window.refresh()

    MOVE_KEYS = {
        'w': Vector2(0, -1),
        'a': Vector2(-2, 0),
        's': Vector2(0, 1),
        'd': Vector2(2, 0),
    }

    def update(self):
        inp = self.window.getch()

        if inp != -1:
            key = chr(inp)

            if key == 'q':
                self.game.running = False

            if self.game.current_view == 'world':

                if key in self.MOVE_KEYS:
                    new_pos = self.player.position + self.MOVE_KEYS[key]
                    if self.world.is_traversable(*new_pos):
                        if new_pos in self.world.waiting_chairs and self.world.waiting_chairs[new_pos] is not None:
                            self.world.waiting_chairs[new_pos].on_player_interact() # type: ignore
                            self.game.world.needs_refresh = True

                        elif new_pos in self.world.haircutting_chairs and self.world.haircutting_chairs[new_pos] is not None:
                            self.game.on_haircut_chair_interact(self.world.haircutting_chairs[new_pos]) # type: ignore

                        else:
                            self.player.position += self.MOVE_KEYS[key]
                            self.game.world.needs_refresh = True

                elif key == 'N':
                    created_character = Character.new(self.game)
                    self.game.add_character(created_character)

                    self.game.world.needs_refresh = True

                elif key == 'n':
                    for character in self.game.characters:
                        if character.position in self.world.waiting_chairs:
                            character.add_action('plan', 'sit in a haircutting chair')
                            self.game.world.needs_refresh = True
                            break

            elif self.game.current_view == 'haircutting_chair':
                if key == 'e':
                    self.game.current_view = 'world'
                    self.game.world.needs_refresh = True

                else:
                    self.game.haircutting_chair.on_key_press(key)

            self.window.addstr(3, self.window.getmaxyx()[1]-2, key)


class ChatWindow:
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.window = curses.newwin(curses.LINES, floor(curses.COLS*CHAT_WINDOW_WIDTH), 
                                    0, ceil(curses.COLS*MAIN_WINDOW_WIDTH))

        self.history = []
        # self.add_dialogue('ERROR! Not showing up!')
        # self.add_dialogue('ERROR! Not showing up!')

        self.chat_width = self.window.getmaxyx()[1] - 2
        self.chat_height = self.window.getmaxyx()[0] - 2

        self.refresh_needed = True


    def draw(self):
        if self.refresh_needed:
            self.window.clear()

            self.window.border()
            self.window.addstr(0, 1, 'Chat')

            for i in range(1, min(self.chat_height-1, len(self.history)+1)):
                self.window.addstr(self.chat_height-i-1, 1, self.history[-i])

            self.window.refresh()
            self.refresh_needed = False

    def add_dialogue(self, dialogue):
        for i in range(0, len(dialogue), self.chat_width):
            self.history.append(dialogue[i:i+self.chat_width])

        self.refresh_needed = True
