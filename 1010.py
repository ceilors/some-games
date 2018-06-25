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

figures = [
    # all boxes
    np.array([[True] * 3, [True] * 3, [True] * 3]).T,
    np.array([[True, True], [True, True]]).T,
    np.array([[True]]).T,
    # all lines
    np.array([[True] * 5]),
    np.array([[True] * 4]),
    np.array([[True] * 3]),
    np.array([[True] * 2]),
    # others
    np.array([[True, False, False], [True, False, False], [True, True, True]]),
    np.array([[True, False, False], [True, False, False], [True, True, False]]),
    np.array([[True, False], [True, True]]),
]

shift_pos = (10, 10)
TILE_SIZE = 32
TILE_SHIFT = 28

# mouse pressed key
LEFT_MOUSE = 1
RIGHT_MOUSE = 3

# координаты с корзинам с фигурами
basket_pos = [[x, game_height - TILE_SIZE * 5] for x in np.arange(0, game_width, game_width / 3)]


def rotate(figure, right=True):
    side_size = figure.shape[0]
    # создаём новый массив повёрнутый на 90 градусов (влево или вправо)
    nf = np.empty(figure.shape, dtype=np.bool)
    for i in range(side_size):
        for j in range(side_size):
            nf[side_size - i - 1][j] = figure[j][i]
    # находим строки и столбцы полностью пустые
    empty_cols, empty_rows = nf.sum(axis=0), nf.sum(axis=1)
    # и убираем их из текущей фигуры
    return nf[empty_rows != False, :][:, empty_cols != False]


def prepare_figures(figures):
    result = []
    # rotate lines
    for figure in figures[3:][:4]:
        r_figure = rotate(figure)
        # INFO: don't remove .T (for correct placement)
        result += [figure.T, r_figure.T]
    # rotate last figures
    for figure in figures[-3:]:
        # INFO: don't remove .T (for correct placement)
        result.append(figure.T)
        for _ in range(3):
            figure = rotate(figure)
            result.append(figure.T)
    return result


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


def draw_text(r, font, color, position, shift_y, text):
    xp, yp = position
    # режем строку на блоки
    for line in text.split('\n'):
        # рисуем строку
        text = font.render(line, True, color)
        # переносим на отрисовочный слой
        r.blit(text, (xp, yp))
        # переводим указатель на новую строку
        yp += shift_y


class Board:
    def __init__(self, size_x=10, size_y=10):
        self.width = size_x
        self.height = size_y
        self.cells = np.zeros((size_y, size_y))

    def set(self, pos, figure, color=1):
        width, height = len(figure), len(figure[0])
        x_pos, y_pos = pos[0], pos[1]
        for y in range(y_pos, y_pos + height):
            for x in range(x_pos, x_pos + width):
                if figure[x - x_pos][y - y_pos]:
                    self.cells[y, x] = color * figure[x - x_pos][y - y_pos]

    def can_set(self, pos, figure):
        width, height = len(figure), len(figure[0])
        x_pos, y_pos = pos[0], pos[1]
        pole_cond = x_pos >= 0 and x_pos + width <= self.width and\
            y_pos >= 0 and y_pos + height <= self.height
        if not pole_cond:
            return False
        for y in range(y_pos, y_pos + height):
            for x in range(x_pos, x_pos + width):
                if self.cells[y, x] * figure[x - x_pos, y - y_pos] != 0:
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
figures = prepare_figures(figures)


class App:
    MAX_COUNDOWN = 5

    def __init__(self, width=game_width, height=game_height):
        self.figure_drag = False
        self.figure_index = -1
        self.basket_count = 0
        self.basket_figures = np.random.choice(figures, size=3)
        self.basket_colors = np.random.randint(1, 9 + 1, size=3)
        self.width = width
        self.height = height
        self._running = True
        self._display_surf = None
        self.remove_animation = False
        self.remove_countdown = App.MAX_COUNDOWN
        self.game_score = 0
        self.lines = None

    def on_init(self):
        pygame.init()
        pygame.display.set_caption('1010')
        self._display_surf = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE)
        self.font = pygame.font.Font(None, 36)
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._running = False
        if self.remove_animation:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == LEFT_MOUSE:
                x, y = pygame.mouse.get_pos()
                if not self.figure_drag and y >= basket_pos[0][1]:
                    self.figure_index = x // (game_width // 3)
                    self.figure_drag = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == LEFT_MOUSE:
                x, y = pygame.mouse.get_pos()
                figure_in = x > shift_pos[0] and x < (shift_pos[0] + TILE_SIZE * board.width) and\
                    y > shift_pos[1] and y < (shift_pos[1] + TILE_SIZE * board.height)
                if figure_in:
                    index_x = int(np.ceil((x - shift_pos[0] + 8) / TILE_SIZE) - 1)
                    index_y = int(np.ceil((y - shift_pos[1] + 8) / TILE_SIZE) - 1)
                    if board.can_set((index_x, index_y), self.basket_figures[self.figure_index]):
                        self.game_score += self.basket_figures[self.figure_index].sum()
                        board.set(
                            (index_x, index_y),
                            self.basket_figures[self.figure_index],
                            color=self.basket_colors[self.figure_index])
                        self.basket_figures[self.figure_index] = np.array([[]])
                        self.basket_count += 1
                        if self.basket_count == 3:
                            self.basket_figures = np.random.choice(figures, size=3)
                            self.basket_colors = np.random.randint(1, 9 + 1, size=3)
                            self.basket_count = 0
                self.figure_drag = False
                self.figure_index = -1

    def on_loop(self):
        # remove animation
        if not self.remove_animation:
            items = board.get_lines()
            if len(items) > 0:
                self.lines = items
                self.remove_animation = True
        else:
            if self.remove_countdown == 0:
                all_clear = True
                for item in self.lines:
                    if item.sum() > 0:
                        all_clear = False
                    item[item.astype('bool').argmax()] = 0
                    self.game_score += 1
                if all_clear:
                    self.remove_animation = False
                    self.lines = None
                self.remove_countdown = App.MAX_COUNDOWN
            else:
                self.remove_countdown -= 1

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
        text_pos = (TILE_SIZE * (board.width + 1), 10)
        text_color = (200, 200, 200)
        draw_text(self._display_surf, self.font, text_color, text_pos, 30, f'game score\n{self.game_score}')
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
