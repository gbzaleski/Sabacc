from typing import Optional

# Class for game participant
class Player:
    def __init__(self, starting_money : int) -> None:
        self.name : str = ""
        self.money : int = starting_money
        self.folded : bool = False
        self.cards : list[tuple[str, Optional[int]]] = []
        self.message : str = ""