#include <iostream>
#include <SDL2/SDL.h>
#include "core.hpp"

const uint16_t WINDOW_WIDTH = 18 * 16;
const uint16_t WINDOW_HEIGHT = 21 * 16;

void sdl_error_quit(const char * function) {
    std::cout << function << " error:" << SDL_GetError() << std::endl;
    exit(1);
}

int main(int argc, char ** argv) {
    bool quit_flag = false;
    bool pause_flag = true;
    SDL_Event event;

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
    Tetris tetris = Tetris(render);
    while (!quit_flag) {
        while (SDL_PollEvent(&event) != 0) {
            switch (event.type) {
                case SDL_QUIT:
                    quit_flag = true;
                    break;
                case SDL_KEYDOWN:
                    switch (event.key.keysym.sym) {
                        case SDLK_q:
                        case SDLK_ESCAPE:
                            quit_flag = true;
                            break;
                        case SDLK_SPACE:
                            pause_flag = !pause_flag;
                            break;
                        case SDLK_w:
                            if (!pause_flag) {
                                tetris.move(MOVE_HARD_DOWN);
                            }
                            break;
                        case SDLK_s:
                            if (!pause_flag) {
                                tetris.move(MOVE_SOFT_DOWN);
                            }
                            break;
                        case SDLK_a:
                            if (!pause_flag) {
                                tetris.move(MOVE_LEFT);
                            }
                            break;
                        case SDLK_d:
                            if (!pause_flag) {
                                tetris.move(MOVE_RIGHT);
                            }
                            break;
                        case SDLK_g:
                            if (!pause_flag) {
                                tetris.move(ROTATE_LEFT);
                            }
                            break;
                        case SDLK_h:
                            if (!pause_flag) {
                                tetris.move(ROTATE_RIGHT);
                            }
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
        tetris.render(render, pause_flag);
        SDL_RenderPresent(render);
        if (!pause_flag) {
            tetris.move(MOVE_SOFT_DOWN, true);
        }
    }
    SDL_DestroyRenderer(render);
    SDL_DestroyWindow(wnd);
    SDL_Quit();
    return EXIT_SUCCESS;
}