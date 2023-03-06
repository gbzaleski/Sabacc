from typing import Optional


# Class for game participant
class Player:
    def __init__(self, starting_money: int) -> None:
        self.name = ""
        self.money = starting_money
        self.folded = False
        self.cards: list[tuple[str, Optional[int]]] = []
        self.message = ""

    def get_cards_value(self) -> int:
        sum_cards = 0
        for _, card_value in self.cards:
            assert card_value is not None
            sum_cards += card_value
        return sum_cards
