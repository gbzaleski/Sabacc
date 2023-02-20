import pygame
from network import Network
import pickle
import sabacc_game as sg
import sys
import time 
from move import *

pygame.font.init()

width = 800
height = 600
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Sabacc Player")

m_whose_turn = -1
m_whose_turn_accept = -1
m_current_phase = None

def redrawWindow(win, game, p):
    pass


def update_game(win, game : sg.SabaccGame, my_pid):
    global m_whose_turn, m_whose_turn_accept, m_current_phase
    if m_whose_turn == game.whose_turn \
        and m_whose_turn_accept == game.whose_turn_accept \
        and m_current_phase == game.current_phase:
        return 

    m_whose_turn = game.whose_turn
    m_whose_turn_accept = game.whose_turn_accept
    m_current_phase = game.current_phase
    game.status()
    # redrawWindows

def read_player_move(game, my_pid):
    # TODO Do pygame interface
    if game.current_phase == sg.RAISE:
        print("Bet to raise (non-positive = skip)")
        value = int(input())
        return Move(my_pid, sg.RAISE, value)
    
    elif game.current_phase == sg.ACCEPTING_RAISE:
        print("Wrong command error accept_raise", file=sys.stderr)
        exit()

    elif game.current_phase == sg.SHUFFLE:
        print("Roll dice")
        input()
        return Move(my_pid, sg.SHUFFLE)

    elif game.current_phase == sg.SHOW:
        print("Show cards (1 = Show, 0 = Continue)")
        value = int(input())
        return Move(my_pid, sg.SHOW, value)

    elif game.current_phase == sg.RESULTS:
        # No moves here
        return Move(my_pid, sg.GET_BOARD)

    elif game.current_phase == sg.SUDDEN_DEMISE:
        # No moves here
        return Move(my_pid, sg.GET_BOARD)

    elif game.current_phase == sg.DRAW:
        print("Draw new cards: (-1 = None, -2 = Extra Card, i = Index for card swap)")
        value = int(input())
        return Move(my_pid, sg.DRAW, value)

    else:
        print("Wrong command error", file=sys.stderr)
        exit()


# Run with python client.py server_name port [username]
if __name__ == "__main__":
    run = True
    clock = pygame.time.Clock()
    n = Network("localhost", 5555)
    my_pid = int(n.get_p())

    print("You are player: ", my_pid)

    while run:
        clock.tick(1)

        try:
            game = n.send(Move(my_pid, sg.GET_BOARD))
            print("Received: ", game)
            update_game(win, game, my_pid)
        except:
            run = False
            print("Coudn't get game!")
            break

        if (game.whose_turn == my_pid and game.current_phase not in {sg.ACCEPTING_RAISE, sg.SHOW}) \
            or (game.whose_turn_accept == my_pid and game.current_phase in {sg.ACCEPTING_RAISE, sg.SHOW}):
            # Update my move
            next_move = read_player_move(game, my_pid)
            game = n.send(next_move)
            update_game(win, game, my_pid)
            pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                #pygame.quit()
                
        
