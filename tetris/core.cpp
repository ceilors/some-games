#include "core.hpp"

// simple random
static uint8_t y8 = (uint8_t)time(NULL);

static uint8_t tile_size = 16;

const uint8_t next_figure_blocks_count = 6;
const uint16_t score_table[5] = {0, 100, 300, 700, 1500};

uint8_t xorshift8(void) {
    y8 ^= (y8 << 7);
    y8 ^= (y8 >> 5);
    return y8 ^= (y8 << 3);
}

point find_phantom(Field field, Figure curr) {
    Figure t = curr;
    while (!field.intersect(&t)) {
        t.pos.y--;
    }
    curr.pos.y = t.pos.y + 1;
    return curr.pos;
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
    // game consts
    update_counter_max = 50;
    time_to_set_default = 40;
    // game timer
    time_to_set = time_to_set_default;
    update_counter = update_counter_max;

    high_score = std::max(game_score, high_score);

    // game info
    game_score = 0;
    game_speed = 1;
    game_lines = 0;

    game_over_flag = false;

    field.clear();
    curr.set(xorshift8() % (FIGURE_Z + 1), field.width(), field.height() - 1);
    next.set(xorshift8() % (FIGURE_Z + 1), field.width(), field.height() - 1);
}

void Tetris::move(uint8_t state, bool delay) {
    point _shifts[] = {point(-1, 0), point(1, 0), point(0, -1), point(0, 1)};
    figure_t shifts(_shifts, _shifts+4);
    static bool set_flag = false;

    if (state != PAUSE_STATE && pause_flag) {
        return;
    }

    switch (state) {
        case PAUSE_STATE: {
            pause_flag = !pause_flag;
            if (game_over_flag) {
                gameover();
            }
            return;
            break;
        }
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
            // задержка для регулирования скорости игры
            if (update_counter <= 0 || !delay || set_flag) {
                update_counter = update_counter_max;
            } else {
                update_counter--;
                return;
            }
            
            curr.pos.y--;
            if (field.intersect(&curr)) {
                curr.pos.y++;
                set_flag = true;
            }
            break;
        }
        case MOVE_HARD_DOWN: {
            point new_pos = find_phantom(field, curr);
            // очки за быстрый спуск
            game_score += (curr.pos.y - new_pos.y);
            curr.pos = new_pos;
            set_flag = true;
            break;
        }
        case ROTATE_LEFT:
        case ROTATE_RIGHT: {
            bool side = true ? state == ROTATE_LEFT : false;
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
    if (set_flag && time_to_set <= 0 && !game_over_flag) {
        set_flag = false;
        time_to_set = time_to_set_default;
        try {
            field.set(&curr);
        } catch (std::out_of_range &) {
            game_over_flag = true;
            pause_flag = true;
            return;
        }
        // очки за установку фигуры на поле
        game_score += curr.coords.size();
        curr = next;
        next.set(xorshift8() % (FIGURE_Z + 1), field.width(), field.height() - 1);
        // очистка заполненных ячеек поля
        uint8_t lines_count = 0;
        for (int index = field.height() - 1; index >= 1; --index) {
            // здесь можно запилить подсчёт очков
            if (field.check_line((uint8_t)index)) {
                field.clear_line((uint8_t)index);
                lines_count++;
            }
        }
        // очки за удаление линий
        game_score += score_table[lines_count];
        if ((game_lines + lines_count) / 10 - game_lines / 10 == 1) {
            update_counter_max -= 4;
            time_to_set_default += 3;
            game_speed += 1;
        }
        game_lines += lines_count;
        // проверяем что фигуре ничего не мешает
        if (field.intersect(&curr)) {
            game_over_flag = true;
            pause_flag = true;
            return;
        }
    } else if (set_flag) {
        time_to_set--;
    }
}

Tetris::Tetris(SDL_Renderer * r) {
    if (TTF_Init() != 0) {
        std::cout << "TTF_Init error:" << TTF_GetError() << std::endl;
        exit(1);
    }

    tile = IMG_LoadTexture(r, "../resources/tetris_block.png");
    int tile_height = 16;
    SDL_QueryTexture(tile, NULL, NULL, NULL, &tile_height);
    tile_size = (uint8_t) tile_height;

    font = TTF_OpenFont("../resources/FiraMono-Regular.ttf", 12);
    
    pause_flag = true;

    gameover();

    w_width = (field.width() + next_figure_blocks_count) * tile_size;
    w_height = field.height() * tile_size;
}

Tetris::~Tetris() {
    SDL_DestroyTexture(tile);
    TTF_CloseFont(font);
    TTF_Quit();
}

void draw_box(SDL_Renderer * r, SDL_Texture * tex, int8_t x, int8_t y, uint8_t id) {
    SDL_Rect wnd = { id * tile_size, 0, tile_size, tile_size };
    SDL_Rect pos = { x * tile_size, y * tile_size, tile_size, tile_size };
    SDL_RenderCopy( r, tex, &wnd, &pos );
}

void draw_frame(SDL_Renderer * r, point * pos, figure_t * coords, Field * field) {
    std::vector<SDL_Rect> rects;
    for (figure_t::iterator it = coords->begin(); it != coords->end(); ++it) {
        SDL_Rect f = {
            (it->x + pos->x) * tile_size, (field->height() - (it->y + pos->y) - 1) * tile_size,
            tile_size, tile_size
        };
        rects.push_back(f);
    }
    SDL_SetRenderDrawColor(r, 255, 255, 255, 255);
    SDL_RenderDrawRects(r, rects.data(), rects.size());
    SDL_SetRenderDrawColor(r, 0, 0, 0, 255);
}

void draw_text(SDL_Renderer * r, TTF_Font * font, const char * text, uint16_t x, uint16_t y, SDL_Color color) {
    SDL_Surface * f_surface = TTF_RenderText_Blended(font, text, color);
    SDL_Texture * f_texture = SDL_CreateTextureFromSurface(r, f_surface);
    SDL_Rect text_rect = {0, 0, 0, 0};
    SDL_Rect wnd_rect = {x, y, 0, 0};
    SDL_QueryTexture(f_texture, NULL, NULL, &text_rect.w, &text_rect.h);
    wnd_rect.w = text_rect.w;
    wnd_rect.h = text_rect.h;
    SDL_RenderCopy(r, f_texture, &text_rect, &wnd_rect);
    SDL_DestroyTexture(f_texture);
}

void draw_text(SDL_Renderer * r, TTF_Font * font, int value, uint16_t x, uint16_t y, SDL_Color color) {
    std::ostringstream buffer;
    buffer << value;
    draw_text(r, font, buffer.str().c_str(), x, y, color);
}

void Tetris::render(SDL_Renderer * r) {
    const int8_t next_figure_shift = field.width() + 1;
    const SDL_Color clr_white = {255, 255, 255, 255};

    if (!pause_flag) {
        // рисуем игровое поле
        for (int8_t y = 0; y < field.height(); ++y) {
            for (int8_t x = 0; x < field.width(); ++x) {
                uint8_t tile_type = field(x, y);
                if (tile_type > 0) {
                    draw_box(r, tile, x, field.height() - y - 1, tile_type - 1);
                }
            }
        }
        // сдвигаем точку отчёта для оси y для человеческой отрисовки
        // рисуем текущую фигуру на поле
        for (figure_t::iterator it = curr.coords.begin(); it != curr.coords.end(); ++it) {
            draw_box(r, tile, it->x + curr.pos.x, field.height() - (it->y + curr.pos.y) - 1, curr.color);
        }
        point phantom = find_phantom(field, curr);
        // рисуем предпологаемое место фигуры на дне стакана
        draw_frame(r, &phantom, &(curr.coords), &field);
        // следующая фигура
        for (figure_t::iterator it = next.coords.begin(); it != next.coords.end(); ++it) {
            draw_box(r, tile, it->x + next_figure_shift, next.y_max - it->y + 1, next.color);
        }
    } else {
        draw_text(r, font, "paused", next_figure_shift * tile_size, 14 * tile_size, clr_white);
    }
    draw_text(r, font, "next", next_figure_shift * tile_size, 0, clr_white);
    draw_text(r, font, "highscore", next_figure_shift * tile_size, 4 * tile_size, clr_white);
    draw_text(r, font, high_score, next_figure_shift * tile_size, 5 * tile_size, clr_white);
    draw_text(r, font, "score", next_figure_shift * tile_size, 6 * tile_size, clr_white);
    draw_text(r, font, game_score, next_figure_shift * tile_size, 7 * tile_size, clr_white);
    draw_text(r, font, "lines", next_figure_shift * tile_size, 8 * tile_size, clr_white);
    draw_text(r, font, game_lines, next_figure_shift * tile_size, 9 * tile_size, clr_white);
    draw_text(r, font, "speed", next_figure_shift * tile_size, 11 * tile_size, clr_white);
    draw_text(r, font, game_speed, next_figure_shift * tile_size, 12 * tile_size, clr_white);
    if (game_over_flag) {
        draw_text(r, font, "gameover", next_figure_shift * tile_size, 15 * tile_size, clr_white);
    }
}
