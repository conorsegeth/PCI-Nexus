import math
import random
from typing import Tuple
from pygame.math import Vector2
from pygame.surface import Surface
from vi import Agent, ProximityIter, Simulation

predatorImages = ['images/foxsmolish.png']
preyImages = ['images/rabbitsmol.png']

EAT_DISTANCE = 10
TIMESTEP_INTERVAL = 6  # 0.1 seconds (assuming 60fps)


class MyBaseAgent(Agent):
    def __init__(self, images: list[Surface], simulation: Simulation, pos: Vector2 | None = None,
                 move: Vector2 | None = None):
        super().__init__(images, simulation, pos, move)
        self.simulation = simulation
        
        self.energy = 100
        self.energy_consumption = 0.25

        self.ate = self.shared.counter

    def update(self):
        if self.shared.counter % TIMESTEP_INTERVAL == 0:
            self.energy -= self.energy_consumption
            if self.energy <= 0:
                self.kill()

    # Basic random movement for base class (could override later in prey/predator class to give unique movement)
    def change_position(self):
        if not self._moving:
            return

        self.there_is_no_escape()

        self.direction = self.move.normalize()

        if random.random() < 0.1:
            self.direction = Vector2(
                random.uniform(self.direction.x - 0.35, self.direction.x + 0.35),
                random.uniform(self.direction.y - 0.35, self.direction.y + 0.35)
            )
            self.direction = self.direction.normalize()

        self.move = self.direction
        self.pos += self.move


class Grass(MyBaseAgent):
    def update(self):
        self.save_data('type', 'Grass')
        if hasattr(self.simulation, "seasons"):
            self.save_data('season', list(self.simulation.seasons.keys())[self.simulation.season_idx])

    def change_position(self):
        pass


PREY_EAT_COOLDOWN = 30
PREY_ENERGY_REGAIN = 15
PREY_REPRODUCTION_CHANCE = 0.8

class Prey(MyBaseAgent):
    def update(self):
        self.save_data('type', 'Prey')
        if hasattr(self.simulation, "seasons"):
            self.save_data('season', list(self.simulation.seasons.keys())[self.simulation.season_idx])

        super().update()

        # Only perform actions every timestep
        if self.shared.counter % TIMESTEP_INTERVAL == 0:  
            self._reset_ate()

            neighbors = self.in_proximity_accuracy()
            for neighbor, distance in neighbors:
                if self._can_eat(neighbor, distance):
                    self.eat(neighbor)

                    if random.random() < PREY_REPRODUCTION_CHANCE:
                        self.reproduce()

    def _reset_ate(self):
        if self.shared.counter > self.ate + PREY_EAT_COOLDOWN:
            self.ate = -float('inf')

    def _can_eat(self, agent, distance):
        if isinstance(agent, Grass) and distance < EAT_DISTANCE and self.ate < 0:
            return True
        return False

    def eat(self, agent):
        agent.kill()
        self.ate = self.shared.counter
        self.energy = min(100, self.energy + PREY_ENERGY_REGAIN)


class Predator(MyBaseAgent):
    def __init__(self, images: list[Surface], simulation: Simulation, pos: Vector2 | None = None,
                 move: Vector2 | None = None):
        super().__init__(images, simulation, pos, move)
        self.ate = -float('inf')

    def update(self):
        self.save_data('type', 'Predator')

        # Only perform actions every timestep
        if self.shared.counter % TIMESTEP_INTERVAL == 0:
            # If predator ate more than 45 frames ago, let it eat again
            if self.shared.counter > self.ate + 30:  # 30
                self.ate = -float('inf')

            neighbors = self.in_proximity_accuracy()
            for agent, distance in neighbors:
                # Check which prey are within eating distance
                if distance <= EAT_DISTANCE and isinstance(agent, Prey) and self.ate < 0:
                    agent.kill()
                    self.ate = self.shared.counter

                    # Chance to spawn another predator after eating
                    if random.random() < 0.38:  # 0.374
                        self.reproduce()
                        # print("ate a mf")

            # Chance to die randomly
            if random.random() < 0.0088:  # 0.0088
                self.kill()


class PredatorWithEnergy(Predator):
    def __init__(self, images: list[Surface], simulation: Simulation, pos: Vector2 | None = None,
                 move: Vector2 | None = None):
        super().__init__(images, simulation, pos, move)

    def update(self):
        self.save_data('type', 'Predator')
        if hasattr(self.simulation, "seasons"):
            self.save_data('season', list(self.simulation.seasons.keys())[self.simulation.season_idx])

        # Only perform actions every timestep
        if self.shared.counter % TIMESTEP_INTERVAL == 0:
            self.energy -= 0.25
            if self.energy == 0:
                self.kill()

            # If predator ate more than some amount of frames ago, let it eat again
            if self.shared.counter > self.ate + 30:
                self.ate = -float('inf')

            neighbors = self.in_proximity_accuracy()
            for agent, distance in neighbors:
                # Check which prey are within eating distance
                if distance <= EAT_DISTANCE and isinstance(agent, Prey) and self.ate < 0:
                    agent.kill()
                    self.energy = min(100, self.energy + 30)
                    self.ate = self.shared.counter

                    # Chance to spawn another predator after eating
                    if random.random() < 0.075:
                        self.reproduce()
                        # print("ate a mf")

            # Chance to die randomly
            if random.random() < self._calculate_death_probability(self.energy):
                self.kill()

    def _calculate_death_probability(self, energy: float) -> float:
        a = 0.1
        prob = math.e ** (-a * energy)
        return prob

    def change_position(self):
        if not self._moving:
            return

        self.there_is_no_escape()

        self.direction = self.move.normalize()

        neighbors = self.in_proximity_accuracy()
        exists, target = self._get_closest_target(neighbors)
        if exists:
            targetDir = (target.pos - self.pos).normalize()
            self.direction += 0.03 * targetDir
            self.direction = self.direction.normalize()
        else:
            if random.random() < 0.1:
                self.direction = Vector2(
                    random.uniform(self.direction.x - 0.35, self.direction.x + 0.35),
                    random.uniform(self.direction.y - 0.35, self.direction.y + 0.35)
                )
                self.direction = self.direction.normalize()

        speed = max(0.7, self.energy / 75)

        self.move = self.direction * speed
        self.pos += self.move

    def _get_closest_target(self, neighbors: ProximityIter) -> Tuple[bool, Prey]:
        closestDist = float('inf')
        closestTarget = None

        for agent, distance in neighbors:
            if isinstance(agent, Prey) and distance < closestDist:
                closestDist = distance
                closestTarget = agent

        if closestTarget != None:
            return True, closestTarget

        return False, None
