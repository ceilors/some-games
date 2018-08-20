#include <iostream>
#include <SDL2/SDL.h>
#include "core.hpp"

const uint16_t WINDOW_WIDTH = 256;
const uint16_t WINDOW_HEIGHT = 240;

void sdl_error_quit(const char * function) {
    std::cout << function << " error:" << SDL_GetError() << std::endl;
    exit(1);
}

int main() {
    const uint8_t update_counter_max = 20;
    uint8_t update_counter = update_counter_max;
    bool quit_flag = false;
    SDL_Event event;

    Tetris tetris = Tetris();

    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        sdl_error_quit("SDL_Init");
    }
    SDL_Window * wnd = SDL_CreateWindow("Tetris", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
        WINDOW_WIDTH, WINDOW_HEIGHT, SDL_WINDOW_OPENGL);
    if (wnd == NULL) {
        sdl_error_quit("SDL_CreateWindow");
    }
    SDL_Renderer * render = SDL_CreateRenderer(wnd, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (render == NULL) {
        sdl_error_quit("SDL_CreateRenderer");
    }
    while (!quit_flag) {
        if (update_counter == 0) {
            tetris.step();
            update_counter = update_counter_max;
        } else {
            update_counter--;
        }
        while (SDL_PollEvent(&event) != 0) {
            switch (event.type) {
                case SDL_QUIT:
                    quit_flag = true;
                    break;
                case SDL_KEYDOWN:
                    switch (event.key.keysym.sym) {
                        case SDLK_w:
                            tetris.action(MOVE_HARD_DOWN);
                            break;
                        case SDLK_s:
                            tetris.action(MOVE_SOFT_DOWN);
                            break;
                        case SDLK_a:
                            tetris.action(MOVE_LEFT);
                            break;
                        case SDLK_d:
                            tetris.action(MOVE_RIGHT);
                            break;
                        case SDLK_g:
                            tetris.action(ROTATE_LEFT);
                            break;
                        case SDLK_h:
                            tetris.action(ROTATE_RIGHT);
                            break;
                        default:
                            break;
                    }
                    break;
                default:
                    break;
            }
        }
        SDL_RenderClear(render);
        tetris.render(render);
        SDL_RenderPresent(render);
    }
    SDL_DestroyRenderer(render);
    SDL_DestroyWindow(wnd);
    SDL_Quit();
}