import math

def calculate_relative_sensor_positions(rotation = 45, fov = 180, num_of_rays = 5, ray_length = 10):
    relative_sensor_positions = []
    agent_angle_rad = math.radians(rotation)
    step_angle_rad = math.radians(fov / (num_of_rays - 1))
    start_angle_rad = agent_angle_rad - math.radians(fov / 2)  # Corrected start angle based on fov
    print(fov / (num_of_rays - 1))
    for i in range(num_of_rays):
        adjacent = math.cos(start_angle_rad + step_angle_rad * i) * ray_length  # Ray length = Hypothenuse
        opposite = math.sin(start_angle_rad + step_angle_rad * i) * ray_length  # Ray length = Hypothenuse
        pos = (round(adjacent), round(opposite))
        relative_sensor_positions.append(pos)

    print(relative_sensor_positions)
    return relative_sensor_positions


calculate_relative_sensor_positions()