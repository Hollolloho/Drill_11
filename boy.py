from math import pi
from time import monotonic

from pico2d import (
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE,
    get_canvas_width, load_image,
)
from transitions import Machine


class AutoRun:
    DURATION = 5.0
    INITIAL_SPEED = 500.0
    ACCELERATION = 80.0
    SCALE_GROWTH = 0.15

    def __init__(self, boy):
        self.boy = boy
        self.scale = 1.0

    def enter(self):
        self.started_at = self.last_update = monotonic()
        self.scale = 1.0
        self.boy.frame = 0

    def expired(self, now):
        return now - self.started_at >= self.DURATION

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.pressed_directions = []
        self.image = load_image('animation_sheet.png')
        self.state_machine = Machine(
            model=self, states=['IDLE', 'RUN', 'SLEEP'], initial='IDLE', auto_transitions=False
        )
        # Internal transitions update the animation without leaving the current state.
        self.state_machine.add_transition('animate', 'IDLE', None, after='update_idle')
        self.state_machine.add_transition('animate', 'RUN', None, after='update_run')
        self.state_machine.add_transition('start_running', ['IDLE', 'SLEEP'], 'RUN')
        self.state_machine.add_transition('stop_running', 'RUN', 'IDLE')
        self.state_machine.add_transition('fall_asleep', 'IDLE', 'SLEEP')
        self.state_machine.add_transition('wake_up', 'SLEEP', 'IDLE')
        self.on_enter_IDLE()

    def on_enter_IDLE(self):
        self.idle_since = monotonic()

    def check_sleep_timeout(self, now):
        if self.state == 'IDLE' and now - self.idle_since >= 5:
            self.fall_asleep()

    def handle_event(self, event):
        now = monotonic()
        self.check_sleep_timeout(now)
        if self.state == 'IDLE':
            self.idle_since = now
        if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if event.key in self.pressed_directions:
                self.pressed_directions.remove(event.key)
            self.pressed_directions.append(event.key)
            self.face_dir = -1 if event.key == SDLK_LEFT else 1
            if self.state in ('IDLE', 'SLEEP'):
                self.frame = 0
                self.start_running()
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if event.key in self.pressed_directions:
                self.pressed_directions.remove(event.key)
            if self.state == 'RUN':
                if self.pressed_directions:
                    self.face_dir = -1 if self.pressed_directions[-1] == SDLK_LEFT else 1
                else:
                    self.stop_running()
        elif self.state == 'SLEEP' and event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.wake_up()

    def update(self):
        self.check_sleep_timeout(monotonic())
        if self.state in ('IDLE', 'RUN'):
            self.animate()

    def update_idle(self):
        self.frame = (self.frame + 1) % 8

    def update_run(self):
        self.frame = (self.frame + 1) % 8
        self.x = max(50, min(get_canvas_width() - 50, self.x + self.face_dir * 5))

    def draw(self):
        if self.state == 'SLEEP':
            # The rotated frame's visible bottom rests on the grass.
            self.image.clip_composite_draw(0, 300, 100, 100, pi / 2, '', self.x, self.y - 17, 100, 100)
        else:
            row = 100 if self.state == 'RUN' else 300
            if self.face_dir == -1:
                row -= 100
            self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)
