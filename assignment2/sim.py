from vi import Simulation, Window
from vi.config import Config
from predator import Predator
from prey import Prey

if __name__ == '__main__':
    window = Window(960, 540)

    (
        Simulation(
            Config(
                window=window,
                image_rotation=True,
            )
        )
        .batch_spawn_agents(20, Predator, ['images/bird.png'])
        .batch_spawn_agents(50, Prey, ['images/green.png'])
        .run()
    )

