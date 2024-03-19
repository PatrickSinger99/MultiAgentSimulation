import math


class VisionSensor:
    def __init__(self, parent_agent, num_of_rays: int, ray_length: int, fov: int):
        self.parent_agent = parent_agent
        self.num_of_rays = max(1, num_of_rays)
        self.ray_length = max(0, ray_length)
        self.fov = max(0, min(fov, 360))
        self.relative_sensor_positions = self.calculate_relative_sensor_positions()

        self.sensor_coords = self.calculate_sensor_pos()
        self.sensor_collisions = [None for _ in range(num_of_rays)]
        self.sensor_collision_distance = [None for _ in range(num_of_rays)]

    def update(self):
        self.sensor_coords = self.calculate_sensor_pos()
        self.sensor_collisions = [None for _ in range(self.num_of_rays)]
        self.sensor_collision_distance = [None for _ in range(self.num_of_rays)]

    def calculate_relative_sensor_positions(self):
        relative_sensor_positions = []
        start_angle_rad = -math.radians(self.fov / 2)  # Corrected start angle based on fov

        if self.num_of_rays > 1:
            step_angle_rad = math.radians(self.fov / (self.num_of_rays - 1))
        else:
            step_angle_rad = -start_angle_rad  # TODO FIX if only one sensor, position is not correct (skewed to side)

        for i in range(self.num_of_rays):
            adjacent = math.cos(start_angle_rad + step_angle_rad*i) * self.ray_length  # Ray length = Hypothenuse
            opposite = math.sin(start_angle_rad + step_angle_rad*i) * self.ray_length  # Ray length = Hypothenuse
            pos = (round(adjacent), round(opposite))
            relative_sensor_positions.append(pos)

        return relative_sensor_positions

    def calculate_sensor_pos(self):
        # Convert angle to radians
        angle_rad = math.radians(self.parent_agent.rotation)
        # Define the rotation matrix
        rotation_matrix = [
            [math.cos(angle_rad), -math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ]
        # Apply the rotation matrix to each point
        rotated_positions = []
        for point in self.relative_sensor_positions:
            rotated_point = [
                point[0] * rotation_matrix[0][0] + point[1] * rotation_matrix[0][1],
                point[0] * rotation_matrix[1][0] + point[1] * rotation_matrix[1][1]
            ]

            # Add current coords
            rotated_point = (rotated_point[0] + self.parent_agent.location[0], rotated_point[1] + self.parent_agent.location[1])

            rotated_positions.append(rotated_point)

        return rotated_positions
