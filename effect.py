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


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Effect test')
    clock = pygame.time.Clock()

    surface = pygame.Surface(window_size)
    surface.fill(background_color)

    image = np.array(Image.open('./resources/image.png').convert('RGB')).reshape(IMG_SIZE ** 2, 3)
    effect = np.array(Image.open('./resources/effect.png').convert('L')).reshape(IMG_SIZE ** 2)

    while not quit_flag:
        surface.fill(background_color)

        indexes = np.where(effect <= color_range)
        result = np.array(image, copy=True)
        result[indexes] = [0, 0, 0]
        result = result.reshape((IMG_SIZE, IMG_SIZE, 3))
        result = result.transpose((1, 0, 2))

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

        clock.tick(game_clock)
