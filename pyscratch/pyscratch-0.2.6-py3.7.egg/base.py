# encoding: utf-8
# module pyscratch
#
import sys
import os
import pygame
import threading
import time
import math
import random
import inspect
import functools
from collections import OrderedDict
from pygame.locals import *

game_running = True

backdrop_color = (255, 255, 255)

fps = 35
time_piece = 1/fps
cur_fragment = OrderedDict()
func_stack = OrderedDict()
thread_stack = OrderedDict()

screen = None
events = OrderedDict()
current_backdrop = None
backdrop_key = None
backdrop = OrderedDict()
lines = []
sprites_in_game = OrderedDict()
texts = []
mouse_position = (0, 0)

#
pygame.init()
screen = pygame.display.set_mode((480, 360))
pygame.display.set_caption("openscratch.com/pyscratch")
screen.fill(backdrop_color)
pygame.font.init()
font = pygame.font.Font(None, 24)
pygame.key.set_repeat(10)



def text(text_str, x=-120, y=-120, font_name=None, size=40, color=(128, 128, 128)):
    if not isinstance(text_str, str):
        text_str = str(text_str)
    font = pygame.font.Font(font_name, size)
    text_image = font.render(text_str, True, color) # ,(128,128,128)
    new_text = {"text": text_str, "x": x, "y": y, "size": size, "image": text_image}
    texts.append(new_text)


def refresh_events(start_time):
    global events
    new_events = {}
    for event_name, time_list in events.items():
        new_time_list = []
        for event_time in time_list:
            if event_time > start_time - time_piece:  # not too old
                new_time_list.append(event_time)
        if len(new_time_list) > 0:
            new_events[event_name] = new_time_list
    events = new_events


def update_screen():
    if not game_running:
        return
    # draw back ground
    if current_backdrop and current_backdrop.get_locked() is not True:
        screen.blit(current_backdrop, (0, 0))
    else:
        screen.fill(backdrop_color)
    # draw all lines
    for line in lines:
        #
        start_x = line['start_pos'][0] + 240
        start_y = 180 - line['start_pos'][1]
        end_x = line['end_pos'][0] + 240
        end_y = 180 - line['end_pos'][1]

        pygame.draw.line(screen, line['color'], [start_x, start_y], [end_x, end_y], line['width'])
    # draw all sprite
    for s in list(sprites_in_game.values()):
        if not s.sprite.get_locked() and s.showing:
            rect = s.rect.copy()
            rect.x = rect.x + 240 - rect.width//2
            rect.y = 180 - rect.y - rect.height//2
            if s.rotate_angle is not 0:
                new_sprite = pygame.transform.rotate(s.sprite, s.rotate_angle)
                #new_rect = s.sprite.get_rect(center=(55,53))
                screen.blit(new_sprite, rect)
            else:
                screen.blit(s.sprite, rect)
            if s.text_end_time is not None and time.perf_counter() > s.text_end_time:
                s.text = None
                s.text_end_time = None
            if s.text:
                text_rect = s.text.get_rect()
                text_x = rect.x - text_rect.width
                text_y = rect.y
                if text_x < 0:
                    text_x = rect.x + rect.width

                pygame.draw.rect(screen, [255, 255, 255], [text_x - 5, text_y - 5, text_rect.width + 10, text_rect.height + 10], 0)
                screen.blit(s.text, (text_x, text_y))

    for t in texts:
        start_x = t['x'] + 240
        start_y = 180 - t['y']
        screen.blit(t['image'], (start_x, start_y))

    pygame.display.update()


def frame_loop():
    while game_running:

        # time fragment
        start_time = time.perf_counter()
        cur_fragment['start_time'] = start_time
        cur_fragment['end_time'] = start_time + time_piece

        func_stack.clear()
        # event
        refresh_events(time.perf_counter())
        # events.clear()

        update_screen()
        elapsed = time.perf_counter() - start_time

        if time_piece > elapsed:
            time.sleep(time_piece - elapsed)


threading.Thread(target=frame_loop).start()


def frame_control(func):

    def wrapper(*args, **kwargs):

        get_events()

        stack = inspect.stack()
        stack_str = ""
        for s in stack:
            stack_str = stack_str + s[1] + str(s[2])
        hash_str = hash(str(stack_str))

        if hash_str in func_stack:
            # pause the function call if duplicate call in one fragment
            if func_stack[hash_str] > cur_fragment['start_time']:
                if cur_fragment['end_time'] - func_stack[hash_str] > 0:
                    time.sleep(cur_fragment['end_time'] - func_stack[hash_str])

        func_stack[hash_str] = time.perf_counter()
        result = func(*args, **kwargs)
        #update_screen()
        functools.update_wrapper(wrapper, func)
        return result
    return wrapper


def global_event(event_name, event_time=None):
    if event_time is None:
        event_time = time.perf_counter()
    # append event to global events
    if event_name in events:
        events[event_name].append(event_time)
    else:
        events[event_name] = [event_time]

    for s in list(sprites_in_game.values()):
        s.event(event_name)


def game_name(name):
    pygame.display.set_caption(name)


def erase_all():
    lines.clear()


def key_pressed(key):
    if isinstance(key, str):
        key = ord(key)

    if key in events:
        return True
    else:
        return False


def add_line(color, start_pos, end_pos, width):
    line = {'color': color, 'start_pos': start_pos, 'end_pos': end_pos, 'width': width}
    lines.append(line)


def get_events():
    global game_running
    global mouse_position
    mouse_position = pygame.mouse.get_pos()
    mouse_x = mouse_position[0] - 240
    mouse_y = 180 - mouse_position[1]
    mouse_position = mouse_x, mouse_y

    for event in pygame.event.get():
        if event.type == QUIT:
            game_running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            global_event(event.key)


def start():
    global game_running
    game_running = True
    global_event("start")

    while game_running:
        get_events()
        time.sleep(0.01)


class Sprite(object):
    def __init__(self, sprite_name, name=None, x=0, y=0):
        #name = str(name, 'utf-8')
        self.sprite_name = sprite_name
        if name is None:
            name = sprite_name
        self.size = 100
        self.x = x
        self.y = y
        self.direction = 90
        self.timer_start = time.perf_counter()
        self.pen_down_flag = False
        self.pen_size = 1
        self.pen_color = (0, 150, 0)
        self.event_watcher = {}
        self.costume = {}
        self.text = None
        self.text_end_time = None
        self.showing = True

        if not os.path.exists(name):
            name = os.path.join(os.path.split(__file__)[0], "sprite", name)

        for file_name in os.listdir(name):
            file_name_key = os.path.splitext(file_name)[0]
            self.costume[file_name_key] = os.path.join(name, file_name) #open(os.path.join(name,file_name), 'r')

        current_costume = list(self.costume.items())[0]
        self.current_costume_key = current_costume[0]
        self.current_costume_value = current_costume[1]

        self.proto_sprite = pygame.image.load(self.current_costume_value).convert_alpha();
        self.sprite = self.proto_sprite

        self.rect = self.sprite.get_rect() #rect(1,2,3,4) #  self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rotate_angle = 0

        sprites_in_game[sprite_name] = self

    # motition
    #
    @frame_control
    def move(self, steps):
        direction = 90 - self.direction
        direction_pi = math.pi * (direction/180) # to π

        steps_x = steps * round(math.cos(direction_pi), 15)
        steps_y = steps * round(math.sin(direction_pi), 15)

        self.go_to(self.rect.x + steps_x, self.rect.y + steps_y)

    @frame_control
    def turn_right(self, degrees):
        self.turn(-degrees)

    @frame_control
    def turn_left(self, degrees):
        self.turn(degrees)

    @frame_control
    def go_to(self, new_x, new_y):
        if self.pen_down_flag:
            add_line(self.pen_color, [self.rect.x, self.rect.y], [new_x, new_y], self.pen_size)
        self.set_x_to(new_x)
        self.set_y_to(new_y)
        self.adjust_position()

    @frame_control
    def go_to_random_position(self):
        random_x = random.randint(-240, 240)
        random_y = random.randint(-180, 180)
        self.go_to(random_x, random_y)

    @frame_control
    def go_to_mouse_pointer(self):
        self.go_to(mouse_position[0], mouse_position[1])

    @frame_control
    def glide_to(self, sec, x, y):
        interval = fps
        step_x = (x - self.rect.x)//interval
        step_y = (y - self.rect.y)//interval
        for i in range(interval):
            self.set_x_to(self.rect.x + step_x)
            self.set_y_to(self.rect.y + step_y)
            self.adjust_position()
            time.sleep(sec/interval)

    @frame_control
    def point(self, direction):
        self.direction = direction

    @frame_control
    def point_towards_mouse_pointer(self):
        mouse_x = mouse_position[0]
        mouse_y = mouse_position[1]

        direction_pi = math.atan2(mouse_y - self.rect.y, mouse_x - self.rect.x)
        self.direction = (direction_pi * 180) / math.pi
        self.direction = 90 - self.direction

    @frame_control
    def change_x_by(self, change_x):
        self.x = self.x + change_x
        self.rect.x = self.rect.x + change_x
        self.adjust_position()

    @frame_control
    def set_x_to(self, new_x):
        self.x = new_x
        self.rect.x = new_x
        self.adjust_position()

    @frame_control
    def change_y_by(self, change_y):#
        self.y = self.y + change_y
        self.rect.y = self.rect.y + change_y
        self.adjust_position()

    @frame_control
    def set_y_to(self, new_y):
        self.y = new_y
        self.rect.y = new_y
        self.adjust_position()

    def bounce_if_on_edge(self):
        if self.rect.x >= 240:
            self.direction = -self.direction
            self.flip()
        elif self.rect.x <= -240:
            self.direction = -self.direction
            self.flip()
        elif self.rect.y > 180:
            self.direction = 180 - self.direction
        elif self.rect.y < -180:
            self.direction = 180 - self.direction

    def adjust_position(self):
        if self.rect.x > 240:
            self.rect.x = 240
        if self.rect.x < -240:
            self.rect.x = -240
        if self.rect.y > 180:
            self.rect.y = 180
        if self.rect.y < -180:
            self.rect.y = -180

    def flip(self):
        self.sprite = pygame.transform.flip(self.sprite, True, False)

    @frame_control
    def turn(self, degrees):
        self.rotate_angle += degrees
        self.direction = self.direction + degrees

    # Looks
    #
    def say(self, text_str):
        self.say_for_seconds(text_str, None)

    def say_for_seconds(self, text_str, secs=2):
        text_image = font.render(str(text_str), True, (128, 128, 128))  # ,(128,128,128)
        self.text = text_image
        if secs is not None:
            self.text_end_time = time.perf_counter() + secs
            self.wait(secs)
        else:
            self.text_end_time = None

    def switch_costume_to(self, name):
        if name != self.current_costume_key:
            self.current_costume_key = name
            self.current_costume_value = self.costume.get(name)
            new_sprite = pygame.image.load(self.current_costume_value).convert_alpha()
            new_sprite = pygame.transform.smoothscale(new_sprite, (self.rect.width, self.rect.height))
            self.sprite = new_sprite

    def next_costume(self):
        keys = list(self.costume.keys())
        size = len(keys)
        index = keys.index(self.current_costume_key)
        if index >= size-1:
            index = 0
        else:
            index = index + 1

        self.switch_costume_to(keys[index])

    @frame_control
    def change_size_by(self, size_by):
        new_size = self.size + size_by
        if new_size > 0 :
            self.set_size_to(new_size)

    def set_size_to(self, num):
        proto_rect = self.proto_sprite.get_rect()
        width = proto_rect.width
        height = proto_rect.height
        new_width = int(width * (num / 100))
        new_height = int(height * (num / 100))
        self.sprite = pygame.transform.smoothscale(self.proto_sprite, (new_width, new_height))
        self.rect.width = new_width
        self.rect.height = new_height
        self.size = num

    def change_effect_by(self):
        pass

    def set_effect_to(self):
        pass

    def clear_graphic_effects(self):
        pass

    def show(self):
        self.showing = True

    def hide(self):
        self.showing = False

    def goto_front_layer(self):
        global sprites_in_game
        s = sprites_in_game[self.sprite_name]
        del sprites_in_game[self.sprite_name]
        sprites_in_game[self.sprite_name] = s

    def goto_back_layer(self):
        global sprites_in_game
        s = sprites_in_game[self.sprite_name]
        del sprites_in_game[self.sprite_name]
        new_dict = OrderedDict()
        new_dict[self.sprite_name] = s
        for k, v in sprites_in_game.items():
            new_dict[k] = v
        sprites_in_game = new_dict

    def go_forward_layer(self, num):
        pass

    def go_backward_layer(self, num):
        pass

    # Sound
    def play_sound(self, sound):
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        sound_file = pygame.mixer.Sound(sound)
        sound_file.play()

    # Events
    def regist_event(self, event_name, func):
        stack = inspect.stack()
        stack_str = ""
        for s in stack:
            stack_str = stack_str + s[1] + str(s[2])
        hash_str = hash(str(stack_str))
        func_data = [func, hash_str]
        if event_name in self.event_watcher:
            functions = self.event_watcher.get(event_name)
            functions.append(func_data)
        else:
            self.event_watcher[event_name] = [func_data]

    def when_start(self, func):
        self.regist_event("start", func)

    def when_key_pressed(self, key_name, func):
        self.regist_event(key_name, func)

    def when_receive(self,event_name, func):
        self.regist_event(event_name, func)

    def broadcast(self, event_name):
        global_event(event_name)

    # Control
    def wait(self, seconds):
        end = time.perf_counter() + seconds
        while time.perf_counter() < end:
            get_events()
            time.sleep(0.01)

    # Sensing
    def touching(self, sprite_name):
        sprite_2 = sprites_in_game.get(sprite_name)
        if sprite_2 is None:
            return False
        return pygame.Rect.colliderect(self.pygame_rect(self.rect), self.pygame_rect(sprite_2.rect))

    def reset_timer(self):
        self.timer_start = time.perf_counter()

    def timer(self):
        return time.perf_counter() - self.timer_start

    def pygame_rect(self, target_rect):
        new_rect = target_rect.copy()
        new_rect.x = new_rect.x + 240 - new_rect.width // 2
        new_rect.y = 180 - new_rect.y - new_rect.height // 2
        return new_rect

    # Operators
    def random(self, from_num, to_num):
        return random.randrange(from_num, to_num)

    # Pen
    @frame_control
    def pen_down(self):
        self.pen_down_flag = True

    @frame_control
    def pen_up(self):
        self.pen_down_flag = False

    def event(self, event_name):
        if event_name in self.event_watcher:
            functions = self.event_watcher.get(event_name)
            for func_data in functions:
                f = func_data[0]
                hash_str = func_data[1]

                thread_is_running = False
                if hash_str in thread_stack:
                    t = thread_stack.get(hash_str)
                    if t.is_alive():
                        thread_is_running = True

                if thread_is_running is False : # only one thread per time
                    t = threading.Thread(target=f)
                    t.start()
                    thread_stack[hash_str] = t

    def delete(self):
        del sprites_in_game[self.sprite_name]

def add_backdrop(name):
    global current_backdrop
    global backdrop_key
    global backdrop
    if os.path.exists(name):
        new_backdrop = pygame.image.load(name).convert_alpha()
    else:
        if not name.endswith(".jpg"):
            path = name + ".jpg"
            path = os.path.join(os.path.split(__file__)[0], "backdrop", path)
            new_backdrop = pygame.image.load(path).convert_alpha()

    backdrop[name] = new_backdrop
    current_backdrop = new_backdrop
    backdrop_key = name


def switch_backdrop(name):
    global current_backdrop
    global backdrop
    global backdrop_key
    if name not in backdrop:
        add_backdrop(name)
    current_backdrop = backdrop[name]
    backdrop_key = name


def next_backdrop():
    global current_backdrop
    global backdrop_key
    keys = list(backdrop.keys())
    size = len(keys)
    if size == 0:
        return
    # if backdrop is None:
    #     backdrops.items()[0]
    #     backdrop_item = list(backdrops.items())[0]
    #     backdrop_key = backdrop_item[0]
    #     backdrop = backdrop_item[1]
    #     return

    index = keys.index(backdrop_key)
    if index >= size - 1:
        index = 0
    else:
        index = index + 1

    switch_backdrop(keys[index])


def remove_backdrop(name):
    global current_backdrop
    global backdrop
    if name in backdrop:
        del backdrop[name]
