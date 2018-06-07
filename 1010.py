import pygame


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

figures = [
    [
        [1, 1],
        [1, 0],
    ],
    [[1, 0], [1, 1]],
]

shift_pos = (10, 10)
TILE_SIZE = 32
TILE_SHIFT = 28


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
        self.cell = [[0 for _ in range(size_x)] for _ in range(size_y)]

    def set(self, pos, figure, color=1):
        width, height = len(figure[0]), len(figure)
        x_pos, y_pos = pos[0], pos[1]
        for y in range(y_pos, y_pos + height):
            for x in range(x_pos, x_pos + width):
                self.cell[y][x] = color * figure[y - y_pos][x - x_pos]

    def draw(self, display):
        for j, row in enumerate(self.cell):
            for i, item in enumerate(row):
                rect = (shift_pos[0] + i * TILE_SIZE + 8, shift_pos[1] + j * TILE_SIZE + 8, TILE_SHIFT, TILE_SHIFT)
                AAfilledRoundedRect(display, rect, colors[item])


board = Board()
board.set((1, 1), figures[0], color=9)
board.set((2, 2), figures[1], color=8)


class App:
    def __init__(self, x=100, y=100, width=640, height=480):
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

    def on_loop(self):
        pass

    def on_render(self):
        pygame.draw.rect(self._display_surf, (100, 100, 100), (0, 0, self.width, self.height))
        board.draw(self._display_surf)
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
