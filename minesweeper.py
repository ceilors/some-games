import numpy as np
import pygame

background_color = (0xc2, 0xd0, 0xe0)
pole_size = (10, 10)
tile_size = 32
game_clock = 30
quit_flag = False
game_over_flag = False
text_shift = (10, 6)
mines_count = 20
window_size = (pole_size[0] * tile_size, pole_size[1] * tile_size)

# game pole status
POLE_EMPTY = 0
POLE_CLOSED = 10
POLE_FLAG = 11
POLE_MINE = 12
# mouse pressed key
LEFT_MOUSE = 1
RIGHT_MOUSE = 3


class Game:
    def __init__(self, height, width, mines):
        self.height = height
        self.width = width
        self.mine_positions = set()
        while len(self.mine_positions) < mines:
            self.mine_positions.add((np.random.randint(0, width - 1), np.random.randint(0, height - 1)))
        self.mine_positions = np.array(list(self.mine_positions))

    def is_neighbour(self, v):
        if v[0] <= 1 and v[1] <= 1:
            return True
        return False

    def is_mine(self, x, y):
        for p in self.mine_positions:
            if p[0] == x and p[1] == y:
                return True
        return False

    def mines_count(self, x, y):
        dists = np.abs(self.mine_positions - np.array([x, y]))
        result = 0
        for d in dists:
            if self.is_neighbour(d):
                result += 1
        return result

    def __repr__(self):
        return self.mine_positions.__repr__()


def is_game_end(game, pole, pole_size):
    for y in range(pole_size[1]):
        for x in range(pole_size[0]):
            if pole[x, y] == POLE_CLOSED and not game.is_mine(x, y):
                return False
    return True


def new_game():
    game = Game(*pole_size, mines_count)
    pole = np.ones(pole_size, dtype='uint8') * 10
    game_over_flag = False
    return game, pole, game_over_flag


if __name__ == '__main__':
    # init game
    game = Game(*pole_size, mines_count)
    pole = np.ones(pole_size, dtype='uint8') * POLE_CLOSED

    pygame.init()
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption('Minesweeper')
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 32)
    surface = pygame.Surface(window_size)
    surface.fill(background_color)
    image = pygame.image.load('minesweeper.png')

    while not quit_flag:
        surface.fill(background_color)

        # draw pole
        for y in range(pole_size[1]):
            for x in range(pole_size[0]):
                font_draw = False
                # пустое поле
                if pole[x, y] == POLE_EMPTY:
                    tile_rect = (32, 0, 32, 32)
                # неоткрытое поле
                elif pole[x, y] == POLE_CLOSED:
                    tile_rect = (0, 0, 32, 32)
                # поставлен флаг
                elif pole[x, y] == POLE_FLAG:
                    tile_rect = (64, 0, 32, 32)
                # мины
                elif pole[x, y] == POLE_MINE:
                    tile_rect = (96, 0, 32, 32)
                elif pole[x, y] < POLE_CLOSED and pole[x, y] >= POLE_EMPTY:
                    tile_rect = (32, 0, 32, 32)
                    font_draw = True
                surface.blit(image, (x * tile_size, y * tile_size), tile_rect)
                if font_draw:
                    text = font.render(str(game.mines_count(x, y)), True, (0, 0, 0))
                    surface.blit(text, (x * tile_size + text_shift[0], y * tile_size + text_shift[1]))

        screen.blit(surface, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_flag = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_flag = True
                if event.key == pygame.K_r:
                    game, pole, game_over_flag = new_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over_flag:
                    game, pole, game_over_flag = new_game()
                # левая кнопка
                x, y = pygame.mouse.get_pos()
                x //= tile_size
                y //= tile_size
                # заменить числа на константы
                if event.button == LEFT_MOUSE:
                    mc = game.mines_count(x, y)
                    if game.is_mine(x, y):
                        for y in range(pole_size[1]):
                            for x in range(pole_size[0]):
                                if game.is_mine(x, y):
                                    pole[x, y] = POLE_MINE
                        print('game over')
                        game_over_flag = True
                    elif mc > 0:
                        pole[x, y] = mc
                    elif mc == 0:
                        visited = set()
                        queue = [(x, y)]
                        while queue:
                            x, y = queue.pop()
                            pole[x, y] = game.mines_count(x, y)
                            visited.add((x, y))
                            if game.mines_count(x, y) == 0:
                                for u, v in [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1), (x, y - 1), (x, y + 1),
                                             (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)]:
                                    if 0 <= u < pole_size[0] and 0 <= v < pole_size[1]:
                                        if not (u, v) in visited:
                                            queue.insert(0, (u, v))
                elif event.button == RIGHT_MOUSE:
                    if pole[x, y] == POLE_FLAG:
                        pole[x, y] = POLE_CLOSED
                    else:
                        pole[x, y] = POLE_FLAG

        if is_game_end(game, pole, pole_size):
            for y in range(pole_size[1]):
                for x in range(pole_size[0]):
                    if game.is_mine(x, y):
                        pole[x, y] = POLE_FLAG
            game_over_flag = True

        clock.tick(game_clock)
