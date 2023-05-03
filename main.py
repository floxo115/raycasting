import enum

import pygame as pg
import numpy as np
from typing import Type


class AppConfig():
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 800

    HORIZONTAL_CELLS = 20
    VERTICAL_CELLS = 20

    BLOCK_HEIGHT = WINDOW_HEIGHT // HORIZONTAL_CELLS
    BLOCK_WIDTH = WINDOW_WIDTH // VERTICAL_CELLS

    MAX_TICKS = 60
    DISPLAY_DLL_HITS = True

    world = np.random.random((HORIZONTAL_CELLS, VERTICAL_CELLS))
    world[world > 0.95] = 1
    world[world <= 0.95] = 0
    world[0, :] = 1
    world[-1, :] = 1
    world[:, 0] = 1
    world[:, -1] = 1


class Side(enum.Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


def x_to_draw_x(x: int, appconfig: Type[AppConfig]):
    return x * appconfig.WINDOW_WIDTH / appconfig.HORIZONTAL_CELLS


def y_to_draw_y(x: int, appconfig: Type[AppConfig]):
    return appconfig.WINDOW_HEIGHT - x * appconfig.WINDOW_WIDTH / appconfig.HORIZONTAL_CELLS


def vec_to_draw_coord(point, appconfig: Type[AppConfig]):
    x = x_to_draw_x(point[0], appconfig)
    y = y_to_draw_y(point[1], appconfig)

    return x, y


def rotate(pos, angle):
    return np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]) @ pos


def draw_grid(surface: pg.Surface, appconfig: Type[AppConfig]):
    for row in range(1, appconfig.HORIZONTAL_CELLS):
        pg.draw.line(surface, "grey", (0, appconfig.BLOCK_HEIGHT * row),
                     (appconfig.WINDOW_WIDTH, appconfig.BLOCK_HEIGHT * row), 1)
    for col in range(1, appconfig.VERTICAL_CELLS):
        pg.draw.line(surface, "grey", (appconfig.BLOCK_WIDTH * col, 0),
                     (appconfig.BLOCK_WIDTH * col, appconfig.WINDOW_HEIGHT,), 1)


def draw_blocks(surface: pg.Surface, appconfig: Type[AppConfig]):
    for row in range(0, appconfig.HORIZONTAL_CELLS):
        for col in range(0, appconfig.VERTICAL_CELLS):
            if appconfig.world[row, col] == 1:
                rect = pg.Rect(
                    appconfig.BLOCK_WIDTH * col,
                    appconfig.WINDOW_HEIGHT - appconfig.BLOCK_HEIGHT * (row + 1),
                    appconfig.BLOCK_WIDTH,
                    appconfig.BLOCK_HEIGHT
                )
                pg.draw.rect(surface, "blue", rect)


def ddl(pos, direction, appconfig: Type[AppConfig]) -> (float, Side):
    direction = direction / np.linalg.norm(direction)
    is_looking_up = direction[1] > 0
    is_looking_right = direction[0] > 0

    cur_x = np.floor(pos[0])
    cur_y = np.floor(pos[1])

    # compute the y-slope (how many y per one x) and x-slope (how many x per one y)
    try:
        slope_y = direction[1] / direction[0]
    except ZeroDivisionError:
        slope_y = float("inf")
    try:
        slope_x = direction[0] / direction[1]
    except ZeroDivisionError:
        slope_x = float("inf")

    # compute the orthogonal distances to the next x and y line
    if is_looking_up:
        dist_orth_y = np.abs(np.floor(pos[1]) + 1 - pos[1])
    else:
        dist_orth_y = np.abs(np.floor(pos[1]) - pos[1])

    if is_looking_right:
        dist_orth_x = np.abs(np.floor(pos[0]) + 1 - pos[0])
    else:
        dist_orth_x = np.abs(np.floor(pos[0]) - pos[0])

    # compute the directional distance to next x and y line
    dist_cross_x = np.sqrt(dist_orth_x ** 2 + (dist_orth_x * slope_y) ** 2)
    dist_cross_y = np.sqrt(dist_orth_y ** 2 + (dist_orth_y * slope_x) ** 2)

    step_x = 1 if is_looking_right else -1
    step_y = 1 if is_looking_up else -1

    hit_side = None
    dist = 0
    while True:
        if dist_cross_x < dist_cross_y:
            cur_x += step_x
            point_x = cur_x
            point_y = np.floor(pos[1] + dist_cross_x * direction[1])
            if appconfig.world[int(point_y), int(point_x)]:
                dist = dist_cross_x
                if is_looking_right:
                    hit_side = Side.WEST
                else:
                    hit_side = Side.EAST
            dist_cross_x += np.sqrt(1 + slope_y ** 2)
        else:
            cur_y += step_y
            point_y = cur_y
            point_x = np.floor(pos[0] + dist_cross_y * direction[0])
            if appconfig.world[int(point_y), int(point_x)]:
                dist = dist_cross_y
                if is_looking_up:
                    hit_side = Side.SOUTH
                else:
                    hit_side = Side.NORTH
            dist_cross_y += np.sqrt(1 + slope_x ** 2)

        if hit_side:
            break

    return dist, hit_side


class Game:
    def __init__(self, appconfig: Type[AppConfig]):
        self.appconfig = appconfig

        self.clock = pg.time.Clock()

        self.window = pg.display.set_mode((appconfig.WINDOW_WIDTH, appconfig.WINDOW_HEIGHT), vsync=True)
        pg.display.set_caption("ddl test")
        self.window.fill("black")

        self.player = Player(np.array([5., 5.]), np.array([1., 1.]) / np.sqrt(2), np.array([-1, 1]), appconfig)

        self.quit = False

    def draw(self):
        self.window.fill("black")
        draw_blocks(self.window, self.appconfig)
        draw_grid(self.window, self.appconfig)

        self.player.draw(self.window)

        if self.appconfig.DISPLAY_DLL_HITS:
            for i in range(1, 50):
                dir = self.player.direction + self.player.camera / 50 * i
                dir = dir / np.linalg.norm(dir)
                dist, _ = ddl(self.player.pos, dir, self.appconfig)
                pg.draw.circle(self.window, "green",
                               vec_to_draw_coord(self.player.pos + dir * dist, self.appconfig), 6)

                dir = self.player.direction - self.player.camera / 50 * i
                dir = dir / np.linalg.norm(dir)
                dist, _ = ddl(self.player.pos, dir, self.appconfig)
                pg.draw.circle(self.window, "green",
                               vec_to_draw_coord(self.player.pos + dir * dist, self.appconfig), 6)
            dist, _ = ddl(self.player.pos, self.player.direction, self.appconfig)
            pg.draw.circle(self.window, "red",
                           vec_to_draw_coord(self.player.pos + self.player.direction * dist, self.appconfig), 6)

        pg.display.flip()

    def run(self):
        while not self.quit:
            delta = self.clock.tick(60) / 1000
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit = True

            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT]:
                self.player.rotate(0.5, delta)
            if keys[pg.K_RIGHT]:
                self.player.rotate(-0.5, delta)
            if keys[pg.K_UP]:
                self.player.move(0.1, delta)
            if keys[pg.K_DOWN]:
                self.player.move(-0.1, delta)
            if keys[pg.K_s]:
                self.player.direction += 0.1
            if keys[pg.K_a]:
                if np.all(self.player.direction) > 0.1:
                    self.player.direction -= 0.1

            self.draw()


class Player:
    def __init__(self, pos, direction, camera, appconfig: Type[AppConfig]):
        self.appconfig = appconfig
        self.pos = pos
        self.direction = direction
        self.camera = camera

    def rotate(self, angle, delta):
        self.direction = rotate(self.direction, angle * 2 * np.pi * delta)
        self.camera = rotate(self.camera, angle * 2 * np.pi * delta)

    def move(self, speed, delta):
        self.pos += self.direction / np.linalg.norm(self.direction) * speed

    def draw(self, surface):
        pg.draw.circle(surface, "yellow", vec_to_draw_coord(self.pos, self.appconfig), 10)
        pg.draw.line(surface, "green", vec_to_draw_coord(self.pos, self.appconfig),
                     vec_to_draw_coord(self.pos + self.direction, self.appconfig), 2)
        pg.draw.line(surface, "grey", vec_to_draw_coord(self.pos + self.direction, self.appconfig),
                     vec_to_draw_coord(self.pos + self.direction + self.camera, self.appconfig), 2)
        pg.draw.line(surface, "grey", vec_to_draw_coord(self.pos + self.direction, self.appconfig),
                     vec_to_draw_coord(self.pos + self.direction - self.camera, self.appconfig), 2)


if __name__ == "__main__":
    game = Game(AppConfig)
    game.run()
