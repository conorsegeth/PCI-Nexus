import random
from typing import Optional
from pygame.math import Vector2
from pygame.surface import Surface
from vi import Agent
from vi.simulation import HeadlessSimulation
from sim import MySimulation

predatorImages = ["images/foxsmolish.png"]
preyImages = ["images/rabbitsmol.png"]
grassImages = ["images/green.png"]

EAT_DISTANCE = 12
TIME_SINCE_KILL = 0
TIMESTEP_INTERVAL = 6  # 0.1 seconds (assuming 60fps)


class MyBaseAgent(Agent):
    def __init__(self, images: list[Surface], simulation: MySimulation, pos: Optional[Vector2] = None, move: Optional[Vector2] = None):
        super().__init__(images, simulation, pos, move)
        self.simulation = simulation
        self.velocity = 1
    
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

        self.move = self.direction *self.velocity
        self.pos += self.move
    


class Predator(MyBaseAgent):
    def __init__(self, images: list[Surface], simulation: MySimulation, pos: Optional[Vector2] = None, move: Optional[Vector2] = None):
        super().__init__(images, simulation, pos, move)
        self.simulation = simulation
        self.ate = -float('inf')
       

    def update(self):
        self.save_data('type', 'Predator')

        # Only perform actions every timestep
        if self.shared.counter % TIMESTEP_INTERVAL == 0:
            # If predator ate more than 45 frames ago, let it eat again
            if self.shared.counter > self.ate + 45:
                self.ate = -float('inf')

            neighbors = self.in_proximity_accuracy()
            for agent, distance in neighbors:
                # Check which prey are within eating distance
                if distance <= EAT_DISTANCE and isinstance(agent, Prey) and self.ate < 0:
                    agent.kill()
                    self.velocity = 1
                    # Chance to spawn another predator after eating
                    if random.random() < 0.5:
                        self.reproduce()
                        self.ate = self.shared.counter
                        # print("ate a mf") 
                else:
                    self.velocity -= 0.01

            # Chance to die randomly
            if random.random() < 0.01:
                self.kill()
            #change speed
            #count timesteps
            #use timemachine



class Prey(MyBaseAgent):
    def __init__(self, images: list[Surface], simulation: MySimulation, pos: Optional[Vector2] = None, move: Optional[Vector2] = None):
        super().__init__(images, simulation, pos, move)
        self.simulation = simulation
        self.ate = -float('inf')
       

    def update(self):
        self.save_data('type', 'Prey')

        # Only perform actions every timestep
        if self.shared.counter % TIMESTEP_INTERVAL == 0:
            # If predator ate more than 45 frames ago, let it eat again
            if self.shared.counter > self.ate + 45:
                self.ate = -float('inf')

            neighbors = self.in_proximity_accuracy()
            for agent, distance in neighbors:
                # Check which prey are within eating distance
                if distance <= EAT_DISTANCE and isinstance(agent, Grass) and self.ate < 0:
                    agent.kill()
                    self.velocity = 1
                    # Chance to spawn another predator after eating
                    if random.random() < 0.5:
                        self.reproduce()
                        self.ate = self.shared.counter
                        # print("ate a mf") 
                else:
                    self.velocity -= 0.01

            # Chance to die randomly
            if random.random() < 0.01:
                self.kill()
#class Prey(MyBaseAgent):
    #def __init__(self, images: list[Surface], simulation: MySimulation, pos: Optional[Vector2] = None, move: Optional[Vector2] = None):
        #super().__init__(images, simulation, pos, move)
        #self.simulation = simulation

    #def update(self):
        #self.save_data('type', 'Prey')

        # Only perform actions every timestep : random chance to reproduce

        #if self.shared.counter % TIMESTEP_INTERVAL == 0 and random.random() < 0.0072:
            #self.reproduce()
            # print("split")

class Grass(MyBaseAgent):
    def __init__(self, images: list[Surface], simulation: MySimulation, pos: Optional[Vector2] = None, move: Optional[Vector2] = None):
        super().__init__(images, simulation, pos, move)
        self.simulation = simulation
    

    def update(self):
        self.save_data('type', 'Grass')
        self.freeze_movement()
        # Only perform actions every timestep : random chance to reproduce

        if self.shared.counter % TIMESTEP_INTERVAL == 0 and random.random() < 0.0072:
            self.reproduce()
            self.simulation.batch_spawn_agents(2,Grass, grassImages)
            # print("split")