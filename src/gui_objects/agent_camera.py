import pygame
import math
from typing import Tuple

from src.colors import *
from src.sim_objects.agent import Agent


class AgentCameraSurface(pygame.Surface):

    # Figures
    entity_polygon = [(0, 0), (-10, -5), (-8, 0), (-10, +5)]

    def __init__(self, size: Tuple[int, int], agent: Agent, sky_color: Tuple[int, int, int] = black,
                 floor_color: Tuple[int, int, int] = grey):
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

        # Calculate the angle between each ray and the player's direction
        delta_angle = self.agent.vision_sensor.fov / self.agent.vision_sensor.num_of_rays
        half_fov = self.agent.vision_sensor.fov / 2

        # Draw a vision line for every vision ray collision
        for i, collision_distance in enumerate(collision_distances):
            if collision_distance is not None:

                # Calculate the angle of the current ray relative to the player's direction
                current_angle = self.agent.rotation - half_fov + (i * delta_angle)

                line_color = (0, 255 - (self.color_step_size * collision_distance), 0)

                # Correct the collision distance to remove fisheye effect
                collision_distance = collision_distance * math.cos(math.radians(current_angle - self.agent.rotation))

                # Calculate length of vision line and line color
                vision_line_length_pixel = (self.max_vision_line_length -
                                            int(collision_distance * self.vision_line_length_per_distance_unit))

                # Calculate coords for vision line
                vision_line_coords = (self.vision_line_width * i,  # X
                                      self.y_middle - int(vision_line_length_pixel / 2),  # Y
                                      math.ceil(self.vision_line_width),  # width
                                      vision_line_length_pixel)  # height

                # Draw vision line
                pygame.draw.rect(self, line_color, vision_line_coords)

        """DRAW OTHER AGENTS"""

        near_agents = self.agent.agent_vicinity_detection(self.max_collision_distance)
        pixel_per_fov = self.size[0] / self.agent.vision_sensor.fov
        agent_max_size = 30
        delta_size_per_distance_unit = agent_max_size / self.max_collision_distance
        rays_per_fov = self.agent.vision_sensor.num_of_rays / self.agent.vision_sensor.fov

        for agent, values in near_agents.items():
            agent_distance, agent_angle = values[0], values[1]
            if agent_angle <= half_fov or agent_angle >= 360-half_fov:  # If angle is in view

                # Convert high angle (left side of view) to small negative angle
                if agent_angle >= 360-half_fov:
                    agent_angle -= 360

                # Check if agent is behind obstacle
                agent_pos_to_collision_index = min(round((agent_angle + half_fov) * rays_per_fov),
                                                   self.agent.vision_sensor.num_of_rays - 1)

                if (collision_distances[agent_pos_to_collision_index] is None or
                        collision_distances[agent_pos_to_collision_index] >= agent_distance):

                    agent_display_location = (pixel_per_fov * (agent_angle + half_fov), self.y_middle)
                    agent_display_size = agent_max_size + 1 - agent_distance*delta_size_per_distance_unit
                    agent_display_color = (255 - (self.color_step_size * agent_distance), 0, 0)

                    pygame.draw.circle(self, agent_display_color, agent_display_location, agent_display_size, width=0)
