#pragma once
#include <iostream>
#include <stdexcept>
#include <stdint.h>
#include <utility>
#include <vector>

// SDL2
#include <SDL2/SDL.h>

/* 
для enum'мов не менять нумерацию
*/

enum FigureAngle {
    ANGLE_0 = 0,
    ANGLE_90 = 1,
    ANGLE_180 = 2,
    ANGLE_270 = 3
};


enum FigureType {
    FIGURE_I = 0,
    FIGURE_J = 1,
    FIGURE_L = 2,
    FIGURE_O = 3,
    FIGURE_S = 4,
    FIGURE_T = 5,
    FIGURE_Z = 6,
};

enum GameControl {
    MOVE_LEFT = 0,
    MOVE_RIGHT = 1,
    MOVE_SOFT_DOWN = 2,
    MOVE_HARD_DOWN = 3,
    ROTATE_LEFT = 4,
    ROTATE_RIGHT = 5
};

struct point {
    int8_t x, y;

    point() {}
    point(int8_t _x, int8_t _y): x(_x), y(_y) {}
};

typedef std::vector<point> figure_t;

class Figure {
public:
    Figure() : figure_max(FIGURE_Z), angle_max(ANGLE_270) {}

    void set(uint8_t figure, uint8_t angle, uint8_t w, uint8_t h);
    void rotate(bool direction=true);

    figure_t coords;
    point pos;
    uint8_t figure_max;
    uint8_t angle_max;
    int8_t x_max;
    int8_t y_max;
};

class Field {
    const uint8_t _width;
    const uint8_t _height;
    std::vector<uint8_t> field;
public:
    Field(uint8_t width=10, uint8_t height=15): _width(width + 2), _height(height + 1), field(_width * _height) {}

    void set(Figure * f);
    void clear();
    void clear_line(uint8_t index);
    bool check_line(uint8_t index);
    bool intersect(Figure * f);
    point border_outside(Figure * f);

    const uint8_t width() { return _width; }
    const uint8_t height() { return _height; }
    uint8_t & operator ()(uint8_t x, uint8_t y);
};

class Tetris {
    Figure curr;
    Figure next;
    Field field;
public:
    Tetris();
    void gameover();
    void step();
    void move(uint8_t direction);
    void render(SDL_Renderer * r);
};