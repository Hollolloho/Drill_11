from pico2d import *
import random

from boy import Boy  # boy: 모듈이름, Boy: 클래스 이름
from grass import Grass  # grass: 모듈이름, Grass: 클래스 이름

# Game object class here

def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        boy.handle_event(event)
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


def reset_world():
    global world
    global boy

    world = []

    grass = Grass()
    world.append(grass)

    boy = Boy()
    world.append(boy)



def update_world():
    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


running = True

open_canvas()
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)
# finalization code
close_canvas()
