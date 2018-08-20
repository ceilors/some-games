#include "core.hpp"

// simple random
static uint8_t y8 = 1;

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
        this->operator()(it->first + f->pos.first, it->second + f->pos.second) = 1;
    }
}

bool Field::intersect(Figure * f) {
    // достижение дна
    if (f->pos.second + f->y_max == 0 || f->pos.second + f->y_max > _height) {
        return true;
    }
    for (figure_t::iterator it = f->coords.begin(); it != f->coords.end(); ++it) {
        // выход за границы
        if ((it->first + f->pos.first >= _width) || (it->second + f->pos.second >= _height)) {
            return true;
        }
        // пересечение с фигурой
        if (this->operator()(it->first + f->pos.first, it->second + f->pos.second)) {
            return true;
        }
    }
    return false;
}

pair_xy Field::border_outside(Figure * f) {
    uint8_t x = f->pos.first + f->x_max;
    uint8_t y = f->pos.second + f->y_max;
    pair_xy pos = std::make_pair(0, 0);

    if (x >= width()) {
        pos.first = (width() + 1) - x;
    }
    if (y >= height()) {
        pos.second = y - height();
    }
    return pos;
}

void Field::clear_line(uint8_t index) {
    for (uint8_t y = index + 1; y < _height; ++y) {
        for (uint8_t x = 0; x < _width; ++x) {
            this->operator()(x, y - 1) = this->operator()(x, y);
        }
    }
}

bool Field::check_line(uint8_t index) {
    uint8_t filled = 0;
    for (uint8_t x = 0; x < _width; ++x) {
        filled += this->operator()(x, index);
    }
    return filled == _width;
}

void Figure::set(uint8_t figure, uint8_t angle, uint8_t w, uint8_t h) {
    if (angle > angle_max) {
        throw std::invalid_argument("invalid figure angle");
    }
    x_max = y_max = 0;
    coords.clear();
    switch (figure) {
        case FIGURE_I:
            coords.push_back(std::make_pair(0, 0));
            coords.push_back(std::make_pair(1, 0));
            coords.push_back(std::make_pair(2, 0));
            coords.push_back(std::make_pair(3, 0));
            break;
        case FIGURE_J:
            coords.push_back(std::make_pair(0, 0));
            coords.push_back(std::make_pair(0, 1));
            coords.push_back(std::make_pair(1, 1));
            coords.push_back(std::make_pair(2, 1));
            break;
        case FIGURE_L:
            coords.push_back(std::make_pair(2, 0));
            coords.push_back(std::make_pair(0, 1));
            coords.push_back(std::make_pair(1, 1));
            coords.push_back(std::make_pair(2, 1));
            break;
        case FIGURE_O:
            coords.push_back(std::make_pair(0, 0));
            coords.push_back(std::make_pair(0, 1));
            coords.push_back(std::make_pair(1, 0));
            coords.push_back(std::make_pair(1, 1));
            break;
        case FIGURE_S:
            coords.push_back(std::make_pair(0, 0));
            coords.push_back(std::make_pair(0, 1));
            coords.push_back(std::make_pair(1, 1));
            coords.push_back(std::make_pair(1, 2));
            break;
        case FIGURE_T:
            coords.push_back(std::make_pair(1, 0));
            coords.push_back(std::make_pair(0, 1));
            coords.push_back(std::make_pair(1, 1));
            coords.push_back(std::make_pair(2, 1));
            break;
        case FIGURE_Z:
            coords.push_back(std::make_pair(1, 0));
            coords.push_back(std::make_pair(0, 1));
            coords.push_back(std::make_pair(1, 1));
            coords.push_back(std::make_pair(0, 2));
            break;
        default:
            throw std::invalid_argument("invalid figure index");
    }
    for (figure_t::iterator it = coords.begin(); it != coords.end(); ++it) {
        x_max = std::max(it->first, x_max);
        y_max = std::max(it->second, y_max);
    }
    pos = std::make_pair((w - x_max) / 2, h - y_max);
}

void Figure::rotate(bool direction) {
    uint8_t max_x = x_max;
    uint8_t mx = max_x;
    uint8_t my = max_x;
    // rotate
    for (figure_t::iterator it = coords.begin(); it != coords.end(); ++it) {
        uint8_t x = it->first;
        uint8_t y = it->second;
        if (direction) {
            it->first = max_x - y;
            it->second = x;
        } else {
            it->first = y;
            it->second = max_x - x;
        }
        mx = std::min(it->first, mx);
        my = std::min(it->second, my);
    }
    // shift
    for (figure_t::iterator it = coords.begin(); it != coords.end(); ++it) {
        it->first -= mx;
        it->second -= my;
    }
    // x & y maxs
    for (figure_t::iterator it = coords.begin(); it != coords.end(); ++it) {
        x_max = std::max(it->first, x_max);
        y_max = std::max(it->second, y_max);
    }
}

void Tetris::step() {
    curr.pos.second--;
    if (field.intersect(&curr)) {
        // установка и генерирование фигуры
        curr.pos.second++;
        field.set(&curr);
        curr = next;
        next.set(xorshift8() % (FIGURE_Z + 1), xorshift8() % (ANGLE_270 + 1), field.width(), field.height());
        // очистка заполненных ячеек поля
        for (int index = field.height() - 1; index >= 0; --index) {
            // здесь можно запилить подсчёт очков
            if (field.check_line((uint8_t)index)) {
                field.clear_line((uint8_t)index);
            }
        }
    }
}
 
void Tetris::action(uint8_t stat) {
    // for MOVE_HARD_DOWN
    Figure t = curr;
    pair_xy r;

    switch (stat) {
        case MOVE_LEFT:
            curr.pos.first--;
            if (field.intersect(&curr)) {
                curr.pos.first++;
            }
            break;
        case MOVE_RIGHT:
            curr.pos.first++;
            if (field.intersect(&curr)) {
                curr.pos.first--;
            }
            break;
        case MOVE_SOFT_DOWN:
            curr.pos.second--;
            if (field.intersect(&curr)) {
                curr.pos.second++;
            }
            break;
        case MOVE_HARD_DOWN:
            t.pos.second = field.height() - curr.y_max + 1;
            while (field.intersect(&t)) {
                t.pos.second++;
            }
            curr.pos.second = t.pos.second;
            break;
        case ROTATE_LEFT:
            curr.rotate(false);
            // проверка на выход за границы игрового поля
            r = field.border_outside(&curr);
            if (r.first != 0 || r.second != 0) {
                curr.pos.first -= r.first;
                curr.pos.second -= r.second;
            }
            break;
        case ROTATE_RIGHT:
            curr.rotate();
            r = field.border_outside(&curr);
            if (r.first != 0 || r.second != 0) {
                curr.pos.first -= r.first;
                curr.pos.second -= r.second;
            }
            break;
        default:
            throw std::invalid_argument("invalid figure action");
    }
}

Tetris::Tetris() {
    curr.set(xorshift8() % (FIGURE_Z + 1), xorshift8() % (ANGLE_270 + 1), field.width(), field.height());
    next.set(xorshift8() % (FIGURE_Z + 1), xorshift8() % (ANGLE_270 + 1), field.width(), field.height());
}

void draw_box(SDL_Renderer * r, uint8_t x, uint8_t y) {
    SDL_Rect box = { x * tile_size, y * tile_size, tile_size, tile_size };
    SDL_RenderFillRect(r, &box);
}

void Tetris::render(SDL_Renderer * r) {
    const SDL_Rect border = { 0, 0, field.width() * tile_size, field.height() * tile_size };
    const uint8_t next_figure_shift = field.width() + 1;

    SDL_SetRenderDrawColor(r, 255, 255, 255, SDL_ALPHA_OPAQUE);
    // сдвигаем точку отчёта для оси y для человеческой отрисовки
    // рисуем текущую фигуру на поле
    for (figure_t::iterator it = curr.coords.begin(); it != curr.coords.end(); ++it) {
        draw_box(r, it->first + curr.pos.first, field.height() - (it->second + curr.pos.second) - 1);
    }
    // следующая фигура
    for (figure_t::iterator it = next.coords.begin(); it != next.coords.end(); ++it) {
        draw_box(r, it->first + next_figure_shift, it->second + 1);
    }
    // рисуем игровое поле
    for (uint8_t y = 0; y < field.height(); ++y) {
        for (uint8_t x = 0; x < field.width(); ++x) {
            if (field(x, y) > 0) {
                draw_box(r, x, field.height() - y - 1);
            }
        }
    }
    SDL_RenderDrawRect(r, &border);
    SDL_SetRenderDrawColor(r, 0, 0, 0, SDL_ALPHA_OPAQUE);
}