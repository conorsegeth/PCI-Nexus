from math import sqrt
from enum import Enum, auto

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.005
    separation_weight: float = 0.25

    delta_time: float = 3

    mass: int = 20

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        
        self.direction = self.move.normalize()
        self.velocity = 2

        neighborhood = self.in_proximity_accuracy()
        num_neighbors = self.in_proximity_accuracy().count()

        if num_neighbors > 0:
            total_dirs = self.direction.copy()
            total_separation = pg.Vector2(0, 0)
            total_pos = pg.Vector2(0, 0)
            for agent, distance in neighborhood:
                # Calculate sum of direction for alignment
                total_dirs += agent.direction

                # Calculate difference in position to neighboring boids
                pos_diff = self.pos - agent.pos
                total_separation += pos_diff

                # Calculate total position of neighboring boids
                total_pos += agent.pos

            # Calculate average direction for alignment
            avg_dir = total_dirs / num_neighbors
            avg_dir = avg_dir.normalize()
            
            # alignment = avg_dir - self.direction

            # Calculate average difference in position for separation
            avg_separation_dir = total_separation / num_neighbors
            avg_separation_dir = avg_separation_dir.normalize()

            # Calculate average position of neighbors & cohesion force
            avg_pos = total_pos / num_neighbors
            cohesion_force = avg_pos - self.pos
            cohesion = cohesion_force - self.direction

            
            self.move = self.direction + (FlockingConfig().alignment_weight * avg_dir) + (FlockingConfig().separation_weight * avg_separation_dir) + (FlockingConfig().cohesion_weight * cohesion) 
            self.move = self.move.normalize()


        self.pos += self.move * self.velocity



class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        print(f"A: {a:.3f} - C: {c:.3f} - S: {s:.3f}")


(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=100,
            seed=1,
        )
    )
    .batch_spawn_agents(80, Bird, images=["PCI-Nexus/assignment0/images/bird.png"])
    .run()
)
