from PIL import Image
import pygame as pg
from pygame.math import Vector2
from pygame.surface import Surface
from vi import Simulation, Agent
from vi.config import Config, dataclass, deserialize
from vi.simulation import HeadlessSimulation
import random

@deserialize
@dataclass
class AggregationConfig(Config):
    delta_time: float = 0.1

class Cockroach(Agent):
    def __init__(self, images: list[Surface], simulation: HeadlessSimulation, pos: Vector2 | None = None, move: Vector2 | None = None):
        super().__init__(images, simulation, pos, move)
        self.state = "wandering"
        self.direction = self.move.normalize()
        self.velocity = AggregationConfig().movement_speed
    
    def update(self):
        if self.state == 'wandering':
            self.continue_movement()
            if self.on_site():
                self.state = 'join'
    
        elif self.state == 'join':
            pass

    def change_position(self):
        if not self._moving:
            return

        self.direction = self.move.normalize()

        if self.pos.x + (self.direction.x * 5) < self._area.left:
            self.direction.x *= -1
        elif self.pos.x + (self.direction.x * 5) > self._area.right:
            self.direction.x *= -1
        elif self.pos.y + (self.direction.y * 5) < self._area.top:
            self.direction.y *= -1
        elif self.pos.y + (self.direction.y * 5) > self._area.bottom:
            self.direction.y *= -1

        if random.random() < 0.001:
            self.direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            self.direction = self.direction.normalize()

        self.move = self.direction * self.velocity
        self.pos += self.move
    

config = Config()
x, y = config.window.as_tuple()

site = Image.open('images/circle.png')
site = site.resize((200,200))
site.save('images/circle_resized.png')

(
    Simulation(
        AggregationConfig(
            image_rotation=False,
            movement_speed=0.5,
            radius=50
        )
    )
    .spawn_site("images/circle_resized.png", x // 2, y // 2)
    .batch_spawn_agents(4, Cockroach, ["images/white.png", "images/red.png"])
    .run()
)

