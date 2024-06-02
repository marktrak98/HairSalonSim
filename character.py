from __future__ import annotations
import random
import datetime

from vector import Vector2
from utils import get_directions
from mood import Mood
from hair import Hair

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import Game


#👧👩👩‍🦰🧑‍🦰👩‍🦳👩‍🦲🧑‍🦳👱‍♀️
class Character:

    NAMES = ['Emily', 'Alice', 'May', 'Olivia', 'Sophia', 'Ava', 
             'Isabella', 'Mia', 'Charlotte', 'Amelia', 'Haley', 
             'Evelyn', 'Abigail', 'Emily', 'Elizabeth', 'Sofia', 
             'Ella', 'Scarlett', 'Grace', 'Victoria']

    def __init__(self, game: Game, name: str, age: int, hair: Hair, mood: Mood, position: Vector2):
        self.game = game
        self.world = self.game.world
        self.chat = self.game.chat

        self.name = name
        self.age = age
        self.hair = hair
        self.mood = mood

        self.has_cape = False
        self.has_neck_roll = False

        self.position = position

        self.time_to_next_action = self.game.current_gametime

        self.pending_actions: list = [
            ('plan', 'sit in a waiting chair'),
        ]

        self.async_actions: list = [
            ('interact with player', 'introduce self to player'),
        ]

    def add_action(self, action, args):
        self.pending_actions.append((action, args))

    def on_player_interact(self):
        if ('interact with player', 'introduce self to player') in self.async_actions:
            self.chat.add_dialogue(f'{self.name}: Hi! My name is {self.name}.')

    def goto_position(self, target_position):
        directions = get_directions(self.position, target_position, self.world.is_traversable)

        if directions == -1: return False

        self.pending_actions.extend([('move', direction) for direction in directions])
        return True
    
    ACTION_TIME_COST = {
        'plan': datetime.timedelta(minutes=1),
        'move': datetime.timedelta(seconds=15),
        'leave': datetime.timedelta(minutes=1)
    }  # In minutes

    def update(self):
        if not self.pending_actions or self.time_to_next_action > self.game.current_gametime: return

        action, args = self.pending_actions.pop(0)

        if action == 'move':
            self.position += args
            self.world.needs_refresh = True

        elif action == 'leave':
            if self.position != Vector2(22, 12): raise Exception('Canno\'t leave unless at exit')

            self.game.characters.remove(self)
            self.world.needs_refresh = True

        elif action == 'plan':
            if args == 'sit in a waiting chair':
                free_waiting_chairs = [pos for pos, occupant in self.world.waiting_chairs.items() if occupant is None]
                if free_waiting_chairs:
                    character_waiting_chair_pos = random.choice(free_waiting_chairs)
                    self.world.waiting_chairs[character_waiting_chair_pos] = self
                    if not self.goto_position(character_waiting_chair_pos):
                        # Planning couldn't be done, so plan again next time
                        self.pending_actions.insert(0, (action, args))

            elif args == 'sit in a haircutting chair':
                free_haircutting_chairs = [pos for pos, occupant in self.world.haircutting_chairs.items() if occupant is None]
                if free_haircutting_chairs:
                    character_haircutting_chair_pos = random.choice(free_haircutting_chairs)
                    self.world.waiting_chairs[self.position] = None
                    self.world.haircutting_chairs[character_haircutting_chair_pos] = self
                    if not self.goto_position(character_haircutting_chair_pos):
                        # Planning couldn't be done, so plan again next time
                        pass
                        # Not readding plan
                        #self.pending_actions.insert(0, (action, args))

            elif args == 'walk out':
                if self.position in self.world.haircutting_chairs:
                    self.world.haircutting_chairs[self.position] = None

                elif self.position in self.world.waiting_chairs:
                    self.world.waiting_chairs[self.position] = None

                self.goto_position(Vector2(22, 12))
                self.add_action('leave', None)

            else:
                raise NotImplementedError()

        else:
            raise NotImplementedError()
        
        self.time_to_next_action = self.game.current_gametime + self.ACTION_TIME_COST[action]

    @classmethod
    def new(cls, game: Game):
        return cls(game, random.choice(cls.NAMES), random.randint(18, 30), Hair.new(), Mood.new(), Vector2(24, 12))
        