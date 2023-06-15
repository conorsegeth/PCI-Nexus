from PIL import Image
import pygame as pg
from pygame.math import Vector2
from pygame.surface import Surface
from vi import Simulation, Agent
from vi.config import Config
from vi.simulation import HeadlessSimulation
import random
import math
import matplotlib.pyplot as plt
import polars as pl
import numpy as np

class Cockroach(Agent):
    def __init__(self, images: list[Surface], simulation: HeadlessSimulation, pos: Vector2 | None = None, move: Vector2 | None = None):
        super().__init__(images, simulation, pos, move)
        self.state = "wandering"
        self.direction = self.move.normalize()
        self.velocity = simulation.config.movement_speed

        self.check_interval = 50

        self.left_on_tick = float('inf')
    
    def _calculate_join_probability(self, n):
        a = 0.03
        b = 0.48
        c = 0.64
        prob = a + b * (1 - math.e**(-c * n))
        # print(prob)
        return prob
    
    def _calculate_leave_probability(self, n):
        a = 0.85
        b = 1
        prob = a * math.e**(-b * n) + 0.0001
        # print(prob)
        return prob

    def update(self):
        self.save_data("state", self.state)
        
        site_id = -1 if self.on_site_id() == None else self.on_site_id()
        if self.state == 'wandering':
            site_id = -1
        self.save_data("on_site_id", site_id)
        
        num_neighbors = self.in_proximity_accuracy().count()

        if self.state == 'wandering':
            self.continue_movement()

            # Change state to join if agent currently on a site
            if self.on_site():
                self.state = 'join'
    
        elif self.state == 'join':
            # If agents go off the site change back to wandering (prevents stopping after leaving the site)
            if not self.on_site():
                self.state = 'wandering'

            # Join with some probability every 50 ticks
            if self.shared.counter % self.check_interval == 0:
                if random.random() < self._calculate_join_probability(num_neighbors):
                    self.state = 'still'
        
        elif self.state == 'still':
            self.freeze_movement()

            # Enter leave state with some probability every 50 ticks
            if self.shared.counter % self.check_interval == 0:
                if random.random() < self._calculate_leave_probability(num_neighbors):
                    self.left_on_tick = self.shared.counter
                    self.state = 'leave'
        
        else:
            # Continue movement & don't enter wandering again for some number of ticks
            self.continue_movement()
            if self.shared.counter == self.left_on_tick + 500:
                self.left_on_tick = float('inf')
                self.state = 'wandering'
        
    def change_position(self):
        if not self._moving:
            return

        self.direction = self.move.normalize()

        if self.pos.x + (self.direction.x * 5) < self._area.left:
            self.direction.x *= -1
        elif self.pos.x + (self.direction.x * 5) > self._area.right:
            self.direction.x *= -1
        elif self.pos.y + (self.direction.y * 5) < self._area.top:
            self.direction.y *= -1
        elif self.pos.y + (self.direction.y * 5) > self._area.bottom:
            self.direction.y *= -1

        if random.random() < 0.005:
            self.direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            self.direction = self.direction.normalize()

        self.move = self.direction * self.velocity
        self.pos += self.move


def plot_wandering_vs_site_total(snapshots, title):
    # Create dataframe from metrics
    df = snapshots.drop(['x', 'y', 'image_index'])

    # Only use data from every 50 frames
    df = df.filter(
        (pl.col('frame') % 50 == 0)
    )

    # Get x values for padding later
    x_values = df.drop('id', 'state', 'on_site_id').groupby('frame', maintain_order=True).agg(pl.count('*'))['frame'].to_list()

    # Calcualte frame range for padding later
    arr = np.arange(0, max(x_values) + 1, step=50)
    arr = arr.astype(np.int64)
    frame_range = pl.DataFrame({'frame': arr})

    # Group by frame, state & on_site_id and filter out all unneeded rows
    grouped = df.groupby(["frame", "state"], maintain_order=True).agg(pl.count("id").alias("count"))
    filtered = grouped.filter(
        ((pl.col('state') == 'wandering') | ((pl.col('state') == 'still')))
    )

    df_wandering = filtered.filter((pl.col('state') == 'wandering')).drop(['state'])
    df_still = filtered.filter((pl.col('state') == 'still')).drop(['state'])

    df_wandering_padded = frame_range.join(df_wandering, on='frame', how='left').fill_null(0)
    df_still_padded = frame_range.join(df_still, on='frame', how='left').fill_null(0)

    wandering_values = df_wandering_padded['count'].to_list()
    still_values = df_still_padded['count'].to_list()
    
    plt.clf()

    plt.plot(x_values, wandering_values, label='wandering')
    plt.plot(x_values, still_values, label='still')

    plt.xlabel("Frame")
    plt.ylabel("Count")
    plt.title(title)

    plt.legend()
    plt.savefig(f'assignment1/graphs/{title}.png')

def plot_site_populations(num_sites, snapshots):
    lines = ['wandering']
    for _ in range(num_sites):
        lines.append('still')

    # Create dataframe from metrics
    df = snapshots.drop(['x', 'y', 'image_index'])

    # Only use data from every 50 frames
    df = df.filter(
        (pl.col('frame') % 50 == 0)
    )

    # Get x values for padding later
    x_values = df.drop('id', 'state', 'on_site_id').groupby('frame', maintain_order=True).agg(pl.count('*'))['frame'].to_list()

    # Calcualte frame range for padding later
    arr = np.arange(0, max(x_values) + 1, step=50)
    arr = arr.astype(np.int64)
    frame_range = pl.DataFrame({'frame': arr})

    # Group by frame, state & on_site_id and filter out all unneeded rows
    grouped = df.groupby(["frame", "state", "on_site_id"], maintain_order=True).agg(pl.count("id").alias("count"))
    filtered = grouped.filter(
        ((pl.col('state') == 'wandering') | ((pl.col('state') == 'still') & (pl.col('on_site_id').is_in(range(num_sites)))))
    )

    # Create dataframes containting only information about wandering, still & on site 0, still & on site 1
    for i, state in enumerate(lines):
        if state == 'wandering':
            line_df = filtered.filter((pl.col('state') == 'wandering') & (pl.col("on_site_id") == -1)).drop(['state', 'on_site_id'])
        else:
            line_df = filtered.filter((pl.col("state") == "still") & (pl.col("on_site_id") == i - 1)).drop(['state', 'on_site_id'])

        # Create new df padded with 0s to fill frame count
        line_df_padded = frame_range.join(line_df, on='frame', how='left').fill_null(0)

        # Separate values for line to plot
        line_values = line_df_padded['count'].to_list()

        # Do the plots
        if state == 'wandering':
            plt.plot(x_values, line_values, label=f'{state}')
        else:
            plt.plot(x_values, line_values, label=f'{state}, on_site {i - 1}')
    
    plt.clf()

    plt.xlabel("Frame")
    plt.ylabel("Count")
    plt.title("Count by Frame")

    plt.legend()
    plt.show()

config = Config()
x, y = config.window.as_tuple()

site = Image.open('images/circle.png')
site = site.resize((200,200))
site.save('images/circle_resized.png')

site = Image.open('images/circle.png')
site = site.resize((141,141))
site.save('images/circle_resized2.png')

site = Image.open('images/circle.png')
site = site.resize((115,115))
site.save('images/circle_resized3.png')

site = Image.open('images/circle.png')
site = site.resize((100,100))
site.save('images/circle_resized4.png')

site = Image.open('images/circle.png')
site = site.resize((89,89))
site.save('images/circle_resized5.png')

site = Image.open('images/circle.png')
site = site.resize((81,81))
site.save('images/circle_resized6.png')

metrics = (
    Simulation(
        Config(
            image_rotation=False,
            movement_speed=1.35,
            radius=50,
            fps_limit=144,
            duration=20000,
        )
    )
    .spawn_site("images/circle_resized.png", x // 2, y // 2)
    .batch_spawn_agents(100, Cockroach, ["images/white.png"])
    .run()
)

plot_wandering_vs_site_total(metrics.snapshots, 'Single Site (Size 200)')

metrics = (
    Simulation(
        Config(
            image_rotation=False,
            movement_speed=1.35,
            radius=50,
            fps_limit=6000,
            duration=20000,
        )
    )
    .spawn_site("images/circle_resized2.png", 225, y // 2)
    .spawn_site("images/circle_resized2.png", 525, y // 2)
    .batch_spawn_agents(100, Cockroach, ["images/white.png", "images/red.png"])
    .run()
)

plot_wandering_vs_site_total(metrics.snapshots, 'Two Sites (Size 141)')

metrics = (
    Simulation(
        Config(
            image_rotation=False,
            movement_speed=1.35,
            radius=50,
            fps_limit=6000,
            duration=20000,
        )
    )
    .spawn_site("images/circle_resized3.png", 200, 550)
    .spawn_site("images/circle_resized3.png", 550, 550)
    .spawn_site("images/circle_resized3.png", x // 2, 200)
    .batch_spawn_agents(100, Cockroach, ["images/white.png", "images/red.png"])
    .run()
)

plot_wandering_vs_site_total(metrics.snapshots, 'Three Sites (Size 115)')

metrics = (
    Simulation(
        Config(
            image_rotation=False,
            movement_speed=1.35,
            radius=50,
            fps_limit=6000,
            duration=20000,
        )
    )
    .spawn_site("images/circle_resized4.png", 200, 200)
    .spawn_site("images/circle_resized4.png", 550, 200)
    .spawn_site("images/circle_resized4.png", 200, 550)
    .spawn_site("images/circle_resized4.png", 550, 550)
    .batch_spawn_agents(100, Cockroach, ["images/white.png", "images/red.png"])
    .run()
)


plot_wandering_vs_site_total(metrics.snapshots, 'Four Sites (Size 100)')

metrics = (
    Simulation(
        Config(
            image_rotation=False,
            movement_speed=1.35,
            radius=50,
            fps_limit=6000,
            duration=20000,
        )
    )
    .spawn_site("images/circle_resized5.png", 175, 175)
    .spawn_site("images/circle_resized5.png", 575, 175)
    .spawn_site("images/circle_resized5.png", 175, 575)
    .spawn_site("images/circle_resized5.png", 575, 575)
    .spawn_site("images/circle_resized5.png", x // 2, y // 2)
    .batch_spawn_agents(100, Cockroach, ["images/white.png", "images/red.png"])
    .run()
)

plot_wandering_vs_site_total(metrics.snapshots, 'Five Sites (Size 89)')

metrics = (
    Simulation(
        Config(
            image_rotation=False,
            movement_speed=1.35,
            radius=50,
            fps_limit=6000,
            duration=20000,
        )
    )
    .spawn_site("images/circle_resized6.png", 200, 150)
    .spawn_site("images/circle_resized6.png", 550, 150)
    .spawn_site("images/circle_resized6.png", 200, y // 2)
    .spawn_site("images/circle_resized6.png", 550, y // 2)
    .spawn_site("images/circle_resized6.png", 200, 600)
    .spawn_site("images/circle_resized6.png", 550, 600)
    .batch_spawn_agents(100, Cockroach, ["images/white.png", "images/red.png"])
    .run()
)

plot_wandering_vs_site_total(metrics.snapshots, 'Six Sites (Size 81)')