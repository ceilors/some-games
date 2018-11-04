#!/usr/bin/env python3
from PIL import Image
import numpy as np
import pygame


background_color = (100, 100, 100)
window_size = (500, 500)
game_clock = 60
quit_flag = False
color_range = 0
incrementer = 1
IMG_SIZE = 500


def effect_from_image(image):
    effect = np.array(Image.open(image).convert('L')).reshape(-1)

    def function(img, t):
        indexes = np.where(effect <= t)
        result = np.array(img, copy=True)
        result[indexes] = [0, 0, 0]
        result = result.reshape((IMG_SIZE, IMG_SIZE, 3))
        return result.transpose((1, 0, 2))

    return function


def effect_tiles(tile_size=50, img_size=IMG_SIZE):
    steps = 2 * img_size // tile_size
    effect = np.zeros((IMG_SIZE, IMG_SIZE))
    for x in range(effect.shape[0]):
        for y in range(effect.shape[1]):
            effect[x, y] = (1 + x // tile_size + y // tile_size) / steps * 255
    effect = effect.reshape(-1)

    def function(img, t):
        indexes = np.where(effect <= t)
        result = np.array(img, copy=True)
        result[indexes] = [0, 0, 0]
        result = result.reshape((IMG_SIZE, IMG_SIZE, 3))
        return result.transpose((1, 0, 2))

    return function


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Effect test')
    clock = pygame.time.Clock()

    surface = pygame.Surface(window_size)
    surface.fill(background_color)

    image = np.array(Image.open('./resources/image.png').convert('RGB')).reshape(IMG_SIZE ** 2, 3)
    effects = [effect_from_image(f'./resources/effect.png'), effect_tiles()]
    effect_index = 0

    while not quit_flag:
        surface.fill(background_color)

        result = effects[effect_index](image, color_range)

        color_range += incrementer
        if color_range >= 255:
            incrementer = -1
        if color_range <= 0:
            incrementer = 1

        pygame.surfarray.blit_array(surface, result)

        # render
        screen.blit(surface, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_flag = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_flag = True
                if event.key == pygame.K_LEFT:
                    color_range = 0
                    incrementer = 1
                    effect_index -= 1
                    if effect_index < 0:
                        effect_index = 0
                if event.key == pygame.K_RIGHT:
                    color_range = 0
                    incrementer = 1
                    effect_index += 1
                    if effect_index >= len(effects):
                        effect_index = len(effects) - 1

        clock.tick(game_clock)
