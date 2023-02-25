import random
import copy
import time
from typing import Optional

### Auxiliary function for deck of cards ###
def get_clear_deck(): # [(name, value)]
    deck = []
    colours = ["Sabre", "Stave", "Flask", "Coin"]
    
    for colour in colours:
        deck += [(colour + "-" + str(v), v) for v in range(1, 12)]
        deck.append((colour + "-" + "commander", 12))
        deck.append((colour + "-" + "mistress", 13))
        deck.append((colour + "-" + "master", 14))
        deck.append((colour + "-" + "ace", 15))

    # Negatives
    neg = [("Queen", -2), ("Endurance", -8), ("Balance", -11), 
        ("Demise", -13), ("Moderation", -14), ("Evil-one", -15), ("Star", -17)]

    deck += neg
    deck += [(n + "_", v) for (n, v) in neg]

    # Idiots
    deck.append(("Idiot", 0))
    deck.append(("Idiot2", 0))

    return deck

def sort_deck(deck):
    deck.sort(key = lambda ele: -ele[1]) # Sort by card's value
    return deck

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

## Phases of the game ##
RAISE = "Raise Phase"
ACCEPTING_RAISE = "Accepting Raise Phase" # not used yet
SHUFFLE = "Shuffle Phase"
SHOW = "Show Phase"
RESULTS = "Results Phase"
SUDDEN_DEMISE = "Sudden Demise Phase"
DRAW = "Draw Phase"

GET_BOARD = "Get Board"
SET_NAME = "Set Name"
IDLE = "Idle Phase"

# Anonymous card
BACK_CARD = "Back"

# Messages
BOMB_OUT = "Bomb Out"
PURE_SABACC = "Pure Sabacc"
IDIOTS_ARRAY = "Idiots Array"
SUDDEN_DEMISE_TIE = "Sudden Demise"
BEST_VALUE_WINNER = "Best Value Cards"

# Parametres
BOMB_RATIO = 1
LOG = True

SABACC_VALUE = 23

## Sabacc game object ## 
class SabaccGame:
    def __init__(self, no_of_players : int = 2, starting_money : int = 2000, basic_bet_value : int = 50):
        self.n = no_of_players
        self.players_names = [""] * self.n
        self.money = [starting_money] * self.n
        self.cards = get_clear_deck()
        self.discarded_cards = []
        self.folded = [False] * self.n
        self.whose_turn = -1
        self.whose_turn_accept = -1
        self.card_players = [[] for _ in range(self.n)]
        self.current_phase = IDLE
        self.message = ""
        self.players_messages = [""] * self.n

        self.basic_bet = basic_bet_value
        self.value_to_raise = 0
        self.sabacc_pot = 0
        self.sabacc_winner = -1
        self.main_pot = 0
        self.main_pot_winner = -1


    def set_name(self, pid, name):
        self.players_names[pid] = name


    def draw_card(self):
        if self.cards == []:
            self.cards = shuffle_deck(self.discarded_cards)
            self.discarded_cards = []

        return self.cards.pop()


    def drop_card(self, pid, card):
        if card in self.card_players[pid]:
            self.card_players[pid].remove(card)
            self.discarded_cards.append(card)


    def sort_players_cards(self):
        for i in range(self.n):
            self.card_players[i] = sort_deck(self.card_players[i])


    def collect_start_game(self, in_value):
        for i in range(self.n):
            if self.money[i] < in_value * 2:
                self.folded[i] = True
            else:
                self.folded[i] = False

            if not self.folded[i]:
                self.money[i] -= in_value * 2
                self.main_pot += in_value
                self.sabacc_pot += in_value


    def start_game(self):
        self.collect_start_game(self.basic_bet)
        self.cards = shuffle_deck(self.cards)
        self.message = ""
        self.players_messages = [""] * self.n

        for i in range(self.n): # Drawing two cards
            if not self.folded[i]:
                self.card_players[i].append(self.draw_card())
                self.card_players[i].append(self.draw_card())

        self.sort_players_cards()


    def raise_bet(self, pid, value):
        value = max(0, value)
        value = min(value, self.money[pid])
        if self.whose_turn == pid and self.current_phase == RAISE:
            self.money[pid] -= value
            self.main_pot += value
            self.value_to_raise = value


    # Player's choice to accept raise
    def accept_bet(self, pid, value):
        if self.whose_turn_accept == pid and self.current_phase == ACCEPTING_RAISE:
            self.money[pid] -= value
            self.main_pot += value


    # Player's choice to skip the rest of the game
    def fold(self, pid):
        if self.whose_turn_accept == pid and self.current_phase == ACCEPTING_RAISE:
            self.folded[pid] = True 
            while len(self.card_players[pid]) > 0:
                self.drop_card(pid, self.card_players[pid][0])


    # Die similator
    def roll_die(self):
        return random.randint(1,6)


    # Shuffle phase (without random rolling part)    
    def shuffle_players_cards(self, pid):
        # TODO Shuffling wait or smth (pt 2)
        if self.whose_turn == pid and self.current_phase == SHUFFLE:
            taken_cards = []
            for i in range(self.n):
                if not self.folded[i]:
                    card = random.choice(self.card_players[i])
                    self.drop_card(i, card)
                    taken_cards.append(card)

            if LOG:
                print("Shuffling cards:")
                print(taken_cards)
            
            taken_cards = shuffle_deck(taken_cards)
            for i in range(self.n):
                if not self.folded[i]:
                    self.card_players[i].append(taken_cards[i])

            if LOG:
                print(taken_cards)

            self.sort_players_cards()
        

    # The final part of the game
    def show_game(self, pid):
        if self.whose_turn == pid and self.current_phase == SHOW:
            
            if LOG:
                print(self.card_players)
        
            # Bomb-outs
            for i in range(self.n):
                if self.folded[i]:
                    continue
                sum_cards = 0
                for (_, value) in self.card_players[i]:
                    sum_cards += value
                
                if sum_cards < (-1 * SABACC_VALUE) or sum_cards == 0 or sum_cards > SABACC_VALUE:
                    self.players_messages[i] = BOMB_OUT

            # Idiot's array
            idiots_array_cnt = 0
            for i in range(self.n):
                if self.folded[i]:
                    continue
                if self.players_messages[i] == BOMB_OUT:
                    continue
                
                zero_present = False
                two_present = False 
                three_present = False
                for (_, value) in self.card_players[i]:
                    if value == 0:
                        zero_present = True
                    elif value == 2:
                        two_present = True
                    elif value == 3:
                        three_present = True
                
                if zero_present and two_present and three_present:
                    idiots_array_cnt += 1
                    self.players_messages[i] = IDIOTS_ARRAY

            if idiots_array_cnt == 1:
                self.pay_prizes(IDIOTS_ARRAY)
                return 
            elif idiots_array_cnt > 1:
                self.run_sudden_demise(IDIOTS_ARRAY)
                self.pay_prizes(IDIOTS_ARRAY)
                return
            

            # Pure Sabacc
            pure_sabacc_cnt = 0
            for i in range(self.n):
                if self.folded[i]:
                    continue
                if self.players_messages[i] == BOMB_OUT:
                    continue

                sum_cards = 0
                for (_, value) in self.card_players[i]:
                    sum_cards += value
                
                if sum_cards == SABACC_VALUE:
                    pure_sabacc_cnt += 1
                    self.players_messages[i] = PURE_SABACC
            
            if pure_sabacc_cnt == 1:
                self.pay_prizes(PURE_SABACC)
                return 
            elif pure_sabacc_cnt > 1:
                self.run_sudden_demise(PURE_SABACC)
                self.pay_prizes(PURE_SABACC)
                return

            # Best cards
            best_cards_cnt = 0
            best_value = -100
            for i in range(self.n):
                if self.folded[i]:
                    continue
                if self.players_messages[i] == BOMB_OUT:
                    continue

                sum_cards = 0
                for (_, value) in self.card_players[i]:
                    sum_cards += value
                
                best_value = max(best_value, sum_cards)
            
            for i in range(self.n):
                if self.players_messages[i] == BOMB_OUT:
                    continue

                sum_cards = 0
                for (_, value) in self.card_players[i]:
                    sum_cards += value

                if sum_cards == best_value:
                    best_cards_cnt += 1
                    self.players_messages[i] = BEST_VALUE_WINNER
            
            if best_cards_cnt == 1:
                self.pay_prizes(BEST_VALUE_WINNER)
                return 
            elif best_cards_cnt > 1:
                self.run_sudden_demise(BEST_VALUE_WINNER)
                self.pay_prizes(BEST_VALUE_WINNER)
                return


    # Tie breaker 
    def run_sudden_demise(self, draw_type):
        print("# Sudden Demise #")
        self.current_phase = SUDDEN_DEMISE
        time.sleep(20)
        if LOG:
            print(self.players_messages)

        for i in range(self.n):
            if self.folded[i]:
                continue
            if self.players_messages[i] == draw_type:
                self.card_players[i].append(self.draw_card())

        if LOG:
            print(self.card_players)

        # Bomb-outs
        for i in range(self.n):
            if self.folded[i]:
                continue
            sum_cards = 0
            for (_, value) in self.card_players[i]:
                sum_cards += value
            
            if sum_cards < (-1 * SABACC_VALUE) or sum_cards == 0 or sum_cards > SABACC_VALUE:
                self.players_messages[i] = BOMB_OUT

        # Best cards
        best_value = -100
        for i in range(self.n):
            if self.folded[i]:
                continue
            if self.players_messages[i] == BOMB_OUT:
                continue

            sum_cards = 0
            for (_, value) in self.card_players[i]:
                sum_cards += value
            
            best_value = max(best_value, sum_cards)
        
        for i in range(self.n):
            if self.folded[i]:
                continue
            if self.players_messages[i] == BOMB_OUT:
                continue

            sum_cards = 0
            for (_, value) in self.card_players[i]:
                sum_cards += value

            if sum_cards < best_value:
                self.players_messages[i] = ""


    # Dealing money after the round
    def pay_prizes(self, win_type):
        winner_count = 0
        sabacc_pot_round = self.sabacc_pot
        self.sabacc_pot = 0
        main_pot_round = self.main_pot
        self.main_pot = 0

        for i in range(self.n):
            if self.folded[i]:
                continue
            if self.players_messages[i] == BOMB_OUT:
                self.sabacc_pot += min(main_pot_round // BOMB_RATIO, self.money[i])
                self.money[i] -= min(main_pot_round // BOMB_RATIO, self.money[i])
                
            elif self.players_messages[i] == win_type:
                winner_count += 1

        if win_type == BEST_VALUE_WINNER: # Sabacc pot goes to the next round
            self.sabacc_pot += sabacc_pot_round
            sabacc_pot_round = 0

        for i in range(self.n):
            if self.folded[i]:
                continue
            if self.players_messages[i] == win_type:
                self.money[i] += main_pot_round // winner_count + sabacc_pot_round // winner_count

        if winner_count == 0:
            self.main_pot = main_pot_round
        
        # Check if the caller won (TODO)


    # Drawing phase - extra card
    def draw_extra_card(self, pid):
        if self.whose_turn == pid and self.current_phase == DRAW:
            self.card_players[pid].append(self.draw_card())
            self.sort_players_cards()


    # Drawing phase - replacing card
    def replace_card(self, pid, card):
        if self.whose_turn == pid and self.current_phase == DRAW and len(self.card_players[pid]) > 2 and card in self.card_players[pid]:
            self.card_players[pid].remove(card)
            self.draw_extra_card(pid)


    # Copy to show to player client unit
    def client_copy(self, pid = -1):
        if self.current_phase == RESULTS or self.current_phase == SUDDEN_DEMISE:
            return self.full_copy()

        result = copy.deepcopy(self)

        for i in range(self.n):
            if i != pid:
                result.card_players[i] = [(BACK_CARD, None)] * len(result.card_players[i])
        
        result.discarded_cards = [(BACK_CARD, None)] * len(result.discarded_cards)
        result.cards = [(BACK_CARD, None)] * len(result.cards)
    
        return result


    # Full copy of the game
    def full_copy(self):
        return copy.deepcopy(self)

    # Printing current game status
    def pprint(self, indent = 0):
        d = self.__dict__
        for key, value in d.items():
            print('\t' * indent + str(key))
            print('\t' * (indent + 1) + str(value))

    def status(self):
        print("#### GAME STATUS ####")
        print(" vs ".join(self.players_names))
        print(self.money, f"Main pot = {self.main_pot}; Sabacc pot = {self.sabacc_pot}")
        print(self.card_players)
        print(self.current_phase, self.whose_turn, self.whose_turn_accept)
        mess_present = self.message != ""
        for ele in self.players_messages:
            mess_present = mess_present or ele != ""
        if mess_present:
            print(self.players_messages, self.message)
        print()



# g = SabaccGame(4)
# g.start_game()

# # Sudden Demise test for Game(2)
# # g.card_players = [[('Coin-ace', 15), ('Sabre-4', 4)], [('Coin-master', 14), ('Coin-5', 5)]]

# # Idiots Array test for Game(2)
# # g.card_players = [[('Sabre-3', 3), ("Idiot2", 0), ('Coin-2', 2)], [('Coin-master', 14), ('Flask-ace', 15)]]

# # Pure Sabacc test for Game(2)
# # g.card_players = [[('Sabre-6', 6), ('Sabre-8', 8), ('Coin-9', 9)], [('Coin-master', 14), ('Coin-5', 5)]]

# g.show_game(-1)
# print(g.players_messages)
# print("##################")
# g.pprint()


