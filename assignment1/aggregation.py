
from vi import Simulation, Agent, Config


class Cockroach(Agent):
    def update(self):
        if self.on_site():
            self.freeze_movement()

config = Config()
x, y = config.window.as_tuple()

(
    Simulation()
    .spawn_site("PCI-Nexus/images/bubble-full.png", x // 2, y // 2)
    .batch_spawn_agents(50, Cockroach, ["PCI-Nexus/images/white.png"])
    .run()
)

