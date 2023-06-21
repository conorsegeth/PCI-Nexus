from vi import Window, Config
from sim import MySimulation
from agents import Predator, Prey, predatorImages, preyImages, TIMESTEP_INTERVAL
from plotting import plot_population_sizes


if __name__ == '__main__':
    window = Window(750, 750)

    metrics = (
        MySimulation(
            Config(
                window=window,
                image_rotation=True,
                fps_limit=144,
                print_fps=False,
                radius=50,
            )
        )
        .batch_spawn_agents(25, Predator, predatorImages)
        .batch_spawn_agents(110, Prey, preyImages)
        .run()
    )

    plot_population_sizes(metrics.snapshots, TIMESTEP_INTERVAL)