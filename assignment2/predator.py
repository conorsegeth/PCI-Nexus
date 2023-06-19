from typing import Optional
from pygame.math import Vector2
from pygame.surface import Surface
from vi import Agent
from vi.simulation import HeadlessSimulation

class Predator(Agent):
    def __init__(self, images: list[Surface], simulation: HeadlessSimulation, pos: Vector2 | None = None, move: Vector2 | None = None):
        super().__init__(images, simulation, pos, move)

    def change_position(self):
        return super().change_position()