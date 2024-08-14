# ToDo :
# Fix Phase through walls
# FPS
# Change impulse to gradually changing velocity
# End screen
# shape filter
# fix big second jump glitch
# fix leg starting position glitch
# Fix other bugs
# boost cooldown indicator

# Add freeze power up
# big jump
# big kick
# No gravity
# Less gravity
# Randomness powerup
# Add a wall
# add a bouncy wall
# pong

# exe



import pygame
import pymunk
import pymunk.pygame_util
import numpy as np
import math
import time
import random
import sys
import ctypes
from ctypes import wintypes
import os

pygame.init()
pygame.mixer.init()


def recenter_window():
    hwnd = pygame.display.get_wm_info()['window']
    user32 = ctypes.WinDLL("user32")
    user32.SetWindowPos.restype = wintypes.HWND
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.UINT]
    user32.SetWindowPos(hwnd, -1, (screen_size[0] - current_width) // 2, (screen_size[1] - current_height) // 2 - 32 // 2, 0, 0, 0x0001)


def window_key_control(e):
    global fake_screen, fullscreen, current_width, current_height

    if e.type == pygame.KEYDOWN and e.key == pygame.K_u:   # Fullscreen
        recenter_window()

        if not fullscreen:
            fake_screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
        else:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (int((screen_size[0] + current_width) / 2), int((screen_size[1] + current_height) / 2))
            fake_screen = pygame.display.set_mode((int(screen_size[0] / 1.2), int(screen_size[1] / 1.2)), pygame.RESIZABLE)
        fullscreen = not fullscreen

    if e.type == pygame.KEYDOWN and e.key == pygame.K_p:  # Recenter
        recenter_window()

    if e.type == pygame.KEYDOWN and e.key == pygame.K_i:
        current_width -= 50
        current_height -= 50

    if e.type == pygame.KEYDOWN and e.key == pygame.K_o:
        current_width += 50
        current_height += 50

    # if event.type == pygame.VIDEORESIZE:


def window_fixsize():
    global fake_screen, display_window_width, display_window_height

    if display_window_width != current_width or display_window_height != current_height:
        fake_screen = pygame.display.set_mode((int(current_height * 16 / 9), current_height), pygame.RESIZABLE)
        display_window_width = current_width
        display_window_height = current_height


def draw_any():
    global current_width, current_height
    window_fixsize()
    # print(fake_screen.get_rect().size)
    current_width = int(fake_screen.get_rect().size[1] * 16/9)
    current_height = fake_screen.get_rect().size[1]
    fake_screen.blit(pygame.transform.scale(screen, (current_width, current_height)), (0, 0))
    pygame.display.flip()
    

class Timer:
    def __init__(self, length):
        self.length = length
        self.start_time = None
        self.pause_start_time = None
        self.paused = False

    def start(self):
        self.start_time = time.time()

    def pause(self):
        self.pause_start_time = time.time()
        self.paused = True

    def resume(self):
        time_paused = time.time() - self.pause_start_time
        self.start_time = self.start_time + time_paused
        self.paused = False

    def get(self):
        if self.paused:
            return self.length - (self.pause_start_time - self.start_time)
        else:
            return self.length - (time.time() - self.start_time)


def modify(key):
    if key in mutator:
        return mutator[key]
    else:
        return 0


def reset_all():
    print('Reset all')
    # player var
    # score


def mypath(file_name):
    return os.path.join('assets', file_name)


def end_screen(w):
    print('Insert end screen')

    print(w, 'wins!')
    return 'customize'
    # return 'play again'
    # return 'home'


def play_game(win_score):
    global scored, score_text

    pygame.mixer.music.play()
    while True:
        space.step(dt)

        t_end = time.time() + 2
        if scored:
            p1_boost_timer.pause()
            p2_boost_timer.pause()
            player_1.force, player_2.force = 0, 0
            while time.time() < t_end:
                space.step(dt)
                update_and_draw()
                # pygame.display.flip()
                draw_any()
                clock.tick(fps)
            scored = False
            reset()
            p1_boost_timer.resume()
            p2_boost_timer.resume()

        if player_1.score >= win_score:
            player_1.delete()
            player_2.delete()
            score_text = score_font.render('0 - 0', True, score_text_color)
            return 'player 1'
        elif player_2.score >= win_score:
            player_1.delete()
            player_2.delete()
            score_text = score_font.render('0 - 0', True, score_text_color)
            return 'player 2'

        score_text = score_font.render(str(player_2.score) + ' - ' + str(player_1.score), True, score_text_color)

        keys()

        update_and_draw()

        clock.tick(fps)


def customization_screen(p1_info, p2_info):
    global player_1_head, player_2_head, player_1_cleat, player_2_cleat, player_1, player_2
    global customize

    # hs means head selection
    p1_hs_angle = 0
    p1_desired_hs_angle = 0
    p1_hs_display = []
    for i in range(heads.index(p1_info['head']) - 2, heads.index(p1_info['head']) + 2 + 1):
        p1_hs_display.append(heads[i % num_heads])
    p1_selection_wheel = 'head'
    p1_hs_used = [False, False]
    p1_hs_shift = 0

    p2_hs_angle = 0
    p2_desired_hs_angle = 0
    p2_hs_display = []
    for i in range(heads.index(p2_info['head']) - 2, heads.index(p2_info['head']) + 2 + 1):
        p2_hs_display.append(heads[i % num_heads])
    p2_selection_wheel = 'head'
    p2_hs_used = [False, False]
    p2_hs_shift = 0

    # cs means cleat selection
    p1_cs_angle = 0
    p1_desired_cs_angle = 0
    # p1_cs_display = list(range(1, 6))
    p1_cs_display = []
    for i in range(p1_info['cleat'] - 2 - 1, p1_info['cleat'] + 2 - 1 + 1):
        p1_cs_display.append(i % num_cleats + 1)
    p1_cs_used = [False, False]
    p1_cs_shift = 0

    p2_cs_angle = 0
    p2_desired_cs_angle = 0
    p2_cs_display = []
    for i in range(p2_info['cleat'] - 2 - 1, p2_info['cleat'] + 2 - 1 + 1):
        p2_cs_display.append(i % num_cleats + 1)
    p2_cs_used = [False, False]
    p2_cs_shift = 0

    p1_outline_pos, p1_desired_outline_pos = 0, 0
    p2_outline_pos, p2_desired_outline_pos = 0, 0

    while True:
        window_fixsize()

        screen.fill((33, 33, 33))

        title_font = pygame.font.Font(mypath('Font.TTF'), 200)
        title_text = title_font.render('Head Soccer', True, (235, 235, 235))

        title_scale = 0.025 * (np.sin(time.time()) + 30)
        title_text = pygame.transform.scale(title_text, (
            int(title_text.get_width() * title_scale), int(title_text.get_height() * title_scale)))
        title_text_rect = title_text.get_rect()
        title_text_rect.center = (width // 2, 200)
        screen.blit(title_text, title_text_rect)

        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(width - sw_pos_info[0] - sw_outline_size[0] // 2, sw_pos_info[1] - sw_outline_size[1] // 2 + p1_outline_pos * sw_pos_info[2], sw_outline_size[0], sw_outline_size[1]), 0, sw_outline_rounding)
        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(sw_pos_info[0] - sw_outline_size[0] // 2, sw_pos_info[1] - sw_outline_size[1] // 2 + p2_outline_pos * sw_pos_info[2], sw_outline_size[0], sw_outline_size[1]), 0, sw_outline_rounding)

        selection_wheel(p1_hs_display, p1_hs_angle, p1_hs_shift, p1_hs_pos, 'head')
        selection_wheel(p1_cs_display, p1_cs_angle, p1_cs_shift, p1_cs_pos, 'cleat')
        selection_wheel(p2_hs_display, p2_hs_angle, p2_hs_shift, p2_hs_pos, 'head')
        selection_wheel(p2_cs_display, p2_cs_angle, p2_cs_shift, p2_cs_pos, 'cleat')

        draw_any()

        p1_outline_pos = p1_outline_pos * (sw_smoothing - 1) / sw_smoothing + p1_desired_outline_pos * 1 / sw_smoothing
        p2_outline_pos = p2_outline_pos * (sw_smoothing - 1) / 5 + p2_desired_outline_pos * 1 / sw_smoothing

        p1_hs_angle = p1_hs_angle * (sw_smoothing - 1) / sw_smoothing + p1_desired_hs_angle * 1 / sw_smoothing
        p1_cs_angle = p1_cs_angle * (sw_smoothing - 1) / sw_smoothing + p1_desired_cs_angle * 1 / sw_smoothing
        p2_hs_angle = p2_hs_angle * (sw_smoothing - 1) / sw_smoothing + p2_desired_hs_angle * 1 / sw_smoothing
        p2_cs_angle = p2_cs_angle * (sw_smoothing - 1) / sw_smoothing + p2_desired_cs_angle * 1 / sw_smoothing

        for event in pygame.event.get():
            window_key_control(event)

            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.mixer.Sound.play(start_game_sound)

                original_title_text = title_text

                d = 270
                for i in range(0, d, 5):
                    if int(original_title_text.get_height() * (d - i) / d) > 0:
                        screen.fill((33, 33, 33))

                        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(width - sw_pos_info[0] - sw_outline_size[0] // 2, sw_pos_info[1] - sw_outline_size[1] // 2 + p1_outline_pos * sw_pos_info[2], sw_outline_size[0], sw_outline_size[1]), 0, sw_outline_rounding)
                        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(sw_pos_info[0] - sw_outline_size[0] // 2, sw_pos_info[1] - sw_outline_size[1] // 2 + p2_outline_pos * sw_pos_info[2], sw_outline_size[0], sw_outline_size[1]), 0, sw_outline_rounding)

                        selection_wheel(p1_hs_display, p1_hs_angle, p1_hs_shift, p1_hs_pos, 'head')
                        selection_wheel(p1_cs_display, p1_cs_angle, p1_cs_shift, p1_cs_pos, 'cleat')
                        selection_wheel(p2_hs_display, p2_hs_angle, p2_hs_shift, p2_hs_pos, 'head')
                        selection_wheel(p2_cs_display, p2_cs_angle, p2_cs_shift, p2_cs_pos, 'cleat')

                        title_text = pygame.transform.scale(original_title_text, (
                            int(original_title_text.get_width() * (d - i) / d),
                            int(original_title_text.get_height() * (d - i) / d)))
                        title_text = pygame.transform.rotate(title_text, i)
                        title_text_rect = title_text.get_rect()
                        title_text_rect.center = (width // 2, 200)
                        screen.blit(title_text, title_text_rect)
                        draw_any()
                    else:
                        break

                # Player Initialization
                player_1_head = p1_hs_display[2]
                player_2_head = p2_hs_display[2]

                player_1_cleat = p1_cs_display[2]
                player_2_cleat = p2_cs_display[2]

                player_1 = Player(width - player_start_x, player_start_y, 'left')
                player_2 = Player(player_start_x, player_start_y, 'right')

                player_1.motor.set_target_angle(np.deg2rad(player_1_min_kick))
                player_2.motor.set_target_angle(np.deg2rad(player_2_min_kick))

                update_and_draw()

                pygame.mixer.Sound.play(countdown_sound)
                for i in range(3, 0, -1):
                    update_and_draw()
                    # countdown_font = pygame.font.Font(mypath('Font.TTF'), 150)
                    countdown_font = goal_font
                    countdown_text = countdown_font.render(str(i), True, (230, 230, 230))
                    countdown_text_rect = countdown_text.get_rect()
                    countdown_text_rect.center = (width // 2, 400)
                    screen.blit(countdown_text, countdown_text_rect)
                    draw_any()
                    time.sleep(1)

                customize = False

                return 0

            # Player 1
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT and not p1_hs_used[1]:
                pygame.mixer.Sound.play(selection_sound)
                if p1_selection_wheel == 'head':
                    p1_desired_hs_angle += 45
                    p1_hs_shift -= 45
                    p1_hs_display = [heads[(heads.index(p1_hs_display[2]) - 3) % num_heads]] + p1_hs_display[:4]
                    p1_hs_used[1] = True
                else:
                    p1_desired_cs_angle += 45
                    p1_cs_shift -= 45
                    p1_cs_display = [(p1_cs_display[2] - 3 - 1) % num_cleats + 1] + p1_cs_display[:4]
                    p1_cs_used[1] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                if p1_selection_wheel == 'head':
                    p1_hs_used[1] = False
                else:
                    p1_cs_used[1] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT and not p1_hs_used[0]:
                pygame.mixer.Sound.play(selection_sound)
                if p1_selection_wheel == 'head':
                    p1_desired_hs_angle -= 45
                    p1_hs_shift += 45
                    p1_hs_display = p1_hs_display[1:] + [heads[(heads.index(p1_hs_display[2]) + 3) % num_heads]]
                    p1_hs_used[0] = True
                else:
                    p1_desired_cs_angle -= 45
                    p1_cs_shift += 45
                    p1_cs_display = p1_cs_display[1:] + [(p1_cs_display[2] + 3 - 1) % num_cleats + 1]
                    p1_cs_used[0] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                if p1_selection_wheel == 'head':
                    p1_hs_used[0] = False
                else:
                    p1_cs_used[0] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN and p1_selection_wheel == 'head':
                pygame.mixer.Sound.play(selection_sound)
                p1_desired_outline_pos = 1
                p1_selection_wheel = 'cleat'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and p1_selection_wheel == 'cleat':
                pygame.mixer.Sound.play(selection_sound)
                p1_desired_outline_pos = 0
                p1_selection_wheel = 'head'

            # Player 2
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a and not p2_hs_used[1]:
                pygame.mixer.Sound.play(selection_sound)
                if p2_selection_wheel == 'head':
                    p2_desired_hs_angle += 45
                    p2_hs_shift -= 45
                    p2_hs_display = [heads[(heads.index(p2_hs_display[2]) - 3) % num_heads]] + p2_hs_display[:4]
                    p2_hs_used[1] = True
                else:
                    p2_desired_cs_angle += 45
                    p2_cs_shift -= 45
                    p2_cs_display = [(p2_cs_display[2] - 3 - 1) % num_cleats + 1] + p2_cs_display[:4]
                    p2_cs_used[1] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_a:
                if p2_selection_wheel == 'head':
                    p2_hs_used[1] = False
                else:
                    p2_cs_used[1] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d and not p2_hs_used[0]:
                pygame.mixer.Sound.play(selection_sound)
                if p2_selection_wheel == 'head':
                    p2_desired_hs_angle -= 45
                    p2_hs_shift += 45
                    p2_hs_display = p2_hs_display[1:] + [heads[(heads.index(p2_hs_display[2]) + 3) % num_heads]]
                    p2_hs_used[0] = True
                else:
                    p2_desired_cs_angle -= 45
                    p2_cs_shift += 45
                    p2_cs_display = p2_cs_display[1:] + [(p2_cs_display[2] + 3 - 1) % num_cleats + 1]
                    p2_cs_used[0] = True
            if event.type == pygame.KEYUP and event.key == pygame.K_d:
                if p2_selection_wheel == 'head':
                    p2_hs_used[0] = False
                else:
                    p2_cs_used[0] = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s and p2_selection_wheel == 'head':
                pygame.mixer.Sound.play(selection_sound)
                p2_desired_outline_pos = 1
                p2_selection_wheel = 'cleat'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w and p2_selection_wheel == 'cleat':
                pygame.mixer.Sound.play(selection_sound)
                p2_desired_outline_pos = 0
                p2_selection_wheel = 'head'

        clock.tick(fps)


def selection_wheel(selection_display, angle, shift, position, wheel_type):
    for i in [0, 4, 1, 3, 2]:
        a = angle + [-90, -45, 0, 45, 90][i] + shift
        distance_scale = (np.cos(np.deg2rad(a)) + 1) / 2
        o = (distance_scale - 0.5) * 2 * (255 - 50) + 50

        item = selection_display[i]
        if wheel_type == 'head':
            item_image = pygame.image.load(mypath(item + '_Head.png'))
            item_image.set_alpha(o)

            item_surface = pygame.transform.scale(item_image, (
                int(distance_scale * head_size * head_scale[item][0]), int(
                    distance_scale * head_scale[item][1] * head_size / item_image.get_size()[0] *
                    item_image.get_size()[1])))
        else:
            item_image = pygame.image.load(mypath('Cleat ' + str(item) + '.png'))
            item_image.set_alpha(o)

            item_surface = pygame.transform.scale(item_image, (
                int(distance_scale * cleat_size), int(
                    distance_scale * cleat_size / item_image.get_size()[0] *
                    item_image.get_size()[1])))

        screen.blit(item_surface, item_surface.get_rect(
            center=(position[0] + np.sin(np.deg2rad(a)) * 150, position[1])))


def progress_bar(current, place):
    if place == 'left':
        pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(pb_x - pb_outline_size, pb_y - pb_outline_size, pb_width + 2 * pb_outline_size, pb_height + 2 * pb_outline_size), 0, int(pb_rounding * 1.5))
        pygame.draw.rect(screen, (100, 190, 100), pygame.Rect(pb_x, pb_y, current * pb_width/boost_delay, pb_height), 0, pb_rounding)
    else:
        pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(width - pb_x - pb_width - pb_outline_size, pb_y - pb_outline_size, pb_width + 2 * pb_outline_size, pb_height + 2 * pb_outline_size), 0, int(pb_rounding * 1.5))
        pygame.draw.rect(screen, (100, 190, 100), pygame.Rect(width - pb_x - pb_width, pb_y, current * pb_width/boost_delay, pb_height), 0, pb_rounding)


def update_and_draw():
    global score_text_rect

    player_1.leg_shape.elasticity = -0.00122807 * player_1.head_body.position.y + 1.67544
    player_2.leg_shape.elasticity = -0.00122807 * player_2.head_body.position.y + 1.67544

    player_1.update()
    player_2.update()

    player_1.motor.update()
    player_2.motor.update()

    ball.update()

    score_text_rect = score_text.get_rect()
    score_text_rect.center = (width // 2, 100)

    screen.fill((33, 33, 33))

    draw_borders()
    ball.draw()
    player_1.draw(player_1_head, player_1_cleat)
    player_2.draw(player_2_head, player_2_cleat)

    try:
        progress_bar(min(boost_delay - p2_boost_timer.get(), boost_delay), 'left')
        progress_bar(min(boost_delay - p1_boost_timer.get(), boost_delay), 'right')
    except:
        pass

    # screen.blit(gametime_text, gametime_text_rect)

    screen.blit(score_text, score_text_rect)
    if scored:
        screen.blit(goal_text, goal_text_rect)


    # space.debug_draw(draw_options)
    draw_any()


def reset():
    global ball
    space.remove(ball.body, ball.shape)
    ball = Ball(ball_start_x, ball_start_y)

    player_1.reset()
    player_2.reset()


def create_borders():
    lines = [pymunk.Segment(space.static_body, (0, height - goal_height), (goal_width, height - goal_height), 5.0),
             pymunk.Segment(space.static_body, (width - goal_width, height - goal_height),
                            (width, height - goal_height), 2.0)]

    for i in range(len(border_points) - 1):
        lines.append(pymunk.Segment(space.static_body, border_points[i], border_points[i + 1], 0.1))

    data = []
    for l in lines:
        l.elasticity = 0.85
        l.friction = 0.6
        data.append(l)
    space.add(*lines)
    return data


def draw_borders():
    screen.blit(goal_net, (0, height - goal_height))
    screen.blit(goal_net, (width - goal_width, height - goal_height))
    pygame.draw.line(screen, (155, 155, 155), (0, height - goal_height), (goal_width, height - goal_height), 10)
    pygame.draw.line(screen, (155, 155, 155), (width - goal_width, height - goal_height), (width, height - goal_height),
                     10)
    pygame.draw.circle(screen, (155, 155, 155), (goal_width, height - goal_height + 1), 4)
    pygame.draw.circle(screen, (155, 155, 155), (width - goal_width, height - goal_height + 1), 4)

    pygame.draw.polygon(screen, (55, 55, 55), left_curve_points + [(0, 0)])
    pygame.draw.polygon(screen, (55, 55, 55), right_curve_points + [(width, 0)])
    pygame.draw.polygon(screen, (55, 55, 55), floor + [(0, height), (width, height)])


class Motor(pymunk.SimpleMotor):
    def __init__(self, body_a, body_b, max_force, max_rate, p_gain):
        super().__init__(body_a, body_b, 0)  # Start with rate = 0
        self.body_a = body_a
        self.body_b = body_b
        self.max_force = max_force
        self.max_rate = max_rate
        self.p_gain = p_gain
        self.target_angle = 0

    def angle(self):
        return self.body_a.angle - self.body_b.angle

    def set_target_angle(self, target_angle):
        self.target_angle = target_angle

    def update(self):
        # to clamp the turning rate
        self.rate = max(min((self.target_angle - self.angle()) * self.p_gain, self.max_rate), -self.max_rate)


class Ball:
    def __init__(self, x, y):
        self.mass = 20
        self.radius = ball_size / 2
        self.inertia = pymunk.moment_for_circle(self.mass, 0, self.radius, (0, 0))
        self.body = pymunk.Body(self.mass, self.inertia)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, self.radius, (0, 0))
        self.shape.elasticity = 0.92
        self.shape.friction = 0.87

        self.body.velocity = (random.randint(-275, 275), 0)
        self.body.angular_velocity = random.randint(-30, 30)

        space.add(self.body, self.shape)

    def draw(self):
        screen.blit(ball_surface, ball_surface.get_rect(center=(int(ball.body.position.x), int(ball.body.position.y))))

    def update(self):
        global ball_surface, scored, goal_sfx, cheer_sfx
        ball_surface = pygame.transform.rotate(original_ball_surface, -(ball.body.angle * 180 / math.pi) % 360)

        if self.body.position.y > height - goal_height and not scored:
            if self.body.position.x < goal_width:
                player_1.score += 1
                scored = True

                cheer_sound = pygame.mixer.Sound(mypath('Cheer ' + str(cheer_sfx) + '.wav'))
                cheer_sound.set_volume(0.75)
                pygame.mixer.Sound.play(cheer_sound)
                last_cheer_sfx = cheer_sfx
                while cheer_sfx == last_cheer_sfx:
                    cheer_sfx = random.randint(1, 4)

                goal_sound = pygame.mixer.Sound(mypath('Goal ' + str(goal_sfx) + '.mp3'))
                goal_sound.set_volume(0.75)
                pygame.mixer.Sound.play(goal_sound)
                last_goal_sfx = goal_sfx
                while goal_sfx == last_goal_sfx:
                    goal_sfx = random.randint(1, 5)

            elif self.body.position.x > width - goal_width:
                player_2.score += 1
                scored = True

                cheer_sound = pygame.mixer.Sound(mypath('Cheer ' + str(cheer_sfx) + '.wav'))
                cheer_sound.set_volume(0.7)
                pygame.mixer.Sound.play(cheer_sound)
                last_cheer_sfx = cheer_sfx
                while cheer_sfx == last_cheer_sfx:
                    cheer_sfx = random.randint(1, 4)

                goal_sound = pygame.mixer.Sound(mypath('Goal ' + str(goal_sfx) + '.mp3'))
                goal_sound.set_volume(0.75)
                pygame.mixer.Sound.play(goal_sound)
                last_goal_sfx = goal_sfx
                while goal_sfx == last_goal_sfx:
                    goal_sfx = random.randint(1, 5)


class Player:
    def __init__(self, x, y, direction):
        self.d = direction

        if direction == 'left':
            points = [[-35, -3], [-35, -21], [-30, -30], [-20, -39], [-10, -42], [0, -43], [10, -42], [20, -39],
                      [30, -30], [35, -21], [37, -5], [35, 7], [28, 16], [20, 21], [5, 21], [3, 45], [-22, 45],
                      [-25, 21]]
        else:
            points = [[35, -3], [35, -21], [30, -30], [20, -39], [10, -42], [0, -43], [-10, -42], [-20, -39],
                      [-30, -30], [-35, -21], [-37, -5], [-35, 7], [-28, 16], [-20, 21], [-5, 21], [-3, 45], [22, 45],
                      [25, 21]]

        self.inertia = pymunk.moment_for_poly(head_mass, points, (0, 0))
        self.head_body = pymunk.Body(head_mass, self.inertia)
        self.head_body.position = x, y
        self.head_shape = pymunk.Poly(self.head_body, points)
        self.head_shape.elasticity = 0.3
        self.head_shape.friction = 0.75

        self.leg_body = pymunk.Body(legMass, pymunk.moment_for_box(legMass, (leg_width, leg_height)))
        self.leg_body.position = self.head_body.position - (35 + (leg_width / 2), 0)

        self.leg_shape = pymunk.Poly.create_box(self.leg_body, (leg_width, leg_height))
        self.leg_shape.color = 255, 0, 0, 100
        self.leg_shape.friction = 0
        self.leg_shape.elasticity = 0.65

        if direction == 'left':
            self.joint = pymunk.PivotJoint(self.leg_body, self.head_body, (leg_width / 2, 0), (-50 / 2, -20))
        else:
            self.joint = pymunk.PivotJoint(self.leg_body, self.head_body, (leg_width / 2, 0), (50 / 2, -20))
        self.motor = Motor(self.leg_body, self.head_body, motor_max_force, motor_max_rate, motor_p_gain)

        space.add(self.head_body, self.head_shape)
        space.add(self.leg_body, self.leg_shape)
        space.add(self.joint, self.motor)

        # Prevent collisions with ShapeFilter
        shape_filter = pymunk.ShapeFilter(group=1)
        self.head_shape.filter = shape_filter
        self.leg_shape.filter = shape_filter

        self.score = 0

        self.kicked_ball = False

        self.force = 0
        self.kick = False
        self.start_jump = False
        self.jumping = True
        self.jump_fall = True
        self.increase_jump = False
        self.head_bounce_stopped = False

    def draw(self, head, cleat):
        if self.d == 'left':
            screen.blit(head_surfaces[head], head_surfaces[head].get_rect(
                center=(int(self.head_body.position.x), int(self.head_body.position.y))))

            cleat_x = int(
                self.leg_body.position.x - 0.6 * leg_width * np.sin(self.leg_body.angle - np.deg2rad(300))) + 30
            cleat_y = int(self.leg_body.position.y + 0.6 * leg_width * np.cos(self.leg_body.angle - np.deg2rad(300)))

            cleat_surface = pygame.transform.rotate(original_cleat_surfaces[cleat],
                                                    - 1.2 * (self.leg_body.angle * 180 / math.pi + 70))

        else:
            screen.blit(pygame.transform.flip(head_surfaces[head], True, False), head_surfaces[head].get_rect(
                center=(int(self.head_body.position.x), int(self.head_body.position.y))))

            cleat_x = int(
                self.leg_body.position.x + 0.6 * leg_width * np.cos(self.leg_body.angle - np.deg2rad(150))) - 30
            cleat_y = int(self.leg_body.position.y + 0.6 * leg_width * np.sin(self.leg_body.angle - np.deg2rad(150)))

            cleat_surface = pygame.transform.rotate(pygame.transform.flip(original_cleat_surfaces[cleat], True, False),
                                                    - 1.15 * (self.leg_body.angle * 180 / math.pi + 110))

        screen.blit(cleat_surface, cleat_surface.get_rect(center=(cleat_x, cleat_y)))

    def update(self):
        self.head_body.angular_velocity = 0
        self.head_body.angle = 0

        if not self.kick:
            self.kicked_ball = False
        elif self.leg_shape.shapes_collide(ball.shape).points and not self.kicked_ball:
            pygame.mixer.Sound.play(kick_sound)
            self.kicked_ball = True

        if self.head_body.velocity.y > 0 and self.jumping and not self.jump_fall:
            self.jump_fall = True
        if self.jump_fall and self.head_body.velocity.y < 0 and self.jumping and not self.head_bounce_stopped:
            self.head_body.velocity = (self.head_body.velocity[0] * 1.1, 0)
            self.head_bounce_stopped = True
            self.jumping = False
            self.jump_fall = False

        if self.start_jump:
            if self.head_body.velocity.y < 0 and self.head_body.position.y > 800:
                self.head_shape.body.apply_force_at_local_point((0, (-5500000 - modify('jump')) * fps/60), (0, 0))
                self.head_bounce_stopped = False
                self.jumping = True
                self.start_jump = False
        if self.increase_jump:
            self.head_shape.body.apply_force_at_local_point((0, (300 * self.head_body.velocity[1] - 5000) * fps/60), (0, 0))

        if self.force != 0 and abs(self.head_body.velocity.x) < max_player_speed:
            self.head_shape.body.apply_force_at_local_point(((self.force * 500000) * fps/60, 0), (0, 0))
        else:
            self.head_body.velocity = (self.head_body.velocity.x * 0.9, self.head_body.velocity.y)

        if self.d == 'left':
            if self.kick:
                if np.rad2deg(self.motor.angle()) >= player_1_max_kick + 0.5:
                    self.kick = 'down'
                if self.kick == 'up':
                    self.motor.set_target_angle(np.deg2rad(player_1_max_kick))
                else:
                    if np.rad2deg(self.motor.angle()) > player_1_min_kick + 1:
                        self.motor.set_target_angle(np.deg2rad(player_1_min_kick))
                    else:
                        self.kick = False
        else:
            if self.kick:
                if np.rad2deg(self.motor.angle()) <= player_2_max_kick - 0.5:
                    self.kick = 'down'
                if self.kick == 'up':
                    self.motor.set_target_angle(np.deg2rad(player_2_max_kick))
                else:
                    if np.rad2deg(self.motor.angle()) < player_2_min_kick - 1:
                        self.motor.set_target_angle(np.deg2rad(player_2_min_kick))
                    else:
                        self.kick = False

    def reset(self):
        if self.d == 'right':
            player_1.head_body.position = (width - player_start_x, player_start_y)
        else:
            player_2.head_body.position = (player_start_x, player_start_y)
        self.kicked_ball = False

        self.force = 0
        self.kick = False
        self.start_jump = False
        self.jumping = True
        self.jump_fall = True
        self.increase_jump = False
        self.head_bounce_stopped = False

    def delete(self):
        space.remove(self.head_body, self.head_shape)
        space.remove(self.leg_body, self.leg_shape)
        space.remove(self.joint, self.motor)


def keys():
    global playing, p1_dtap_start, p1_dtap_start, p1_boost_timer, p2_boost_timer
    for event in pygame.event.get():
        window_key_control(event)

        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and not player_1.jumping:
            player_1.start_jump = True
            player_1.increase_jump = True
        if event.type == pygame.KEYUP and event.key == pygame.K_UP:
            player_1.increase_jump = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            player_1.force = 1
            if p1_dtap_start['right'] and time.time() - p1_dtap_start['right'] < dtap_time and p1_boost_timer.get() < 0:
                # p1_boost_wait_start
                print('right double tapped player 1')
                player_1.head_shape.body.apply_force_at_local_point((boost_force, 0), (0, 0))
                p1_dtap_start['right'] = False
                p1_boost_timer = Timer(boost_delay)
                p1_boost_timer.start()
            else:
                p1_dtap_start['right'] = time.time()
        if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT and player_1.force != -1:
            player_1.force = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            player_1.force = -1
            if p1_dtap_start['left'] and time.time() - p1_dtap_start['left'] < dtap_time and p1_boost_timer.get() < 0:
                print('left double tapped player 1')
                player_1.head_shape.body.apply_force_at_local_point((-boost_force, 0), (0, 0))
                p1_dtap_start['left'] = False
                p1_boost_timer = Timer(boost_delay)
                p1_boost_timer.start()
            else:
                p1_dtap_start['left'] = time.time()
        if event.type == pygame.KEYUP and event.key == pygame.K_LEFT and player_1.force != 1:
            player_1.force = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            player_1.kick = 'up'

        if event.type == pygame.KEYDOWN and event.key == pygame.K_w and not player_2.jumping:
            player_2.start_jump = True
            player_2.increase_jump = True
        if event.type == pygame.KEYUP and event.key == pygame.K_w:
            player_2.increase_jump = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            player_2.force = 1
            if p2_dtap_start['right'] and time.time() - p2_dtap_start['right'] < dtap_time and p2_boost_timer.get() < 0:
                print('right double tapped player 2')
                p2_dtap_start['right'] = False
                player_2.head_shape.body.apply_force_at_local_point((boost_force, 0), (0, 0))
                p2_boost_timer = Timer(boost_delay)
                p2_boost_timer.start()
            else:
                p2_dtap_start['right'] = time.time()
        if event.type == pygame.KEYUP and event.key == pygame.K_d and player_2.force != -1:
            player_2.force = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            player_2.force = -1
            if p2_dtap_start['left'] and time.time() - p2_dtap_start['left'] < dtap_time and p2_boost_timer.get() < 0:
                print('left double tapped player 2')
                p2_dtap_start['left'] = False
                player_2.head_shape.body.apply_force_at_local_point((-boost_force, 0), (0, 0))
                p2_boost_timer = Timer(boost_delay)
                p2_boost_timer.start()
            else:
                p2_dtap_start['left'] = time.time()
        if event.type == pygame.KEYUP and event.key == pygame.K_a and player_2.force != 1:
            player_2.force = 0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            player_2.kick = 'up'


if __name__ == "__main__":
    mutator = {}

    # mutator = {'jump': 500000, 'ball size': 50, 'goal height': 75, 'goal width': 10, 'kick': 2}  # Big (not recommended, still testing)
    # mutator = {'jump': 10000, 'kick': 5, 'speed': 300}  # Speedy

    num_cleats = 9
    num_heads = 3

    player_1_cleat = 1
    player_2_cleat = 2

    space = pymunk.Space()
    space.gravity = (0, 900)

    fps = 60
    dt = 1 / fps
    physics_steps_per_frame = 1

    fullscreen = False

    screen_size = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

    x, y = 100, 100
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

    width = 1600
    height = 900
    current_width = width
    current_height = height
    display_window_width = width
    display_window_height = height
    fake_screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
    screen = fake_screen.copy()
    pygame.display.set_caption('Head Soccer')
    clock = pygame.time.Clock()

    draw_options = pymunk.pygame_util.DrawOptions(screen)

    goal_text_color = (230, 230, 230)
    goal_font = pygame.font.Font(mypath('Font.TTF'), 200)
    goal_text = goal_font.render('Goal!', True, goal_text_color)
    goal_text_rect = goal_text.get_rect()
    goal_text_rect.center = (width // 2, 350)

    score_text_color = (220, 220, 220)
    score_font = pygame.font.Font(mypath('Squarely.TTF'), 115)
    score_text = score_font.render('0 - 0', True, score_text_color)

    # gametime_text_color = (220, 220, 220)
    # gametime_font = pygame.font.Font(mypath('Squarely.TTF'), 40)
    # gametime_text = gametime_font.render('6:59', True, gametime_text_color)
    # gametime_text_rect = gametime_text.get_rect()
    # gametime_text_rect.center = (width // 2, 170)

    goal_height = 250 + modify('goal height')
    goal_width = 75 + modify('goal width')
    goal_net = pygame.Surface((goal_width, goal_height), pygame.SRCALPHA)
    goal_net.fill((255, 255, 255, 50))

    left_curve_points = [(1, height * 4 / 7), (width / 35, height * 12 / 50), (width / 7, height / 18),
                         (width * 7 / 20, 1)]
    right_curve_points = [(width * 13 / 20, 1), (width * 6 / 7, height / 18), (width * 34 / 35, height * 12 / 50),
                          (width - 1, height * 4 / 7)]
    floor = [(width - 1, height * 88 / 90), (1, height * 88 / 90)]

    border_points = left_curve_points + right_curve_points + floor + [left_curve_points[0]]

    border = create_borders()
    floor_object = border[-2]

    # pb stands for progress bar
    pb_x, pb_y = 30, 30
    pb_rounding = 10
    pb_width, pb_height = 150, 25
    pb_outline_size = 5

    ball_size = 45 + modify('ball size')
    max_initial_ball_vel = 275
    ball_start_x, ball_start_y = width / 2, 200
    ball_image = pygame.image.load(mypath("Soccer Ball.png"))
    ball_surface = pygame.transform.scale(ball_image, (ball_size, ball_size))
    original_ball_surface = ball_surface
    ball = Ball(ball_start_x, ball_start_y)

    player_start_x, player_start_y = width / 4, 600
    player_1_max_kick, player_1_min_kick = -10, -80
    player_2_max_kick, player_2_min_kick = -170, -100

    head_size = 75
    head_mass = 200
    max_player_speed = 500 + modify('speed')

    character_selection_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    head_scale = {'Nuwan': [1, 1], 'Mihir': [1.05, 1.12], 'Dad': [0.97, 1]}
    heads = ['Nuwan', 'Mihir', 'Dad']
    head_surfaces = {}
    for i in heads:
        head_image = pygame.image.load(mypath(str(i) + '_Head.png'))
        head_surfaces[i] = pygame.transform.scale(head_image, (int(head_size * head_scale[i][0]), int(
            head_scale[i][1] * head_size / head_image.get_size()[0] * head_image.get_size()[1])))

    cleat_size = 50
    original_cleat_surfaces = {}
    for i in range(1, num_cleats + 1):
        cleat_image = pygame.image.load(mypath('Cleat ' + str(i) + '.png'))
        original_cleat_surfaces[i] = pygame.transform.scale(cleat_image, (
            cleat_size, int(cleat_size / cleat_image.get_size()[0] * cleat_image.get_size()[1])))

    leg_width = 60
    leg_height = 10
    legMass = 10
    # default_leg_elasticity = 0.65

    motor_max_force = np.inf
    motor_max_rate = 15 + modify('kick')
    motor_p_gain = 40

    # playsound.playsound('', False)
    kick_sound = pygame.mixer.Sound(mypath('kick_ball.wav'))
    kick_sound.set_volume(0.95)

    countdown_sound = pygame.mixer.Sound(mypath('Countdown.mp3'))
    countdown_sound.set_volume(0.75)

    selection_sound = pygame.mixer.Sound(mypath('Small_pop.wav'))
    selection_sound.set_volume(0.75)

    start_game_sound = pygame.mixer.Sound(mypath('Start_Game.wav'))
    start_game_sound.set_volume(0.75)

    pygame.mixer.music.load(mypath('background_crowd.wav'))
    pygame.mixer.music.set_volume(0.15)

    goal_sfx = 1
    cheer_sfx = 1

    p1_start_info = {'head': 'Mihir', 'cleat': 8}
    p2_start_info = {'head': 'Nuwan', 'cleat': 3}

    # sw stands for Selection Wheel
    sw_pos_info = [500, 500, 200]  # [x, y, y diff to cleat wheel]
    p1_hs_pos = [width - sw_pos_info[0], sw_pos_info[1]]
    p2_hs_pos = [sw_pos_info[0], sw_pos_info[1]]
    p1_cs_pos = [width - sw_pos_info[0], sw_pos_info[1] + sw_pos_info[2]]
    p2_cs_pos = [sw_pos_info[0], sw_pos_info[1] + sw_pos_info[2]]
    sw_outline_size = [400, 150]
    # Corners are as round as the height, meaning the sides are semicircles
    # sw_outline_rounding = sw_outline_size[1] // 2
    sw_outline_rounding = 60
    sw_smoothing = 5

    # dtap stands for Double Tap
    dtap_time = 0.3
    p1_dtap_start, p2_dtap_start = {'right': False, 'left': False}, {'right': False, 'left': False}
    boost_delay = 20
    boost_force = 30000000

    scored = False

    next_screen = 'customize'

    # fix customize and playing variables
    # do next what you have to do (next_screen)

    while True:
        customization_screen(p1_start_info, p2_start_info)

        p1_boost_timer, p2_boost_timer = Timer(boost_delay), Timer(boost_delay)
        p1_boost_timer.start()
        p2_boost_timer.start()
        winner = play_game(10)
        next_screen = end_screen(winner)
