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


current_player = -1
current_phase = None

def redrawWindow(win, game, p):
    pass



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
        except:
            run = False
            print("Coudn't get game!")
            break

        if game.whose_turn == my_pid:
            # Update my move
            pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                #pygame.quit()
                
        redrawWindow(win, game, my_pid)   
