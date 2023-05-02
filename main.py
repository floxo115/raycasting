import pygame as pg
import numpy as np
from typing import Type


class AppConfig():
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 1000

    HORIZONTAL_CELLS = 20
    VERTICAL_CELLS = 20

    BLOCK_HEIGHT = WINDOW_HEIGHT // HORIZONTAL_CELLS
    BLOCK_WIDTH = WINDOW_WIDTH // VERTICAL_CELLS

    MAX_TICKS = 60

    world = np.zeros((HORIZONTAL_CELLS, VERTICAL_CELLS))
    world[0, :] = 1
    world[-1, :] = 1
    world[:, 0] = 1
    world[:, -1] = 1
    world[4,5] = 1
    world[4,6] = 1
    world[5,5] = 1


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
        pg.draw.line(surface, "white", (0, appconfig.BLOCK_HEIGHT * row),
                     (appconfig.WINDOW_WIDTH, appconfig.BLOCK_HEIGHT * row), 1)
    for col in range(1, appconfig.VERTICAL_CELLS):
        pg.draw.line(surface, "white", (appconfig.BLOCK_WIDTH * col, 0),
                     (appconfig.BLOCK_WIDTH * col, appconfig.WINDOW_HEIGHT,), 1)


def draw_blocks(surface: pg.Surface, appconfig: Type[AppConfig]):
    for row in range(appconfig.HORIZONTAL_CELLS - 1, -1, -1):
        for col in range(0, appconfig.VERTICAL_CELLS):
            if appconfig.world[row, col] == 1:
                rect = pg.Rect(
                    appconfig.BLOCK_HEIGHT * row,
                    appconfig.BLOCK_WIDTH * col,
                    appconfig.BLOCK_WIDTH,
                    appconfig.BLOCK_HEIGHT
                )
                pg.draw.rect(surface, "magenta", rect)



class Game:
    def __init__(self, appconfig: Type[AppConfig]):
        self.appconfig = appconfig

        self.clock = pg.time.Clock()

        self.window = pg.display.set_mode((appconfig.WINDOW_WIDTH, appconfig.WINDOW_HEIGHT), vsync=True)
        pg.display.set_caption("ddl test")
        self.window.fill("black")

        self.player = Player(np.array([5., 5.]), np.array([1., 1.]), 5 * np.array([-1 / 5, 1 / 5]), appconfig)

        self.quit = False

    def draw(self):
        self.window.fill("black")
        draw_grid(self.window, self.appconfig)
        draw_blocks(self.window, self.appconfig)
        self.player.draw(self.window)
        pg.display.flip()

    def run(self):
        while not self.quit:
            delta = self.clock.tick(60) / 1000
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit = True

            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT]:
                self.player.rotate(1, delta)
            if keys[pg.K_RIGHT]:
                self.player.rotate(-1, delta)
            if keys[pg.K_UP]:
                self.player.move(0.1, delta)
            if keys[pg.K_DOWN]:
                self.player.move(-0.1, delta)

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
        self.pos += self.direction * speed

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
