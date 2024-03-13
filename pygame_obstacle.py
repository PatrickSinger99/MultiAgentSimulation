import pygame
from colors import *


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, position: (int, int), width: int, height: int):
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(grey)
        self.rect = self.image.get_rect()
        self.rect.topleft = position

