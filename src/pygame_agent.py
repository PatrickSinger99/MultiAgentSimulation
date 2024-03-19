import pygame
import random
import math
from colors import *
from vision_sensor import VisionSensor


class Agent:
    num_of_agents = 0

    sensor_positions = ((55, 20), (60, 0), (55, -20))

    def __init__(self, simulation, movement_speed: int = 10, turning_speed: int = 10, color=white,
                 num_vision_sensors: int = 3, vision_sensors_fov: int = 75, vision_sensors_length: int = 30):
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

        # Initialize vision sensors
        self.vision_sensor = VisionSensor(self, num_of_rays=num_vision_sensors, ray_length=vision_sensors_length,
                                          fov=vision_sensors_fov)

    def update(self, policy):

        delta_rotation, delta_location = policy.execute(self)

        # Apply rotation change
        self.rotation = self.rotation + delta_rotation

        # Keep rotation between 0 and 359 degrees
        self.rotation = self.rotation % 360
        radians_rotation = math.radians(self.rotation)

        # Save previous location
        self.prev_location = self.location

        # Update location
        self.location = (round(self.location[0] + math.cos(radians_rotation) * delta_location),  # X Coordinate
                         round(self.location[1] + math.sin(radians_rotation) * delta_location))  # Y Coordinate

        # Keep location within simulation boundary
        self.location = (max(0, min(self.location[0], self.simulation.size[0] - 1)),
                         max(0, min(self.location[1], self.simulation.size[1] - 1)))

        # Update sensor coords
        self.vision_sensor.update()

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

    def sensor_collision_detection(self):

        possible_collision_edges = []

        # Get all obstacle borders that are within the radius of a sensor ray to the agent
        for edge in self.simulation.obstacle_edges:
            if self.minimum_distance(edge, self.location) <= self.vision_sensor.ray_length:
                possible_collision_edges.append(edge)

        # Check if edges in range for a collision actually collide with one of the agents sensor rays
        for edge in possible_collision_edges:
            for sensor_index, sensor in enumerate(self.vision_sensor.sensor_coords):
                sensor_line = (sensor, self.location)

                # Check intersection with one sensor ray
                intersection_coords = self.simulation.line_intersection(edge, sensor_line)
                if intersection_coords is not None:

                    # CASE: No other collision with this sensor ray was detected yet
                    if self.vision_sensor.sensor_collisions[sensor_index] is None:
                        self.vision_sensor.sensor_collisions[sensor_index] = intersection_coords
                        # self.sensor_collision_distance[sensor_index] = collision_distance

                    # CASE: Sensor ray already has a collision logged
                    else:
                        collision_distance = self.simulation.calculate_distance(intersection_coords, self.location)  # TODO method import from simulation

                        # Distance for previous collision now needs to be calculated
                        if self.vision_sensor.sensor_collision_distance[sensor_index] is None:
                            prev_collision_distance = self.simulation.calculate_distance(self.vision_sensor.sensor_collisions[sensor_index], self.location)
                            self.vision_sensor.sensor_collision_distance[sensor_index] = prev_collision_distance

                        # Add distance and new coords to arrays
                        if self.vision_sensor.sensor_collision_distance[sensor_index] > collision_distance:
                            self.vision_sensor.sensor_collisions[sensor_index] = intersection_coords
                            self.vision_sensor.sensor_collision_distance[sensor_index] = collision_distance

    @staticmethod
    def minimum_distance(line, point):
        # v, w are points defining the line segment, and p is the point.
        v, w, p = line[0], line[1], point

        l2 = math.dist(v, w) ** 2  # i.e., |w-v|^2 - avoid a sqrt
        if l2 == 0:
            return math.dist(p, v)  # v == w case
        t = max(0, min(1, ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2))
        projection = (v[0] + t * (w[0] - v[0]), v[1] + t * (w[1] - v[1]))
        return math.dist(p, projection)

    def get_collision_distances(self):
        """
        Gets the distances for each sensor to the nearest collision. Also calculates distances for sensors that only
        have one collision as this step was skipped to increase the performance in the base collision detection.
        :return: List of distances to obstacle for each sensor
        """

        # Calculate all sensor collision distances that were skipped in the main collision function
        for i, sensor_collision_coords in enumerate(self.vision_sensor.sensor_collisions):
            if sensor_collision_coords is not None and self.vision_sensor.sensor_collision_distance[i] is None:
                collision_distance = self.simulation.calculate_distance(sensor_collision_coords, self.location)
                self.vision_sensor.sensor_collision_distance[i] = collision_distance

        return self.vision_sensor.sensor_collision_distance


class PlayerControlledAgent(Agent):
    def __init__(self, simulation, **kwargs):
        super().__init__(simulation=simulation, **kwargs)
        self.name = "user_controlled_agent"

    def update(self, policy):  # policy is only placeholder

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
        self.rotation = self.rotation + rotation * self.turning_speed

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
        self.vision_sensor.update()


