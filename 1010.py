#!/usr/bin/env python3
from itertools import product
from pathlib import Path
import numpy as np
import pygame
import os


# основные используемые цвета
background_color = (100, 100, 100)
layout_color = (120, 120, 120)
lighter_color = (150, 150, 150)
text_color = (200, 200, 200)
colors = {
    # игровое поле и шрифт
    0: (170, 170, 170),
    # фигуры
    1: (230, 100, 100),
    2: (230, 210, 100),
    3: (210, 230, 100),
    4: (100, 230, 100),
    5: (100, 230, 210),
    6: (100, 210, 230),
    7: (100, 100, 230),
    8: (210, 100, 230),
    9: (230, 100, 200)
}

figures = [
    # коробки всех размеров
    np.array([[True] * 3, [True] * 3, [True] * 3]).T,
    np.array([[True, True], [True, True]]).T,
    np.array([[True]]).T,
    # # прямые линии
    np.array([[True] * 5]),
    np.array([[True] * 4]),
    np.array([[True] * 3]),
    np.array([[True] * 2]),
    # остальные фигуры
    np.array([[True, False, False], [True, False, False], [True, True, True]]),
    np.array([[True, False, False], [True, False, False], [True, True, False]]),
    np.array([[True, False], [True, True]]),
]

# сдвига начала координат
shift_pos = (10, 10)
# размер одного тайла
TILE_SIZE = 32
# сдвиги и пробелы между тайлами для отрисовки
TILE_SHIFT = 8
TILE_SKIP = 28
# размер корзины для фигур
MAX_BASKET_TILES = 5
# количество ячеек в корзине для фигур
MAX_BASKET_SIZE = 3
# размер игровой доски
BOARD_SIZE = 10

# идентификаторы кнопок мыши в pygame
LEFT_MOUSE = 1
RIGHT_MOUSE = 3

# координаты с корзинам с фигурами
basket_pos = [[x + shift_pos[0], TILE_SIZE * 11 + shift_pos[1]]
              for x in np.arange(0, 3 * MAX_BASKET_TILES * TILE_SIZE, TILE_SIZE * 6)]

# автоматический размер окна
game_width = basket_pos[2][0] + (basket_pos[1][0] - basket_pos[0][0]) - shift_pos[0]
game_height = TILE_SIZE * (BOARD_SIZE + MAX_BASKET_TILES + 2) + shift_pos[1] - shift_pos[1]


# gameover params
game_over_text = 'КОНЕЦ ИГРЫ'
gmx, gmy = len(game_over_text) * 30, 48
gmx_pos = ((game_width - gmx) // 2, (game_height - gmy) // 2)
rect1 = (gmx_pos[0] - 10, gmx_pos[1], gmx + 15, gmy + 13)
rect2 = (gmx_pos[0] - 5, gmx_pos[1] + 5, gmx + 5, gmy + 3)


def remove_zeros(arr):
    # находим строки и столбцы полностью пустые
    empty_cols, empty_rows = arr.sum(axis=0), arr.sum(axis=1)
    # и убираем их из текущей фигуры
    return arr[empty_rows != False, :][:, empty_cols != False]


def rotate(figure):
    # помещаем фигуру в квадрат side_size x side_size
    side_size = max(figure.shape)
    zeros = np.zeros((side_size, side_size), dtype=bool)
    zeros[:figure.shape[0], :figure.shape[1]] = figure
    figure = zeros
    # создаём новый массив повёрнутый на 90 градусов
    nf = np.empty(figure.shape, dtype=bool)
    for i in range(side_size):
        for j in range(side_size):
            nf[side_size - i - 1][j] = figure[j][i]
    return remove_zeros(nf)


def prepare_figures(figures):
    result = figures[:3]
    # генерируем все положения для линейных фигур (2 варианта)
    for figure in figures[3:][:4]:
        r_figure = rotate(figure)
        # INFO: не убирать .T (нужно для корректного отображения фигур)
        result += [remove_zeros(figure.T), r_figure.T]
    # генерируем угловые фигуры (4 варианта)
    for figure in figures[-3:]:
        # INFO: не убирать .T (нужно для корректного отображения фигур)
        result.append(remove_zeros(figure.T))
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
    circle = pygame.transform.smoothscale(
        circle, [int(min(rect.size) * radius)] * 2)
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

    def clear(self):
        self.cells = np.zeros((self.width, self.height))

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
        # проверка на выход из границ игрового поля
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
                rect = (shift_pos[0] + i * TILE_SIZE + TILE_SHIFT,
                        shift_pos[1] + j * TILE_SIZE + TILE_SHIFT, TILE_SKIP, TILE_SKIP)
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


board = Board(size_x=BOARD_SIZE, size_y=BOARD_SIZE)
figures = prepare_figures(figures)


class App:
    MAX_COUNTDOWN = 1
    GAME_FPS = 60

    def __init__(self, width=game_width, height=game_height):
        self.figure_drag = False
        self.figure_index = -1
        self.generate_figures()

        self.width = width
        self.height = height
        self._running = True
        self._display_surf = None
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.cwd = Path(os.path.dirname(os.path.abspath(__file__)))

        self.remove_animation = False
        self.remove_countdown = App.MAX_COUNTDOWN

        self.game_score = 0
        self.score_file = self.cwd / 'gamescore.txt'
        game_score_value = 0
        if self.score_file.exists():
            try:
                game_score_value = int(self.score_file.open('r').read())
            except ValueError:
                pass
        self.game_highscore = game_score_value
        self.lines = None

    def generate_figures(self):
        self.basket_figures = np.random.choice(figures, size=MAX_BASKET_SIZE)
        self.basket_colors = np.random.randint(1, len(colors), size=MAX_BASKET_SIZE)
        self.basket_count = 0

    def on_init(self):
        pygame.init()
        pygame.display.set_caption('1010')
        self._display_surf = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE)
        self._running = True

        path_to_font = str(self.cwd / 'resources' / 'FiraMono-Regular.ttf')
        self.font = pygame.font.Font(path_to_font, 20)
        self.bigfont = pygame.font.Font(path_to_font, 48)

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
                    self.figure_index = x // (game_width // MAX_BASKET_SIZE)
                    self.figure_drag = True
                elif self.figure_drag:
                    # проверка на вхождения xy в границы игрового поля
                    figure_in = x > shift_pos[0] and x < (shift_pos[0] + TILE_SIZE * board.width) and\
                        y > shift_pos[1] and y < (shift_pos[1] + TILE_SIZE * board.height)
                    if figure_in:
                        index_x = int(np.ceil((x - shift_pos[0] + TILE_SHIFT) / TILE_SIZE) - 1)
                        index_y = int(np.ceil((y - shift_pos[1] + TILE_SHIFT) / TILE_SIZE) - 1)
                        # можно ли установить фигуру на поле
                        if board.can_set((index_x, index_y), self.basket_figures[self.figure_index]):
                            self.game_score += int(self.basket_figures[self.figure_index].sum())
                            board.set(
                                (index_x, index_y),
                                self.basket_figures[self.figure_index],
                                color=self.basket_colors[self.figure_index])
                            # удаляем фигуру из ячейки корзины
                            self.basket_figures[self.figure_index] = np.array([[]])
                            self.basket_count += 1
                            # генерируем новые фигуры, если корзина пуста
                            if self.basket_count == MAX_BASKET_SIZE:
                                self.generate_figures()
                    self.figure_drag = False
                    self.figure_index = -1
                if self.game_over:
                    board.clear()
                    self.generate_figures()
                    self.game_highscore = max(self.game_score, self.game_highscore)
                    self.save_game_score()
                    self.game_over = False
                    self.game_score = 0

    def on_loop(self):
        if not self.remove_animation:
            # помещение блоков для анимации
            items = board.get_lines()
            if len(items) > 0:
                self.lines = items
                self.remove_animation = True
            if not self.game_over and not self.remove_animation:
                # проверка игры на проигрыш
                figure_cant_set = True
                for figure in self.basket_figures:
                    if not figure_cant_set:
                        break
                    if figure.sum() == 0:
                        continue
                    for x, y in product(range(board.width), range(board.height)):
                        if board.can_set((x, y), figure):
                            figure_cant_set = False
                            break
                if figure_cant_set:
                    self.game_over = True
        else:
            # реализация анимации удаления заполенной полосы
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
                self.remove_countdown = App.MAX_COUNTDOWN
            else:
                self.remove_countdown -= 1
        self.game_highscore = max(self.game_score, self.game_highscore)

    def on_render(self):
        # рисование подложки
        pygame.draw.rect(self._display_surf, background_color, (0, 0, self.width, self.height))

        # рисование основого игрового поля
        board.draw(self._display_surf)

        # рисование подложки для фигур
        for k in range(MAX_BASKET_SIZE):
            for j in range(MAX_BASKET_TILES):
                for i in range(MAX_BASKET_TILES):
                    rect = [shift_pos[0], shift_pos[1], TILE_SKIP, TILE_SKIP]
                    rect[0] += k * TILE_SIZE * (MAX_BASKET_TILES + 1) + i * TILE_SIZE + TILE_SHIFT
                    rect[1] += (board.height + 1) * TILE_SIZE + j * TILE_SIZE + TILE_SHIFT
                    AAfilledRoundedRect(self._display_surf, rect, layout_color)

        # рисование фигура в корзинах
        for index, (x, y) in enumerate(basket_pos):
            if index == self.figure_index:
                x, y = pygame.mouse.get_pos()
                x -= TILE_SIZE // 2
                y -= TILE_SIZE // 2
            for j, row in enumerate(self.basket_figures[index].T):
                for i, item in enumerate(row):
                    if item > 0:
                        rect = (x + i * TILE_SIZE + TILE_SHIFT, y + j *
                                TILE_SIZE + TILE_SHIFT, TILE_SKIP, TILE_SKIP)
                        AAfilledRoundedRect(
                            self._display_surf, rect, colors[self.basket_colors[index]])

        # вывод игровых очков
        text_pos = (TILE_SIZE * (board.width + 1), shift_pos[1] + 1)
        render_text = f'набранный рекорд\n{self.game_highscore}\nтекущий счёт\n{self.game_score}'
        draw_text(self._display_surf, self.font, text_color, text_pos, 30, render_text)
        if self.game_over:
            AAfilledRoundedRect(self._display_surf, rect1, colors[1], 0.2)
            AAfilledRoundedRect(self._display_surf, rect2, layout_color, 0.2)
            draw_text(self._display_surf, self.bigfont, text_color, gmx_pos, 0, game_over_text)

        pygame.display.flip()

    def save_game_score(self):
        self.score_file.open('w').write(str(self.game_highscore))

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
            self.clock.tick(App.GAME_FPS)
        self.save_game_score()
        self.on_cleanup()


if __name__ == '__main__':
    app = App()
    app.on_execute()
