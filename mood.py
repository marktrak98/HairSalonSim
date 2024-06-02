


class Mood:

    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return self.current_mood
    
    @property
    def current_mood(self):
        return 'Happy'
    
    @classmethod
    def new(cls):
        return cls()