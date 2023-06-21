from vi import Window, Config
from sim import MySimulation
from agents2 import Predator, Prey, Grass, predatorImages, preyImages, grassImages,TIMESTEP_INTERVAL
from plotting import plot_population_sizes


if __name__ == '__main__':
    window = Window(960, 540)

    metrics = (
        MySimulation(
            Config(
                window=window,
                image_rotation=True,
                fps_limit=144
            )
        )
        .batch_spawn_agents(15, Predator, predatorImages)
        .batch_spawn_agents(35, Prey, preyImages)
        .batch_spawn_agents(40, Grass, grassImages)
        .run()
    )

    plot_population_sizes(metrics.snapshots, TIMESTEP_INTERVAL)