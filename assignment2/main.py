from vi import Window, Config
from sim import MySimulation, MyConfig
from agents import Predator, PredatorWithEnergy, Prey, predatorImages, preyImages, TIMESTEP_INTERVAL, Grass
from plotting import plot_population_sizes


if __name__ == '__main__':
    window = Window(750, 750)

    config = MyConfig()

    metrics = (
        MySimulation(
            Grass,
            Config(
                window=window,
                image_rotation=True,
                fps_limit=144,
                print_fps=False,
                radius=25,
                seed=config.seed,
                duration=36000
            )
        )
        .spawn_grass_patches(5, 10, 'images/circle_resized.png')
        .batch_spawn_agents(20, PredatorWithEnergy, predatorImages)
        .batch_spawn_agents(150, Prey, preyImages)
        .run()
    )

    plot_population_sizes(metrics.snapshots, TIMESTEP_INTERVAL)

    # GOOD SEED: 472220471
    # This shit lowkey just runs infinitely I stg: 114300533