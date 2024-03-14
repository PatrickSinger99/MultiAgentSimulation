import pygame
import random
import math
from colors import *


class Agent:
    num_of_agents = 0

    sensor_positions = ((55, 20), (60, 0), (55, -20))

    def __init__(self, simulation, movement_speed: int = 10, turning_speed: int = 10, color=white):
        self.simulation = simulation
        self.movement_speed = movement_speed
        self.turning_speed = turning_speed

        self.color = color

        # Determine start location and rotation
        while True:
            self.location = (random.randint(0, self.simulation.size[0]-1),
                             random.randint(0, self.simulation.size[1]-1))

            # Check if point does not collide with a obstacle in the simulation
            no_collision = True
            for obstacle in self.simulation.obstacles:
                # If collision is detected, calculate collision coords and move agent to them
                if obstacle.rect.collidepoint(self.location[0], self.location[1]):
                    no_collision = False

            if no_collision:
                break

        self.rotation = random.randint(0, 359)
        self.prev_location = self.location

        # Set instance name and iterate name value
        self.name = "agent_" + str(Agent.num_of_agents)
        Agent.num_of_agents += 1

        # TEMP
        self.sensor_coords = self.calculate_sensor_coords()
        self.sensor_collisions = [None, None, None]

    def update(self):

        # Randomly change direction
        self.rotation = self.rotation + random.randint(-self.turning_speed, self.turning_speed)

        # Keep rotation between 0 and 359 degrees
        self.rotation = self.rotation % 360
        radians_rotation = math.radians(self.rotation)

        # Save previous location
        self.prev_location = self.location

        # Update location
        self.location = (round(self.location[0] + math.cos(radians_rotation) * self.movement_speed),  # X Coordinate
                         round(self.location[1] + math.sin(radians_rotation) * self.movement_speed))  # Y Coordinate

        # Keep location within simulation boundary
        self.location = (max(0, min(self.location[0], self.simulation.size[0] - 1)),
                         max(0, min(self.location[1], self.simulation.size[1] - 1)))

        # Update sensor coords
        self.sensor_coords = self.calculate_sensor_coords()
        self.sensor_collisions = [None, None, None]

    def move(self, coordinates: (int, int)):
        self.location = coordinates


    def calculate_sensor_coords(self):
        # Convert angle to radians
        angle_rad = math.radians(self.rotation)
        # Define the rotation matrix
        rotation_matrix = [
            [math.cos(angle_rad), -math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ]
        # Apply the rotation matrix to each point
        rotated_positions = []
        for point in Agent.sensor_positions:
            rotated_point = [
                point[0] * rotation_matrix[0][0] + point[1] * rotation_matrix[0][1],
                point[0] * rotation_matrix[1][0] + point[1] * rotation_matrix[1][1]
            ]

            # Add current coords
            rotated_point = (rotated_point[0] + self.location[0], rotated_point[1] + self.location[1])

            rotated_positions.append(rotated_point)

        return rotated_positions


class PlayerControlledAgent(Agent):
    def __init__(self, simulation, **kwargs):
        super().__init__(simulation=simulation, **kwargs)

    def update(self):

        movement = 0
        rotation = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            movement += 1
        if keys[pygame.K_s]:
            movement -= 1
        if keys[pygame.K_d]:
            rotation += 1
        if keys[pygame.K_a]:
            rotation -= 1

        # Randomly change direction
        self.rotation = self.rotation + rotation

        # Keep rotation between 0 and 359 degrees
        self.rotation = self.rotation % 360
        radians_rotation = math.radians(self.rotation)

        # Save previous location
        self.prev_location = self.location

        # Update location
        self.location = (round(self.location[0] + (math.cos(radians_rotation) * self.movement_speed)*movement),  # X Coordinate
                         round(self.location[1] + (math.sin(radians_rotation) * self.movement_speed)*movement))  # Y Coordinate

        # Keep location within simulation boundary
        self.location = (max(0, min(self.location[0], self.simulation.size[0] - 1)),
                         max(0, min(self.location[1], self.simulation.size[1] - 1)))

        # Update sensor coords
        self.sensor_coords = self.calculate_sensor_coords()
        self.sensor_collisions = [None, None, None]
