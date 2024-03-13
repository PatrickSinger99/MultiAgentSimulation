import pygame
import random
import math
from colors import *


class Agent:
    num_of_agents = 0

    def __init__(self, simulation, movement_speed: int = 10, turning_speed: int = 10):
        self.simulation = simulation
        self.movement_speed = movement_speed
        self.turning_speed = turning_speed

        self.color = white

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

    def move(self, coordinates: (int, int)):
        self.location = coordinates
