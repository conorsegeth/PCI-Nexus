from PIL import Image
import pygame as pg
from pygame.math import Vector2
from pygame.surface import Surface
from vi import Simulation, Agent
from vi.config import Config, dataclass, deserialize
from vi.simulation import HeadlessSimulation
import random

class Cockroach(Agent):
    def __init__(self, images: list[Surface], simulation: HeadlessSimulation, pos: Vector2 | None = None, move: Vector2 | None = None):
        super().__init__(images, simulation, pos, move)
        self.state = "wandering"
        self.direction = self.move.normalize()
        self.velocity = simulation.config.movement_speed

        self.left_on_tick = float('inf')
    
    def update(self):
        if self.in_proximity_accuracy().count() >= 1:
            self.change_image(1)
        else:
            self.change_image(0)

        if self.state == 'wandering':
            self.continue_movement()

            # Change state to join if agent currently on a site
            if self.on_site():
                self.state = 'join'
    
        elif self.state == 'join':
            # If agents go off the site change back to wandering (prevents stopping after leaving the site)
            if not self.on_site():
                self.state = 'wandering'

            # Join with some probability every 50 ticks
            if self.shared.counter % 50 == 0:
                if random.random() < 0.7:
                    self.state = 'still'
        
        elif self.state == 'still':
            self.freeze_movement()

            # Enter leave state with some probability every 50 ticks
            if self.shared.counter % 50 == 0:
                if random.random() < 0.02:
                    self.left_tick = self.shared.counter
                    self.state = 'leave'
        
        else:
            # Continue movement & don't enter wandering again for some number of ticks
            self.continue_movement()
            if self.shared.counter == self.left_on_tick + 500:
                self.state = 'wandering'
            


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

site = Image.open('PCI-Nexus/images/circle.png')
site = site.resize((200,200))
site.save('PCI-Nexus/images/circle_resized.png')

(
    Simulation(
        Config(
            image_rotation=False,
            movement_speed=1,
            radius=50
        )
    )
    .spawn_site("PCI-Nexus/images/circle_resized.png", x // 2, y // 2)
    .batch_spawn_agents(20, Cockroach, ["PCI-Nexus/images/white.png", "PCI-Nexus/images/red.png"])
    .run()
)

