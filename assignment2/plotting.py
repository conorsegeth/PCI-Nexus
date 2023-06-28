import polars as pl
import numpy as np
import matplotlib.pyplot as plt

def plot_population_sizes(snapshots: pl.DataFrame, timestep_frame_interval: int) -> None:
    # Drop unneeded columns
    df = snapshots.drop(['x', 'y', 'image_index', 'angle'])
    df = df.filter((pl.col('frame') % timestep_frame_interval == 0))

    # Remove rows that do not coincide with our timesteps
    timesteps = df.groupby('frame', maintain_order=True).agg(pl.count('*'))['frame'].to_list()
    arr = np.arange(0, max(timesteps) + 1, step=timestep_frame_interval)
    arr = arr.astype(np.int64)
    frame_range = pl.DataFrame({'frame': arr})
    print(frame_range)

    # Calculate x values in seconds 
    # TODO: Fix bug where timesteps and x_values are out of sync by 1 increment
    step = timestep_frame_interval / 60
    stop = 0 + (len(timesteps) * step)
    x_values = np.arange(0, stop, step)
    print(x_values)

    grouped = df.groupby(['frame', 'type'], maintain_order=True).agg(pl.count('id').alias('count'))
    
    df_prey = grouped.filter((pl.col('type') == 'Prey')).drop('type')
    df_predator = grouped.filter((pl.col('type') == 'Predator')).drop('type')

    # Pad dfs with 0s where there are no agents alive
    df_prey_padded = frame_range.join(df_prey, on='frame', how='left').fill_null(0)
    df_predator_padded = frame_range.join(df_predator, on='frame', how='left').fill_null(0)

    prey_values = df_prey_padded['count'].to_list()
    predator_values = df_predator_padded['count'].to_list()

    # Plots
    plt.clf()

    plt.plot(x_values, prey_values, label='Prey')
    plt.plot(x_values, predator_values, label='Predators')

    plt.xlabel('time (seconds)')
    plt.ylabel('population')
    plt.title('Population vs Time')
    plt.legend()

    plt.show()

def plot_population_sizes_with_seasons(snapshots: pl.DataFrame, timestep_frame_interval: int, season_length: int) -> None:
    # Drop unneeded columns
    df = snapshots.drop(['x', 'y', 'image_index', 'angle'])
    df = df.filter((pl.col('frame') % timestep_frame_interval == 0))

    # Remove rows that do not coincide with our timesteps
    timesteps = df.groupby('frame', maintain_order=True).agg(pl.count('*'))['frame'].to_list()
    arr = np.arange(0, max(timesteps) + 1, step=timestep_frame_interval)
    arr = arr.astype(np.int64)
    frame_range = pl.DataFrame({'frame': arr})
    print(frame_range)

    # Calculate x values in seconds 
    # TODO: Fix bug where timesteps and x_values are out of sync by 1 increment
    step = timestep_frame_interval / 60
    stop = 0 + (len(timesteps) * step)
    x_values = np.arange(0, stop, step)
    print(x_values)

    grouped = df.groupby(['frame', 'type'], maintain_order=True).agg(pl.count('id').alias('count'))
    
    df_prey = grouped.filter((pl.col('type') == 'Prey')).drop('type')
    df_predator = grouped.filter((pl.col('type') == 'Predator')).drop('type')
    df_grass = grouped.filter((pl.col('type') == 'Grass')).drop('type')

    # Pad dfs with 0s where there are no agents alive
    df_prey_padded = frame_range.join(df_prey, on='frame', how='left').fill_null(0)
    df_predator_padded = frame_range.join(df_predator, on='frame', how='left').fill_null(0)
    df_grass_padded =frame_range.join(df_grass, on='frame', how='left').fill_null(0)

    prey_values = df_prey_padded['count'].to_list()
    predator_values = df_predator_padded['count'].to_list()
    grass_values = df_grass_padded['count'].to_list()

    # Get x_vales where season changed
    season_time = season_length / 60
    season_changes = [num for num in x_values if num % season_time == 0]
    summer_x = season_changes[0::4]
    autumn_x = season_changes[1::4]
    winter_x = season_changes[2::4]
    spring_x = season_changes[3::4]

    # Plots
    plt.clf()

    plt.plot(x_values, prey_values, label='Prey')
    plt.plot(x_values, predator_values, label='Predators')
    plt.plot(x_values, grass_values, label='Grass', color='green')

    for i in range(len(season_changes)):
        colors = ['yellow', 'orange', 'lightblue', 'springgreen']
        if i == 0:
            idx = np.where(x_values == season_changes[1])
            plt.fill_between(x_values[0: idx[0][0]], 0, max(max(prey_values), max(predator_values)), color=colors[i % 4], alpha=0.25)
        elif i < len(season_changes) - 1:
            idx1 = np.where(x_values == season_changes[i])
            idx2 = np.where(x_values == season_changes[i + 1])
            plt.fill_between(x_values[idx1[0][0]: idx2[0][0]], 0, max(max(prey_values), max(predator_values)), color=colors[i % 4], alpha=0.25)
        else:
            idx = np.where(x_values == season_changes[i])
            plt.fill_between(x_values[idx[0][0]: ], 0, max(max(prey_values), max(predator_values)), color=colors[i % 4], alpha=0.25)
    
    # if summer_x:
    #     [plt.axvline(x=point, linestyle='dotted', color='yellow') for point in summer_x]
    # if autumn_x:
    #     [plt.axvline(x=point, linestyle='dotted', color='orange') for point in autumn_x]
    # if winter_x:
    #     [plt.axvline(x=point, linestyle='dotted', color='blue') for point in winter_x]
    # if spring_x:
    #     [plt.axvline(x=point, linestyle='dotted', color='green') for point in spring_x]

    plt.xlabel('time (seconds)')
    plt.ylabel('population')
    plt.title('Population vs Time')
    plt.legend()

    plt.show()

def print_avg_pop_size_per_season(snapshots: pl.DataFrame, timestep_frame_interval: int) -> None:
    df = snapshots.drop(['x', 'y', 'image_index', 'angle'])
    df = df.filter((pl.col('frame') % timestep_frame_interval == 0))
