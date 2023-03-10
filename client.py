import sys
import random
import pygame
import string
from move import *
from interface import *
from network import Network
import sabacc_game as sg

USER_TAG_LEN = 6

pygame.font.init()

width = 800
height = 600
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Sabacc Player")


def redrawWindow(win, game, p):
    pass


mem_status = None


def parse_mem(game: sg.SabaccGame):
    players_messages = []
    for player in game.players:
        players_messages.append(player.message)

    return (
        game.whose_turn,
        game.whose_turn_accept,
        game.current_phase,
        game.message,
        players_messages,
    )


def update_game(win, game: sg.SabaccGame, my_pid: int):
    global mem_status
    current_status = parse_mem(game)
    if mem_status == current_status:
        return
    mem_status = current_status
    game.status()
    # redrawWindows()


# Currenly used instead of GUI
def read_player_move(game: sg.SabaccGame, my_pid: int) -> Move:
    # TODO Do pygame interface
    if game.current_phase == sg.Phase.RAISE:
        print("Bet to raise (non-positive = skip)")
        value = int(input())
        return Move(my_pid, sg.Phase.RAISE, value)

    elif game.current_phase == sg.Phase.ACCEPTING_RAISE:
        print(f"Accept bet of [{game.value_to_raise}] (1 = Yes, 0 = Fold)")
        value = int(input())
        return Move(my_pid, sg.Phase.ACCEPTING_RAISE, value)

    elif game.current_phase == sg.Phase.SHUFFLE:
        print("Roll dice")
        input()
        return Move(my_pid, sg.Phase.SHUFFLE)

    elif game.current_phase == sg.Phase.SHOW:
        print("Show cards (1 = Show, 0 = Continue)")
        value = int(input())
        return Move(my_pid, sg.Phase.SHOW, value)

    elif game.current_phase == sg.Phase.RESULTS:
        # No moves here
        return Move(my_pid, sg.Phase.GET_BOARD)

    elif (
        game.current_phase == sg.Phase.SUDDEN_DEMISE
        or game.current_phase == sg.Phase.IDLE
    ):
        # No moves here
        return Move(my_pid, sg.Phase.GET_BOARD)

    elif game.current_phase == sg.Phase.DRAW:
        print("Draw new cards: (-1 = None, -2 = Extra Card, i = Index for card swap)")
        value = int(input())
        return Move(my_pid, sg.Phase.DRAW, value)

    else:
        print("Wrong command error", file=sys.stderr)
        game.status()
        exit()


def can_play_now(my_pid: int, game: sg.SabaccGame) -> bool:
    if game.current_phase in {sg.Phase.ACCEPTING_RAISE, sg.Phase.SHOW}:
        return game.whose_turn_accept == my_pid
    else:
        return game.whose_turn == my_pid


# Run with python client.py server_name port [username]
if __name__ == "__main__":
    clock = pygame.time.Clock()
    try:
        server: str = sys.argv[1]
        port = int(sys.argv[2])
        n = Network(server, port)
        my_pid: int = int(n.get_p())
    except:
        print("Error while connecting to the server")
        exit()

    if len(sys.argv) > 3:
        username = sys.argv[3]
    else:
        username = "Username" + "".join(random.sample(string.digits, USER_TAG_LEN))

    print(f"{username} - you are player: {my_pid}")

    while True:
        clock.tick(1)

        try:
            game: sg.SabaccGame = n.send(Move(my_pid, sg.Phase.GET_BOARD))
            if game.players[my_pid].name != username:
                game = n.send(Move(my_pid, sg.Phase.SET_NAME, username))
            print("Received: ", game)
            update_game(win, game, my_pid)
        except:
            print("Coudn't get game!")
            break

        if can_play_now(my_pid, game):
            # Update my move
            next_move = read_player_move(game, my_pid)
            game = n.send(next_move)
            update_game(win, game, my_pid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # pygame.quit()
                break
