#!/usr/bin/env python3
from pathlib import Path
import numpy as np
import pygame
import os


background_color = (100, 100, 100)
pole_size = (12, 8)
tile_size = 64

game_clock = 30
quit_flag = False
window_size = (tile_size * pole_size[0], tile_size * pole_size[1])

# mouse pressed key
LEFT_MOUSE = 1
RIGHT_MOUSE = 3

CWD = Path(os.path.dirname(os.path.abspath(__file__)))


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Three in a row')
    clock = pygame.time.Clock()
    
    surface = pygame.Surface(window_size)
    surface.fill(background_color)
    tiles = pygame.image.load(str(CWD / 'resources' / 'tile.png'))

    while not quit_flag:
        # surface.fill(background_color)
        for y in range(pole_size[1]):
            for x in range(pole_size[0]):
                if (x + y) % 2 != 0:
                    tile_rect = (0, 0, tile_size, tile_size)
                else:
                    tile_rect = (tile_size, 0, tile_size, tile_size)
                surface.blit(tiles, (x * tile_size, y * tile_size), tile_rect)

        screen.blit(surface, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_flag = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_flag = True

        clock.tick(game_clock)
