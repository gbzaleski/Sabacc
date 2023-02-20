import pygame
from network import Network
import pickle
import sabacc_game as sg

pygame.font.init()

width = 800
height = 600
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Sabacc Player")