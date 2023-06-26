import math
import random
from PIL import Image
from typing import Optional, Type
from pygame import Vector2
from vi import Simulation
from vi.config import Config, dataclass, deserialize
from vi.metrics import Metrics


def perturb_point_within_radius(x, y, radius):
# Generate a random angle in radians
    angle = random.uniform(0, 2 * math.pi)
    
    # Generate a random distance within the radius
    distance = random.uniform(0, radius)
    
    # Calculate the new perturbed point
    new_x = x + distance * math.cos(angle)
    new_y = y + distance * math.sin(angle)
    
    return new_x, new_y


@deserialize
@dataclass
class MyConfig(Config):
    seed = random.randint(0, 999999999)
    print(seed)
    
GROW_RATE = 0.025
GROW_RADIUS = 70

class MySimulation(Simulation):
    def __init__(self, grass_agent, config: Config | None = None):
        super().__init__(config)
        self.grass_agent = grass_agent

    def spawn_agent(self, agent_class, images, pos_x, pos_y):
        
        agent_class(images=self._load_images(images), simulation=self, pos=Vector2(pos_x, pos_y))

        return self

    def before_update(self):
        super().before_update()

        for i, pos in enumerate(self.patches):
            if random.random() < GROW_RATE:
                x, y = perturb_point_within_radius(pos.x, pos.y, GROW_RADIUS)
                self.spawn_agent(self.grass_agent, ['images/green.png'], x, y)
        

    def spawn_grass_patches(self, num_patches, min_distance, img_path):
        max_attempts = 100

        img = Image.open(img_path)
        img_width, img_height = img.size

        self.patches = []
        for _ in range(num_patches):
            attempt = 0
            while attempt < max_attempts:
                x = random.randint(min_distance + img_width / 2, self.config.window.width - min_distance - img_width / 2)
                y = random.randint(min_distance + img_height / 2, self.config.window.width - min_distance - img_height / 2)
                new_patch = Vector2(x, y)

                if not any(overlap(new_patch, existing_patch, img) for existing_patch in self.patches):
                    self.patches.append(new_patch)
                    break
                    
                attempt += 1
        
        for i, patch in enumerate(self.patches):
            self.spawn_site(img_path, patch.x, patch.y)
        
        return self

def overlap(pos1, pos2, img):
    img_width, img_height = img.size
    dist = math.sqrt((pos2.x - pos1.x)**2 + (pos2.y - pos1.y)**2)
    return True if dist < img_width or dist < img_height else False

if __name__ == '__main__':
    img = Image.open('images/circle.png')
    img = img.resize((150, 150))
    img.save('images/circle_resized.png')