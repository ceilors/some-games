#!/usr/bin/env python3
from pathlib import Path
import json as js
import pygame
import os


background_color = (100, 100, 100)
pole_size = (8, 8)
tile_size = 32
level = 1

game_clock = 30
quit_flag = False
end_flag = False
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
    surface.blit(img, (xp * size, yp * size), tile_rect)


def do_move(player, field, boxes):
    directions = {
        TI_PLAYER_UP: (0, -1),
        TI_PLAYER_DOWN: (0, 1),
        TI_PLAYER_LEFT: (-1, 0),
        TI_PLAYER_RIGHT: (1, 0)
    }
    p_dir = directions[player[2]]
    p_x, p_y = player[0] + p_dir[0], player[1] + p_dir[1]
    if [p_x, p_y] in boxes:
        np_x = p_x + p_dir[0]
        np_y = p_y + p_dir[1]
        if field[np_y][np_x] != TI_WALL:
            player[0] = p_x
            player[1] = p_y
            boxes[boxes.index([p_x, p_y])] = [np_x, np_y]
    elif field[p_y][p_x] != TI_WALL:
        player[0] = p_x
        player[1] = p_y


def level_clear(boxes, targets):
    boxes = set(tuple(x) for x in boxes)
    targets = set(tuple(x) for x in targets)
    return not bool((targets - boxes))


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Sokoban')
    clock = pygame.time.Clock()

    surface = pygame.Surface(window_size)
    surface.fill(background_color)

    tiles = pygame.image.load(str(CWD / 'resources' / 'sokoban.png'))
    game = js.load(open(CWD / 'resources' / 'sokoban_levels.json'))

    field = game[str(level)]['field']
    player = [*game[str(level)]['player'], TI_PLAYER_UP]
    boxes = game[str(level)]['boxes']
    targets = game[str(level)]['targets']

    while not quit_flag:
        surface.fill(background_color)

        # field
        for y, line in enumerate(field):
            for x, value in enumerate(line):
                draw_tile(tiles, x, y, value)

        # targets
        for x, y in targets:
            draw_tile(tiles, x, y, TI_TARGET)

        # boxes
        for x, y in boxes:
            draw_tile(tiles, x, y, TI_BOX)

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
                    do_move(player, field, boxes)
                if event.key == pygame.K_DOWN:
                    player[2] = TI_PLAYER_DOWN
                    do_move(player, field, boxes)
                if event.key == pygame.K_LEFT:
                    player[2] = TI_PLAYER_LEFT
                    do_move(player, field, boxes)
                if event.key == pygame.K_RIGHT:
                    player[2] = TI_PLAYER_RIGHT
                    do_move(player, field, boxes)

        if level_clear(boxes, targets) and not end_flag:
            level += 1
            if game.get(str(level)):
                print(f'LEVEL {level-1} COMPLETE')
                field = game[str(level)]['field']
                player = [*game[str(level)]['player'], TI_PLAYER_UP]
                boxes = game[str(level)]['boxes']
                targets = game[str(level)]['targets']
            else:
                print('GAME END')
                end_flag = True

        clock.tick(game_clock)
