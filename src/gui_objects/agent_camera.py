import pygame
import math

from src.colors import *


class AgentCameraSurface(pygame.Surface):
    def __init__(self, size, agent, sky_color=black, floor_color=grey):
        super().__init__(size)

        self.size = size
        self.agent = agent
        self.sky_color = sky_color
        self.floor_color = floor_color

        # Precalculate static parameter values
        self.vision_line_width = self.size[0] / self.agent.vision_sensor.num_of_rays
        self.y_middle = int(self.size[1] / 2)
        self.max_vision_line_length = self.size[1]
        self.max_collision_distance = self.agent.vision_sensor.ray_length
        self.vision_line_length_per_distance_unit = self.max_vision_line_length / self.max_collision_distance
        self.color_step_size = 200 / self.max_collision_distance

    def display(self):

        # Reset view. Set sky and floor color.
        self.fill(black)
        pygame.draw.rect(self, self.floor_color, (0, self.y_middle, self.size[0], self.y_middle))

        # Get collision_distances from agent
        collision_distances = self.agent.get_collision_distances()

        # Draw a vision line for every vision ray collision
        for i, collision_distance in enumerate(collision_distances):
            if collision_distance is not None:

                # Calculate length of vision line and line color
                vision_line_length_pixel = (self.max_vision_line_length -
                                            int(collision_distance * self.vision_line_length_per_distance_unit))
                line_color = (0, 255 - (self.color_step_size * collision_distance), 0)

                # Calculate coords for vision line
                vision_line_coords = (self.vision_line_width * i,  # X
                                      self.y_middle - int(vision_line_length_pixel / 2),  # Y
                                      math.ceil(self.vision_line_width),  # width
                                      vision_line_length_pixel)  # height

                # Draw vision line
                pygame.draw.rect(self, line_color, vision_line_coords)
