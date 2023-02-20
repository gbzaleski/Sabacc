import socket
from _thread import *
import pickle
import sys
import time
import sabacc_game as sg

SHUFFLE_THRESHOLD = 2

# value = Amount to raise
def run_raise(move):
    game.raise_bet(move.pid, move.value)
    game.current_phase = sg.ACCEPTING_RAISE

    game.whose_turn_accept = (game.whose_turn + 1) % game.n
    while game.folded[game.whose_turn_accept]:
        game.whose_turn_accept = (game.whose_turn_accept + 1) % game.n



def run_shuffle(move):
    # TODO Shuffling wait or smth (pt 1)
    die_value = game.roll_die()
    print("Rollled: ", die_value)

    if die_value <= SHUFFLE_THRESHOLD:
        game.shuffle_players_cards(move.pid)
    
    game.current_phase = sg.SHOW
    game.whose_turn_accept = (game.whose_turn + 1) % game.n
    while game.folded[game.whose_turn_accept]:
        game.whose_turn_accept = (game.whose_turn_accept + 1) % game.n


# 1 = Show, 0 = Continue
def run_show(move): 
    if move.value == 0:
        game.whose_turn_accept = (game.whose_turn_accept + 1) % game.n
        while game.folded[game.whose_turn_accept]:
            game.whose_turn_accept = (game.whose_turn_accept + 1) % game.n
        # Nobody called
        if game.whose_turn_accept == game.whose_turn: 
            game.whose_turn_accept = -1
            game.current_phase = sg.DRAW

    # Somebody calls
    elif move.value == 1:
        game.whose_turn_accept = -1
        game.current_phase = sg.RESULTS
        # Go back to receving info
        start_new_thread(run_results, (move.pid, ))
        
    else:
        print("Unknown command error at show", file=sys.stderr)
        exit() 


def run_results(pid):
    game.show_game(pid) # Contains run sudden demise and pay prizes
    print("Test long sleep after end") # TODO finish animation
    time.sleep(20)
    start_new_round()

def start_new_round():
    # TODO Add dealer starter
    
    # Prepare deck
    game.cards = game.cards + game.discarded_cards
    game.discarded_cards = []
    game.cards = sg.shuffle_deck(game.cards)

    game.start_game()

    game.whose_turn = 0
    game.current_phase = sg.RAISE
     

# -1 = None, -2 = Extra Card, i = Index for card swap
def run_draw_phase(move):
    if move.value >= 0 and move.value < len(game.card_players[move.pid]):
        game.replace_card(move.pid, game.card_players[move.pid][move.value])
    elif move.value == -2:
        game.draw_extra_card(move.pid)
    
    # Next player's turn
    game.current_phase = sg.RAISE
    game.whose_turn = (game.whose_turn + 1) % game.n
    while game.folded[game.whose_turn]:
        game.whose_turn = (game.whose_turn + 1) % game.n


# Accept bet (1 = Yes, 0 = Fold)   
def run_accepting_bets(move):
    if move.value == 1:
        game.accept_bet(move.pid, game.value_to_raise)
    else:
        game.fold(move.pid)

    game.whose_turn_accept = (game.whose_turn_accept + 1) % game.n
    while game.folded[game.whose_turn_accept]:
        game.whose_turn_accept = (game.whose_turn_accept + 1) % game.n

    # Everyone folded/paid
    if game.whose_turn_accept == game.whose_turn: 
        game.whose_turn_accept = -1
        game.current_phase = sg.SHUFFLE

    # Check if game finished
    not_folded_status = 0
    for fold_status in game.folded:
        if not fold_status:
            not_folded_status += 1


    if not_folded_status == 1:
        print("Everyone folded")
        game.message = "Everyone has folded - round concluded"
        game.current_phase = sg.IDLE
        #start_new_thread(auto_win)


def auto_win():
    time.sleep(10)
    # TODO: Execting and running this
    print("Paying main pot to the winner")
    
    
# Already satisfied fact that the move can be played
def play_move(move):
    if move.type == sg.RAISE:
        run_raise(move)
    elif move.type == sg.ACCEPTING_RAISE:
        run_accepting_bets(move)
    elif move.type == sg.SHUFFLE:
        run_shuffle(move)
    elif move.type == sg.SHOW:
        run_show(move)
    elif move.type == sg.RESULTS:
        print("Wrong command error results", file=sys.stderr)
        exit()
    elif move.type == sg.SUDDEN_DEMISE:
        print("Wrong command error sudden demise", file=sys.stderr)
        exit()
    elif move.type == sg.DRAW:
        run_draw_phase(move)
    else:
        print("Unknown command error", move, file=sys.stderr)
        exit()

    game.status()

def threaded_client(conn, pid):
    conn.send(str.encode(str(pid)))
    
    while True:
        try:
            #data = conn.recv(4096).decode()
            data = pickle.loads(conn.recv(4096))
            print(f"From player {pid}: {data}")

            if not data or data.pid != pid:
                print("Error while receiving data")
                break

            if data.type == sg.GET_BOARD: # Just request for update
                conn.send(pickle.dumps(game.client_copy(pid))) 
                continue

            # Correct update (normal turn)
            if data.type == game.current_phase and \
                ((game.whose_turn == pid and game.current_phase not in {sg.ACCEPTING_RAISE, sg.SHOW}) 
                or (game.whose_turn_accept == pid and game.current_phase in {sg.ACCEPTING_RAISE, sg.SHOW})):
                play_move(data)
            else: # Wrong moment for update
                pass 
            
            conn.send(pickle.dumps(game.client_copy(pid))) 
            
            #conn.sendall(pickle.dumps(game)) 
        except:
            break

# Run with python server.py server_name port [no_of_players] [starting_money] [minimal_bet]
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Run with python server.py server_name \
            port [no_of_players] [starting_money] [minimal_bet]")
        exit()

    try:
        server = sys.argv[1]
        port = int(sys.argv[2])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((server, port))
    except socket.error as err:
        print(err)
        exit()
    except:
        print("Error while setting up server")
        exit()

    if len(sys.argv) == 3:
        game = sg.SabaccGame()
    elif len(sys.argv) == 4:
        game = sg.SabaccGame(int(sys.argv[3]))
    elif len(sys.argv) == 5:
        game = sg.SabaccGame(int(sys.argv[3]), int(sys.argv[4]))
    else:
        game = sg.SabaccGame(int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))

    s.listen(game.n)
    print("Server started, waiting for players")
    
    for pid_count in range(game.n):
        _conn, addr = s.accept()
        print("Connected to: ", addr)

        if pid_count + 1 <  game.n:
            start_new_thread(threaded_client, (_conn, pid_count))
        else: # Last player
            start_new_round()
            threaded_client(_conn, pid_count) 
  
    

    