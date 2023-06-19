from pygame import Vector2
from vi import Simulation

class MySimulation(Simulation):
    def spawn_agent(self, agent_class, images: list[str], x_pos: float, y_pos: float):
        agent_class(images=self._load_images(images), simulation=self, pos=Vector2((x_pos, y_pos)))
        return self