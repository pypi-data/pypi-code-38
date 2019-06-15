# todo : split engine from graphical engine
# todo : remove is_alive from Particle
# todo : remove dead particle
# todo : display only if in screen

import time
from tkinter import Tk
from typing import List, Tuple

import pygame

from physics import Particle, Law
from utils import Number


class GraphicalParticle(Particle):
    def __init__(self, universe: "Universe", mass: Number, position: List[Number], velocity: List[Number]):
        super().__init__(mass, position, velocity)
        self.universe = universe
        self.old_graphical_position = [0, 0]
        self.present_graphical_position = [0, 0]

    @property
    def color(self) -> Tuple[Number, Number, Number]:
        raise NotImplementedError

    @property
    def dimension(self) -> Number:
        raise NotImplementedError

    @property
    def graphical_dimension(self):
        return max(1, self.dimension / self.universe.zoom_level)

    @property
    def graphical_position(self):
        self.old_graphical_position = self.present_graphical_position
        self.present_graphical_position = (
            (self.position[0] / self.universe.zoom_level) + (self.universe.width / 2),
            (self.position[1] / self.universe.zoom_level) + (self.universe.height / 2),
        )
        return self.present_graphical_position


class Universe:
    def __init__(
        self,
        width: Number = None,
        height: Number = None,
        zoom_level: Number = 1,
        draw_trajectory=False,
        sync_time=False,
    ):
        pygame.init()
        self.zoom_level = zoom_level  # 1 is normal, 2 is twice un-zoomed, 0.5 is twice zoomed
        self.sync_time = sync_time
        self.draw_trajectory = draw_trajectory
        if width is None or height is None:
            screen = Tk()
        self.height = height or screen.winfo_screenheight()
        self.width = width or screen.winfo_screenwidth()
        self._units: List[GraphicalParticle] = []
        self._window = pygame.display.set_mode((self.width, self.height))
        self.laws: List[Law] = []
        self._next_zoom_delta = 0
        self._shift = [0, 0]
        self._next_shift = [0, 0]
        self._texts_to_display = []
        self._texts_to_erase = []
        self._font_size = 20
        self._font = pygame.font.SysFont(None, self._font_size)
        self.must_erase_screen = False

    def add_unit(self, particle: GraphicalParticle):
        self._units.append(particle)

    def erase_units(self) -> None:
        for particle in self._units:
            if particle.is_alive or True:
                gd = round(particle.graphical_dimension)
                pygame.draw.circle(
                    self._window,
                    (0, 0, 0),
                    (
                        round(particle.old_graphical_position[0] + self._shift[0]),
                        round(particle.old_graphical_position[1] + self._shift[1]),
                    ),
                    gd * 2,
                    gd * 2,
                )

    def render_units(self) -> None:
        for particle in self._units:
            if particle.is_alive:
                gp = particle.graphical_position
                pygame.draw.circle(
                    self._window,
                    particle.color,
                    (round(gp[0] + self._shift[0]), round(gp[1] + self._shift[1])),
                    round(particle.graphical_dimension),
                    round(particle.graphical_dimension),
                )

    def apply_laws(self):
        for law in self.laws:
            for particle in self._units:
                if particle.is_alive:
                    for other_particle in self._units:
                        if other_particle.is_alive and particle != other_particle:
                            particle.apply_force(law.compute_force(particle, other_particle))

    def update_particle_positions(self):
        for unit in self._units:
            if unit.is_alive:
                unit.exist()

    def ask_for_zoom(self, level_delta):
        if self._next_zoom_delta + level_delta + self.zoom_level >= 1:
            self._next_zoom_delta += level_delta

    def zoom(self):
        if self._next_zoom_delta and self.draw_trajectory:
            self.ask_for_erase_screen()
        self.zoom_level += self._next_zoom_delta
        self._next_zoom_delta = 0

    def ask_for_erase_screen(self):
        self.must_erase_screen = True

    def erase_screen(self):
        if self.must_erase_screen:
            pygame.draw.rect(self._window, (0, 0, 0), ((0, 0), (self.width, self.height)))
            self.must_erase_screen = False

    def ask_for_shift(self, shift_level):
        self._next_shift = shift_level

    def shift(self):
        if self._next_shift != [0, 0]:
            self.ask_for_erase_screen()
        self._shift[0] += self._next_shift[0]
        self._shift[1] += self._next_shift[1]
        self._next_shift = [0, 0]

    def display_text(self):
        next_pos = [0, 0]
        while self._texts_to_display:
            text = self._texts_to_display.pop(0)
            self._texts_to_erase.append(text)
            text_surface = self._font.render(text, True, (255, 255, 255), (0, 0, 0))
            self._window.blit(text_surface, next_pos)
            next_pos[1] += self._font_size

    def erase_text(self):
        next_pos = [0, 0]
        while self._texts_to_erase:
            text = self._texts_to_erase.pop(0)
            text_surface = self._font.render(text, True, (255, 255, 255), (255, 255, 255))
            self._window.blit(text_surface, next_pos)
            next_pos[1] += self._font_size

    def ask_for_text_display(self, text: str):
        self._texts_to_display.append(text)

    def loop(self):
        run = True
        total_time = 0
        while run:
            try:
                total_time += 1

                if not self.draw_trajectory:
                    self.erase_units()
                self.erase_screen()
                self.zoom()
                self.shift()
                self.render_units()
                self.apply_laws()
                self.update_particle_positions()

                self.ask_for_text_display(str(total_time))
                alive_particles = [p for p in self._units if p.is_alive]
                self.ask_for_text_display(str(len(alive_particles)))
                self.ask_for_text_display(
                    str(round(sum([(sum(p.velocity) / 2) * p.mass for p in alive_particles]), 5))
                )

                self.erase_text()
                self.display_text()

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4:  # scroll up
                            self.ask_for_zoom(-1)
                        elif event.button == 5:  # scroll down
                            self.ask_for_zoom(1)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.ask_for_shift((-100, 0))
                        elif event.key == pygame.K_RIGHT:
                            self.ask_for_shift((100, 0))
                        elif event.key == pygame.K_UP:
                            self.ask_for_shift((0, -100))
                        elif event.key == pygame.K_DOWN:
                            self.ask_for_shift((0, 100))

                if self.sync_time:
                    time.sleep(0.01)

            except KeyboardInterrupt:
                run = False
        print(total_time)
