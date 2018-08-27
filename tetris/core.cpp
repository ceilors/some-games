#include "core.hpp"

// simple random
static uint8_t y8 = (uint8_t)time(NULL);

static uint8_t tile_size = 16;

uint8_t xorshift8(void) {
    y8 ^= (y8 << 7);
    y8 ^= (y8 >> 5);
    return y8 ^= (y8 << 3);
}

uint8_t & Field::operator () (uint8_t x, uint8_t y) {
    if (x < _width && y < _height) {
        return field[y * _width + x];
    } else {
        throw std::out_of_range("index out of range");
    }
}

void Field::set(Figure * f) {
    for (figure_t::iterator it = f->coords.begin(); it != f->coords.end(); ++it) {
        (*this)(it->x + f->pos.x, it->y + f->pos.y) = f->color + 1;
    }
}

bool Field::intersect(Figure * f) {
    // достижение дна
    for (figure_t::iterator it = f->coords.begin(); it != f->coords.end(); ++it) {
        // пересечение с фигурой
        try {
            if ((*this)(it->x + f->pos.x, it->y + f->pos.y)) {
                return true;
            }
        } catch (std::out_of_range &) { return true; }
    }
    return false;
}

void Field::clear_line(uint8_t index) {
    for (uint8_t y = index + 1; y < _height; ++y) {
        for (uint8_t x = 1; x < _width - 1; ++x) {
            (*this)(x, y - 1) = (*this)(x, y);
        }
    }
}

bool Field::check_line(uint8_t index) {
    uint8_t filled = 0;
    for (uint8_t x = 0; x < _width; ++x) {
        uint8_t value = 1 ? (*this)(x, index) > 0 : 0;
        filled += value;
    }
    return filled == _width;
}

void Field::clear() {
    for (std::vector<uint8_t>::iterator i = field.begin(); i != field.end(); ++i) {
        *i = 0;
    }
    for (uint8_t y = 0; y < _height; ++y) {
        (*this)(0, y) = 1;
        (*this)(_width - 1, y) = 1;
    }
    for (uint8_t x = 0; x < _width; ++x) {
        (*this)(x, 0) = 1;
    }
}

void Figure::set(uint8_t figure, uint8_t w, uint8_t h) {
    x_max = y_max = 0;
    color = figure + 1;
    coords.clear();
    switch (figure) {
        case FIGURE_I:
            coords.push_back(point(0, 0));
            coords.push_back(point(1, 0));
            coords.push_back(point(2, 0));
            coords.push_back(point(3, 0));
            break;
        case FIGURE_J:
            coords.push_back(point(0, 0));
            coords.push_back(point(0, 1));
            coords.push_back(point(1, 1));
            coords.push_back(point(2, 1));
            break;
        case FIGURE_L:
            coords.push_back(point(2, 0));
            coords.push_back(point(0, 1));
            coords.push_back(point(1, 1));
            coords.push_back(point(2, 1));
            break;
        case FIGURE_O:
            coords.push_back(point(0, 0));
            coords.push_back(point(0, 1));
            coords.push_back(point(1, 0));
            coords.push_back(point(1, 1));
            break;
        case FIGURE_S:
            coords.push_back(point(0, 0));
            coords.push_back(point(0, 1));
            coords.push_back(point(1, 1));
            coords.push_back(point(1, 2));
            break;
        case FIGURE_T:
            coords.push_back(point(1, 0));
            coords.push_back(point(0, 1));
            coords.push_back(point(1, 1));
            coords.push_back(point(2, 1));
            break;
        case FIGURE_Z:
            coords.push_back(point(1, 0));
            coords.push_back(point(0, 1));
            coords.push_back(point(1, 1));
            coords.push_back(point(0, 2));
            break;
        default:
            throw std::invalid_argument("invalid figure index");
    }
    for (figure_t::iterator it = coords.begin(); it != coords.end(); ++it) {
        x_max = std::max(it->x, x_max);
        y_max = std::max(it->y, y_max);
    }
    pos = point((w - x_max) / 2, h - y_max);
}

void Figure::rotate(bool direction) {
    int8_t max_x = x_max;
    int8_t mx = max_x;
    int8_t my = max_x;
    // rotate
    for (figure_t::iterator it = coords.begin(); it != coords.end(); ++it) {
        int8_t x = it->x;
        int8_t y = it->y;
        if (direction) {
            it->x = max_x - y;
            it->y = x;
        } else {
            it->x = y;
            it->y = max_x - x;
        }
        mx = std::min(it->x, mx);
        my = std::min(it->y, my);
    }
    // shift
    for (figure_t::iterator it = coords.begin(); it != coords.end(); ++it) {
        it->x -= mx;
        it->y -= my;
    }
    // x & y maxs
    for (figure_t::iterator it = coords.begin(); it != coords.end(); ++it) {
        x_max = std::max(it->x, x_max);
        y_max = std::max(it->y, y_max);
    }
}

void Tetris::gameover() {
    field.clear();
    curr.set(xorshift8() % (FIGURE_Z + 1), field.width(), field.height() - 1);
    next.set(xorshift8() % (FIGURE_Z + 1), field.width(), field.height() - 1);
}

void Tetris::move(uint8_t direction) {
    const uint8_t time_to_set_default = 2;
    static uint8_t time_to_set = time_to_set_default;
    point _shifts[] = {point(-1, 0), point(1, 0), point(0, -1), point(0, 1)};
    figure_t shifts(_shifts, _shifts+4);
    bool set_flag = false;

    switch (direction) {
        case MOVE_LEFT: {
            curr.pos.x--;
            if (field.intersect(&curr)) {
                curr.pos.x++;
            }
            break;
        }
        case MOVE_RIGHT: {
            curr.pos.x++;
            if (field.intersect(&curr)) {
                curr.pos.x--;
            }
            break;
        }
        case MOVE_SOFT_DOWN: {
            curr.pos.y--;
            if (field.intersect(&curr)) {
                curr.pos.y++;
                set_flag = true;
            }
            break;
        }
        case MOVE_HARD_DOWN: {
            Figure t = curr;
            while (!field.intersect(&t)) {
                t.pos.y--;
            }
            curr.pos.y = t.pos.y + 1;
            set_flag = true;
            time_to_set = 0;
            break;
        }
        case ROTATE_LEFT:
        case ROTATE_RIGHT: {
            bool side = true ? direction == ROTATE_LEFT : false;
            bool ignored_all = true;
            curr.rotate(side);
            if (field.intersect(&curr)) {
                for (int8_t k = 1; k <= std::max(curr.x_max, curr.y_max); ++k) {
                    for (figure_t::iterator it = shifts.begin(); it != shifts.end(); ++it) {
                        point s = (*it);
                        curr.pos.x += s.x * k;
                        curr.pos.y += s.y * k;
                        if (!field.intersect(&curr)) {
                            ignored_all = false;
                            break;
                        } else {
                            curr.pos.x -= s.x * k;
                            curr.pos.y -= s.y * k;
                        }
                    }
                    if (!ignored_all) {
                        break;
                    }
                }
                if (ignored_all) {
                    curr.rotate(!side);
                }
            }
            break;
        }
        default:
            throw std::invalid_argument("invalid figure action");
    }
    if (set_flag && time_to_set == 0) {
        time_to_set = time_to_set_default;
        try {
            field.set(&curr);
        } catch (std::out_of_range &) {
            std::cout << "gameover" << std::endl;
            gameover();
            return;
        }
         curr = next;
         next.set(xorshift8() % (FIGURE_Z + 1), field.width(), field.height() - 1);
         // очистка заполненных ячеек поля
         for (int index = field.height() - 1; index >= 1; --index) {
             // здесь можно запилить подсчёт очков
             if (field.check_line((uint8_t)index)) {
                 field.clear_line((uint8_t)index);
             }
         }
         // проверяем что фигуре ничего не мешает
         if (field.intersect(&curr)) {
            std::cout << "gameover" << std::endl;
            gameover();
            return;
         }
    } else if (set_flag) {
        time_to_set--;
    }
}

Tetris::Tetris(SDL_Renderer * r) {
    tile = IMG_LoadTexture(r, "../resources/tetris_block.png");
    gameover();
}

Tetris::~Tetris() {
    SDL_DestroyTexture(tile);
}

void draw_box(SDL_Renderer * r, SDL_Texture * tex, int8_t x, int8_t y, uint8_t id) {
    SDL_Rect wnd = { id * tile_size, 0, tile_size, tile_size };
    SDL_Rect pos = { x * tile_size, y * tile_size, tile_size, tile_size };
    SDL_RenderCopy( r, tex, &wnd, &pos );
}

void Tetris::render(SDL_Renderer * r) {
    const int8_t next_figure_shift = field.width() + 1;

    // сдвигаем точку отчёта для оси y для человеческой отрисовки
    // рисуем текущую фигуру на поле
    for (figure_t::iterator it = curr.coords.begin(); it != curr.coords.end(); ++it) {
        draw_box(r, tile, it->x + curr.pos.x, field.height() - (it->y + curr.pos.y) - 1, curr.color);
    }
    // следующая фигура
    for (figure_t::iterator it = next.coords.begin(); it != next.coords.end(); ++it) {
        draw_box(r, tile, it->x + next_figure_shift, next.y_max - it->y + 1, next.color);
    }
    // рисуем игровое поле
    for (int8_t y = 0; y < field.height(); ++y) {
        for (int8_t x = 0; x < field.width(); ++x) {
            uint8_t tile_type = field(x, y);
            if (tile_type > 0) {
                draw_box(r, tile, x, field.height() - y - 1, tile_type - 1);
            }
        }
    }
}
