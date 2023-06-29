from vi import Window, Config
from sim import MySimulation, MySeasonalSimulation, MyConfig, SEASON_LENGTH
from agents import Predator, PredatorWithEnergy, Prey, predatorImages, preyImages, TIMESTEP_INTERVAL, Grass
from plotting import plot_population_sizes, plot_population_sizes_with_seasons, print_avg_pop_size_per_season


def run_grass_only_simulation():
    window = Window(750, 750)

    config = MyConfig()

    # GOOD SEED: 472220471
    # This shit lowkey just runs infinitely I stg: 114300533
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

    return metrics

def run_seasonal_simulation():
    # Good seed: 630358656
    window = Window(750, 750)

    config = MyConfig()

    metrics = (
        MySeasonalSimulation(
            Grass,
            Config(
                window=window,
                image_rotation=True,
                fps_limit=144,
                print_fps=False,
                radius=25,
                seed=config.seed,
                duration=7200 * 16
            )
        )
        .spawn_grass_patches(5, 10, 'images/circle_resized.png')
        .batch_spawn_agents(20, PredatorWithEnergy, predatorImages)
        .batch_spawn_agents(150, Prey, preyImages)
        .run()
    )

    return metrics


if __name__ == '__main__':
    metrics = run_seasonal_simulation()

    print_avg_pop_size_per_season(metrics.snapshots, TIMESTEP_INTERVAL)
    plot_population_sizes_with_seasons(metrics.snapshots, TIMESTEP_INTERVAL, SEASON_LENGTH)
