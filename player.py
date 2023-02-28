from typing import Optional

# Class for game participant
class Player:
    def __init__(self, starting_money : int) -> None:
        self.name = ""
        self.money = starting_money
        self.folded = False
        self.cards : list[tuple[str, Optional[int]]] = []
        self.message = ""