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

    plt.xlabel('time')
    plt.ylabel('population')
    plt.title('Population vs Time')
    plt.legend()

    plt.show()