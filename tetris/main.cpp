#include <iostream>
#include <SDL2/SDL.h>
#include "core.hpp"

const uint16_t WINDOW_WIDTH = 100;
const uint16_t WINDOW_HEIGHT = 100;

void sdl_error_quit(const char * function) {
    std::cout << function << " error:" << SDL_GetError() << std::endl;
    exit(1);
}

int main(int argc, char ** argv) {
    bool quit_flag = false;
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
    SDL_SetWindowSize(wnd, tetris.w_width, tetris.w_height);
    SDL_SetWindowPosition(wnd, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED);

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
                            tetris.move(PAUSE_STATE);
                            break;
                        case SDLK_w:
                            tetris.move(MOVE_HARD_DOWN);
                            break;
                        case SDLK_s:
                            tetris.move(MOVE_SOFT_DOWN);
                            break;
                        case SDLK_a:
                            tetris.move(MOVE_LEFT);
                            break;
                        case SDLK_d:
                            tetris.move(MOVE_RIGHT);
                            break;
                        case SDLK_g:
                            tetris.move(ROTATE_LEFT);
                            break;
                        case SDLK_h:
                            tetris.move(ROTATE_RIGHT);
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
        tetris.move(MOVE_SOFT_DOWN, true);
    }
    SDL_DestroyRenderer(render);
    SDL_DestroyWindow(wnd);
    SDL_Quit();
    return EXIT_SUCCESS;
}