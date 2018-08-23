from enum import Enum
import numpy as np
import pygame

# флаг закрытия приложения
quit_flag = False
# флаг паузы игры
game_pause = False
# флаг конца игры
game_over = False

# используемые цвета
f_primary_color = (0, 0, 0)
f_background_color = (255, 130, 40)
f_pole_color = (200, 200, 200)

# цвет фона окна
background_color = (0x30, 0x50, 0x30)

# параметры фигруы
figure_size = 32
figure_center = figure_size // 2

# сдвиг координат от верхнего левого угла
figure_shift = (16, 16)

# размер поля (ширина, высота)
pole_size = (10, 20)

# размер боковой панели с информацией
side_info_size = 160

# размер окна (автоматический в зависимости от размера фигуры)
window_size = (pole_size[0] * figure_size + 2 * figure_shift[0] + side_info_size,
               pole_size[1] * figure_size + 2 * figure_shift[1])

# контур стакана
gamepole_box = [
    [figure_shift[0], figure_shift[1]],
    [figure_shift[0], figure_shift[0] + pole_size[1] * figure_size],
    [figure_shift[0] + pole_size[0] * figure_size, figure_shift[0] + pole_size[1] * figure_size],
    [figure_shift[0] + pole_size[0] * figure_size, figure_shift[0]],
]

# зависимость получаемых очков от количества линий
score_table = [0, 100, 300, 700, 1500]

# игровая статистика
game_score = 0
game_lines = 0
game_speed = 1
game_clock = 30
max_game_score = 0

# игровой шаг сдвига фигуры вниз
init_game_step = 30
game_step = init_game_step
# extra_moving = 30
fantom_lines_count = 0

figures = np.array([
    # I
    np.array([[1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.bool),
    # J
    np.array([
        [0, 1, 0],
        [0, 1, 0],
        [1, 1, 0],
    ], dtype=np.bool),
    # L
    np.array([[1, 0, 0], [1, 0, 0], [1, 1, 0]], dtype=np.bool),
    # O
    np.array([
        [1, 1],
        [1, 1],
    ], dtype=np.bool),
    # S
    np.array([[0, 1, 1], [1, 1, 0], [0, 0, 0]], dtype=np.bool),
    # T
    np.array([[0, 1, 0], [1, 1, 1], [0, 0, 0]], dtype=np.bool),
    # Z
    np.array([[1, 1, 0], [0, 1, 1], [0, 0, 0]], dtype=np.bool)
])


class Key(Enum):
    NONE = 0,
    LEFT = 1,
    RIGHT = 2,
    DOWN = 3


# нажатая кнопка
pressed_key = Key.NONE


class IS(Enum):
    NOT = 0,
    DOWN = 1,
    SIDE = 2


class HList:
    def __init__(self, size=0):
        self.list = [None] * size

    def push(self, item):
        self.list[0:-1] = self.list[1:]
        self.list[-1] = item

    def pop(self):
        return self.list[-1]


def remove_zeros(figure):
    # находим строки и столбцы полностью пустые
    empty_cols, empty_rows = figure.sum(axis=0), figure.sum(axis=1)
    # и убираем их из текущей фигуры
    return figure[empty_rows != False, :][:, empty_cols != False]


def draw_bbox(r, x, y, shift=None):
    if shift is not None:
        x += shift[0]
        y += shift[1]
    line_width = 4
    # набор координат внешней оболочки
    outer_box = [[x, y], [x, y + figure_size], [x + figure_size, y + figure_size], [x + figure_size, y]]
    # рисуем задник фигуры
    pygame.draw.rect(r, f_background_color, [x, y, figure_size, figure_size])
    # внешнюю оболочку
    pygame.draw.lines(r, f_primary_color, True, outer_box, line_width)
    # закрашиваем внутренний блок (не забываем про толщину внешнего блока)
    pygame.draw.rect(r, f_primary_color, [
        x + figure_center // 2 + line_width // 4, y + figure_center // 2 + line_width // 4, figure_center,
        figure_center
    ])


def draw_box(r, x, y, shift=None, color=None):
    if shift is not None:
        x += shift[0]
        y += shift[1]
    # набор координат коробки
    outer_box = [[x, y], [x, y + figure_size], [x + figure_size, y + figure_size], [x + figure_size, y]]
    # рисуем коробку
    pygame.draw.lines(r, color, True, outer_box, 1)


def rotate(figure, right=True):
    side_size = figure.shape[0]
    # создаём новый массив повёрнутый на 90 градусов (влево или вправо)
    nf = np.empty(figure.shape, dtype=np.bool)
    for i in range(side_size):
        for j in range(side_size):
            if right:
                nf[side_size - i - 1][j] = figure[j][i]
            else:
                nf[i][j] = figure[side_size - j - 1][i]
    return nf


def intersect(pole, figure, fx, fy, lx, ly):
    # игнорируем фигуру над стаканом
    if fy < 0:
        return IS.NOT
    # r_figure.T из-за представления игрового поля в памяти
    for iy, line in enumerate(r_figure.T):
        for ix, block in enumerate(line):
            # если оба блок в поле и блок фигуры не пустой, то есть столкновение
            if pole[fx + ix, fy + iy] and block:
                # if abs(fx - lx) > 0 and abs(fy - ly) > 0:
                #     return IS.SIDE
                # боковое стролкновение
                if abs(fx - lx) > 0:
                    return IS.SIDE
                # столкновение с нижней частью
                if abs(fy - ly) > 0:
                    return IS.DOWN
    return IS.NOT


def create_new_figure():
    # генерация новой фигуры
    figure = figures[np.random.randint(0, figures.shape[0])]
    # текущее положение фигуры
    fx, fy = pole_size[0] // 2 - 1, -3
    # старое положение фигуры
    lx, ly = pole_size[0] // 2 - 1, -3
    return (fx, fy, lx, ly), figure


def draw_text(r, font, color, position, shift_y, text):
    xp, yp = position
    # режем строку на блоки
    for line in text.split('\n'):
        # рисуем строку
        text = font.render(line, True, color)
        # переносим на отрисовочный слой
        surface.blit(text, (xp, yp))
        # переводим указатель на новую строку
        yp += shift_y


if __name__ == '__main__':
    # инициализация pygame
    pygame.init()
    # создание окна
    screen = pygame.display.set_mode(window_size)
    # установка названия окна
    pygame.display.set_caption('Tetris')
    # игровой таймер
    clock = pygame.time.Clock()
    # получаем стандартный шрифт
    font = pygame.font.Font('../resources/FiraMono-Regular.ttf', 25)
    # создание поверхности для рисования
    surface = pygame.Surface(window_size)

    # закрашивание задник в цвет фона
    surface.fill(background_color)

    # инициализация игрового поля
    pole = np.zeros(pole_size, dtype=np.bool)

    # инициализация фигуры
    # fx, fy -- текущее положение фигуры
    # lx, ly -- предыдущее положение фигуры
    # figure -- вид фигуры
    (fx, fy, lx, ly), figure = create_new_figure()
    fpx, fpy, lpx, lpy = fx, fy, lx, ly

    # основной цикл программы
    while not quit_flag:
        # обработка конца игры
        if game_over:
            print('NEW GAME')
            (fx, fy, lx, ly), figure = create_new_figure()
            fpx, fpy, lpx, lpy = fx, fy, lx, ly
            game_score, game_lines = 0, 0
            pole[:, :] = False
            game_over = False

        # убираем пустые линии в фигуре
        r_figure = remove_zeros(figure)
        # и запоминаем её размер
        s_figure = r_figure.shape

        #
        # отрисовка всех объектов
        #

        # отрисовка фона
        surface.fill(background_color)

        # отрисовка стакана
        pygame.draw.lines(surface, f_pole_color, False, gamepole_box, 2)

        # отрисовка блоков в стакане
        for ix, line in enumerate(pole):
            for iy, block in enumerate(line):
                if block:
                    # рисуем заполненный блок
                    draw_bbox(surface, ix * figure_size, iy * figure_size, shift=figure_shift)

        # отрисовка фигуры и фантома
        for ix, line in enumerate(r_figure):
            for iy, block in enumerate(line):
                if block:
                    draw_bbox(surface, (fx + ix) * figure_size, (fy + iy) * figure_size, shift=figure_shift)
                    draw_box(
                        surface, (lpx + ix) * figure_size, (lpy + iy) * figure_size,
                        shift=figure_shift,
                        color=f_pole_color)

        if game_pause:
            plot_text = f'HIGHSCORE\n{max_game_score}\n\nSCORE\n{game_score}\n\nLINES\n{game_lines}\n\nSPEED\n{game_speed}\n\n\nPAUSED'
        else:
            plot_text = f'HIGHSCORE\n{max_game_score}\n\nSCORE\n{game_score}\n\nLINES\n{game_lines}\n\nSPEED\n{game_speed}'
        # рендерим текст
        draw_text(surface, font, f_pole_color, (window_size[0] - side_info_size, figure_shift[1]), 2 * figure_shift[1],
                  plot_text)

        # отрисовка на экран
        screen.blit(surface, (0, 0))
        pygame.display.update()

        #
        # обработка событий и нажатии клавиш
        #
        for event in pygame.event.get():
            # проверяем на событие 'закрытие окна'
            if event.type == pygame.QUIT:
                quit_flag = True
            # обработка нажатия клавиш
            if event.type == pygame.KEYUP:
                pressed_key = Key.NONE
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_flag = True
                if event.key == pygame.K_p:
                    game_pause = not game_pause
                # сброс игры
                if event.key == pygame.K_r:
                    game_over = True
                if not game_pause:
                    # поворот фигуры
                    if event.key == pygame.K_SPACE:
                        figure = rotate(figure)
                        r_figure = remove_zeros(figure)
                        s_figure = r_figure.shape
                    # мгновенный спуск фигуры
                    if event.key == pygame.K_UP:
                        game_score += fantom_lines_count
                        fx, fy, lx, ly = lpx, lpy, lpx, lpy - 1
                    # БАГ: проход сквозь фигуру
                    # ПРИЧИНЫ: множественные нажатия
                    # РЕШЕНИЕ: делать проверку столкновений
                    if event.key == pygame.K_DOWN:
                        pressed_key = Key.DOWN
                    if event.key == pygame.K_LEFT:
                        pressed_key = Key.LEFT
                    if event.key == pygame.K_RIGHT:
                        pressed_key = Key.RIGHT

        #
        # обработка игрового цикла (следующий шаг)
        #

        if not game_pause:
            if game_step % 2 == 0:
                # обработка клавиш сдвига фигуры
                if pressed_key == Key.LEFT:
                    lx, ly = fx, fy
                    fx -= 1
                elif pressed_key == Key.RIGHT:
                    lx, ly = fx, fy
                    fx += 1
                elif pressed_key == Key.DOWN:
                    game_score += 1
                    lx, ly = fx, fy
                    fy += 1

            # игровой сдвиг фигуры
            if game_step == 0:
                game_step = init_game_step
                lx, ly = fx, fy
                fy += 1
            else:
                game_step -= 1

            # проверяем выход фигуры за границы (левую и правую)
            if fx < 0:
                fx = 0
            if fx + s_figure[0] > pole_size[0]:
                fx = pole_size[0] - s_figure[0]

            # проверяем столкновение
            intersect_r = intersect(pole, r_figure, fx, fy, lx, ly)

            # блокируем боковое столкновение
            # TODO: почти работает
            if intersect_r == IS.SIDE:
                fx = lx

            # столкновение/достижение дна фигурой
            if intersect_r == IS.DOWN or (fy + s_figure[1] == pole_size[1]):
                if intersect_r is IS.DOWN:
                    # поднимаем фигуру на предыдущее положение
                    fy = ly

                if fy <= 0:
                    game_over = True
                    continue

                # считаем количество очков за установку фигуры на поле
                game_score += r_figure.sum() * 2

                # переносим информацию на поле
                pole[fx:fx + s_figure[0], fy:fy + s_figure[1]] |= r_figure

                # инициализируем новую
                (fx, fy, lx, ly), figure = create_new_figure()

            # нахождение позиции фантомной фигуры
            fpx, fpy, lpx, lpy = fx, fy, lx, ly
            fantom_lines_count = 0
            for _ in range(pole_size[1] - fpy - s_figure[1] + 1):
                fantom_lines_count += 1
                lpx, lpy = fpx, fpy
                fpy += 1
                if fpy + s_figure[1] - 1 == pole_size[1]:
                    break
                intersect_r = intersect(pole, r_figure, fpx, fpy, lpx, lpy)
                if intersect_r == IS.DOWN:
                    break

            # убираем заполненные линии поля
            lines = pole.sum(axis=0)
            indexes = np.arange(pole_size[1])
            l_size = lines.shape[0]
            # количество одновременных линий
            lines_count = 0
            for index, line in zip(indexes, lines):
                if line == pole_size[0]:
                    # сдвигаем первые index блоков на 1 одну позицию вниз
                    pole[:, 1:index + 1:] = pole[:, :index:]
                    lines_count += 1

            # подсчёт очков и игровых линий
            game_lines += lines_count
            game_score += score_table[lines_count]

            # подсчёт максимально набранных очков
            max_game_score = max(max_game_score, game_score)

        # спим, чтобы не грузить проц
        clock.tick(game_clock)
