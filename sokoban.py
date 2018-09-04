#!/usr/bin/env python3
from pathlib import Path
import json as js
import pygame
import os


background_color = (100, 100, 100)
pole_size = (8, 8)
tile_size = 32
level = '1'

game_clock = 30
quit_flag = False
window_size = (tile_size * pole_size[0], tile_size * pole_size[1])

# mouse pressed key
LEFT_MOUSE = 1
RIGHT_MOUSE = 3

# tile indexes
TI_BACKGROUND = 0
TI_WALL = 1
TI_FLOOR = 2
TI_BOX = 3
TI_TARGET = 4
TI_PLAYER_RIGHT = 5
TI_PLAYER_UP = 6
TI_PLAYER_LEFT = 7
TI_PLAYER_DOWN = 8

CWD = Path(os.path.dirname(os.path.abspath(__file__)))


def draw_tile(img, xp, yp, index, size=tile_size):
    tile_rect = (size * index, 0, size, size)
    surface.blit(img, (x * size, yp * size), tile_rect)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Sokoban')
    clock = pygame.time.Clock()
    
    surface = pygame.Surface(window_size)
    surface.fill(background_color)

    tiles = pygame.image.load(str(CWD / 'resources' / 'sokoban.png'))
    game = js.load(open(CWD / 'resources' / 'sokoban_levels.json'))

    field = game[level]['field']
    player = [*game[level]['player'], TI_PLAYER_UP]
    boxes = game[level]['boxes']
    targets = game[level]['targets']

    while not quit_flag:
        surface.fill(background_color)

        # field
        for y, line in enumerate(field):
            for x, value in enumerate(line):
                draw_tile(tiles, x, y, value)
        # boxes
        for x, y in boxes:
            draw_tile(tiles, x, y, TI_BOX)

        # targets
        for x, y in targets:
            draw_tile(tiles, x, y, TI_TARGET)

        # player
        draw_tile(tiles, *player)

        # render
        screen.blit(surface, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_flag = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_flag = True
                if event.key == pygame.K_UP:
                    player[2] = TI_PLAYER_UP
                if event.key == pygame.K_DOWN:
                    player[2] = TI_PLAYER_DOWN
                if event.key == pygame.K_LEFT:
                    player[2] = TI_PLAYER_LEFT
                if event.key == pygame.K_RIGHT:
                    player[2] = TI_PLAYER_RIGHT

        clock.tick(game_clock)
