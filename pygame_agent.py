import pygame
import random
import math

class Agent:
    num_of_agents = 0

    def __init__(self, simulation, movement_speed: int = 10, turning_speed: int = 3):
        self.simulation = simulation
        self.movement_speed = movement_speed
        self.turning_speed = turning_speed

        # Determine start location and rotation
        self.location = (random.randint(0, self.simulation.size[0]-1),
                         random.randint(0, self.simulation.size[1]-1))
        self.rotation = random.randint(0, 359)

        # Set instance name and iterate name value
        self.name = "agent_" + str(Agent.num_of_agents)
        Agent.num_of_agents += 1

    def update(self):

        # Randomly change direction
        self.rotation = self.rotation + random.randint(-self.turning_speed, self.turning_speed)

        # Keep rotation between 0 and 359 degrees
        self.rotation = self.rotation % 360
        radians_rotation = math.radians(self.rotation)

        self.location = (round(self.location[0] + math.cos(radians_rotation) * self.movement_speed),  # X Coordinate
                         round(self.location[1] + math.sin(radians_rotation) * self.movement_speed))  # Y Coordinate
