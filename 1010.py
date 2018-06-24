#!/usr/bin/env python3
import pygame
import numpy as np

colors = {
    0: (200, 200, 200),
    1: (255, 206, 55),
    2: (232, 155, 50),
    3: (255, 129, 68),
    4: (232, 69, 56),
    5: (255, 100, 190),
    6: (190, 88, 255),
    7: (104, 101, 232),
    8: (101, 186, 255),
    9: (62, 232, 210),
}

game_width = 500
game_height = 500

figures = [np.array([[1, 1], [1, 1]]), np.array([[1, 1], [0, 1]]), np.array([[1] * 5])]
figures = np.array([figure.T for figure in figures])

shift_pos = (10, 10)
TILE_SIZE = 32
TILE_SHIFT = 28

# mouse pressed key
LEFT_MOUSE = 1
RIGHT_MOUSE = 3

# координаты с корзинам с фигурами
basket_pos = [[x, game_height - game_height // 3] for x in np.arange(0, game_width, game_width / 3)]


def AAfilledRoundedRect(surface, rect, color, radius=0.2):
    """
    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect, color = pygame.Rect(rect), pygame.Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0, 0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)
    circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)
    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)
    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))
    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)
    return surface.blit(rectangle, pos)


class Board:
    def __init__(self, size_x=10, size_y=10):
        self.cells = np.zeros((size_y, size_y))

    def set(self, pos, figure, color=1):
        width, height = len(figure), len(figure[0])
        x_pos, y_pos = pos[0], pos[1]
        for y in range(y_pos, y_pos + height):
            for x in range(x_pos, x_pos + width):
                self.cells[y, x] = color * figure[x - x_pos][y - y_pos]

    def can_set(self, pos, figure):
        width, height = len(figure), len(figure[0])
        x_pos, y_pos = pos[0], pos[1]
        for y in range(y_pos, y_pos + height):
            for x in range(x_pos, x_pos + width):
                if self.cells[y, x] != 0:
                    return False
        return True

    def draw(self, display):
        for j, row in enumerate(self.cells):
            for i, item in enumerate(row):
                rect = (shift_pos[0] + i * TILE_SIZE + 8, shift_pos[1] + j * TILE_SIZE + 8, TILE_SHIFT, TILE_SHIFT)
                AAfilledRoundedRect(display, rect, colors[item])

    def get_lines(self):
        items = []
        for row in self.cells:
            if np.all(row > 0):
                items.append(row)
        for col in self.cells.T:
            if np.all(col > 0):
                items.append(col)
        return items


board = Board()


class App:
    def __init__(self, x=100, y=100, width=game_width, height=game_height):
        self.figure_drag = False
        self.figure_index = -1
        self.basket_count = 0
        self.basket_figures = np.random.choice(figures, size=3)
        self.basket_colors = np.random.randint(1, 9 + 1, size=3)
        self.width = width
        self.height = height
        self.x, self.y = x, y
        self._running = True
        self._display_surf = None

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE)
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == LEFT_MOUSE:
                x, y = pygame.mouse.get_pos()
                if not self.figure_drag and y >= basket_pos[0][1]:
                    self.figure_index = x // (game_width // 3)
                    self.figure_drag = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == LEFT_MOUSE:
                x, y = pygame.mouse.get_pos()
                figure_in = x > shift_pos[0] and x < (shift_pos[0] + TILE_SIZE * 10) and\
                    y > shift_pos[1] and y < (shift_pos[1] + TILE_SIZE * 10)
                if figure_in:
                    index_x = int(np.ceil((x - shift_pos[0] + 8) / TILE_SIZE) - 1)
                    index_y = int(np.ceil((y - shift_pos[1] + 8) / TILE_SIZE) - 1)
                    if board.can_set((index_x, index_y), self.basket_figures[self.figure_index]):
                        board.set(
                            (index_x, index_y), self.basket_figures[self.figure_index], color=self.basket_colors[self.figure_index])
                        self.basket_figures[self.figure_index] = np.array([[]])
                        self.basket_count += 1
                        if self.basket_count == 3:
                            self.basket_figures = np.random.choice(figures, size=3)
                            self.basket_colors = np.random.randint(1, 9 + 1, size=3)
                            self.basket_count = 0
                self.figure_drag = False
                self.figure_index = -1

    def on_loop(self):
        for item in board.get_lines():
            item[:] = 0

    def on_render(self):
        pygame.draw.rect(self._display_surf, (100, 100, 100), (0, 0, self.width, self.height))
        board.draw(self._display_surf)
        for index, (x, y) in enumerate(basket_pos):
            if index == self.figure_index:
                x, y = pygame.mouse.get_pos()
                x -= TILE_SIZE // 2
                y -= TILE_SIZE // 2
            for j, row in enumerate(self.basket_figures[index].T):
                for i, item in enumerate(row):
                    if item > 0:
                        rect = (x + i * TILE_SIZE + 8, y + j * TILE_SIZE + 8, TILE_SHIFT, TILE_SHIFT)
                        AAfilledRoundedRect(self._display_surf, rect, colors[self.basket_colors[index]])
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self._running = False
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == '__main__':
    app = App()
    app.on_execute()
