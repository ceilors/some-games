CC=g++
CFLAGS=-std=c++98 -Wall $(shell sdl2-config --cflags)
LFLAGS=$(shell sdl2-config --libs) -lSDL2_image -lSDL2_ttf
app=tetris
objects := $(patsubst %.cpp,%.o,$(wildcard *.cpp))

all: $(objects)
	$(CC) $(objects) $(LFLAGS) -o $(app)
$(objects): %.o: %.cpp
	$(CC) $(CFLAGS) -c $< -o $@
clean:
	-$(RM) $(app) $(objects)