import pygame
from pygame_agent import Agent, PlayerControlledAgent
from pygame_obstacle import Obstacle
import math
from colors import *
import random
import time
from typing import Tuple


def run_simulation(environment_dimensions: Tuple[int, int], simulation_fps: int = 30, number_of_agents: int = 20,
                   player_controlled_agent: bool = False):
    """
    Starts a new simulation and runs the main game loop. Parameters for the simulation are defined here.
    :param environment_dimensions: Dimensions of the simulation area defined as a tuple (x, y).
    :param simulation_fps: Target frames per second of the simulation.
    :param number_of_agents: Number of agents that get spawned into the simulation.
    :param player_controlled_agent: Define if a user controllable agent should be spawned.
    """

    # Initialize pygame and set up the window
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Simulation")
    screen = pygame.display.set_mode(environment_dimensions)

    # Create game loop variables
    done = False
    clock = pygame.time.Clock()
    delta_time_last_frame = 1

    # Create simulation instance
    simulation = Simulation(size=environment_dimensions, number_of_agents=number_of_agents,
                            player_controlled_agent=player_controlled_agent)

    """ MAIN GAME LOOP """

    while not done:
        # Run all simulation functions for one step/frame of the simulation
        done = simulation.process_events()
        simulation.update()
        simulation.display_frame(screen, delta_time_last_frame)

        # Display updated screen
        pygame.display.flip()

        # Tick game and save time this frame took to compute
        delta_time_last_frame = clock.tick(simulation_fps) / 1000


class Simulation:
    """
    Main class for running the multi agent simulation.
    """

    # Figures
    entity_polygon = [(0, 0), (-10, -5), (-8, 0), (-10, +5)]

    def __init__(self, size, number_of_agents, player_controlled_agent=False):
        """
        Initialize the simulation.
        :param size: Dimensions of the simulation area defined as a tuple (x, y).
        :param number_of_agents: Number of agents that get spawned into the simulation.
        :param player_controlled_agent: Define if a user controllable agent should be spawned.
        """
        self.size = size

        # Simulation element groups
        self.agents = []
        self.obstacles = pygame.sprite.Group()

        # Initialize fonts
        self.debug_font = pygame.font.SysFont('Arial', 14)
        self.entity_info_font = pygame.font.SysFont("Arial", 12)

        # Display states
        self.show_agent_debug_info = False
        self.show_agent_sensors = False
        self.show_control_hotkeys = True

        # Timers
        self.timer_agent_updates = 0
        self.timer_collision_handling = 0
        self.timer_draw_frame = 0

        # TODO TEMPORARY Add random obstacles
        for _ in range(5):
            self.add_obstacle(position=(random.randint(0, self.size[0]-300), random.randint(0, self.size[1]-300)),
                              width=random.randint(50, 500), height=random.randint(50, 500))

        # Add border obstacles
        self.add_border(thickness=50)

        # Calculate obstacle edges
        self.obstacle_edges = self.get_obstacle_edges()

        # Add agents to simulation
        for _ in range(number_of_agents):
            rand_speed = random.randint(1, 5)
            new_agent = Agent(simulation=self, movement_speed=rand_speed)
            new_agent.color = (280 - rand_speed * 25, 280 - rand_speed * 25, 255)
            self.agents.append(new_agent)

        # Add player controlled agent
        if player_controlled_agent:
            self.agents.append(PlayerControlledAgent(self, movement_speed=3, turning_speed=2, color=green))

    def process_events(self):
        """
        Process input events by the player
        :return State of simulation. True = Simulation ended.
        """
        for event in pygame.event.get():

            # CASE: Game closed
            if event.type == pygame.QUIT:
                return True

            elif event.type == pygame.KEYDOWN:
                # CASE: Toggle agent debug info
                if event.key == pygame.K_t:
                    self.show_agent_debug_info = False if self.show_agent_debug_info else True

                # CASE: Toggle agent sensors
                if event.key == pygame.K_r:
                    self.show_agent_sensors = False if self.show_agent_sensors else True

        return False

    def update(self):
        """
        Update/Step forward the simulation
        """

        # Step agent movements
        timer_start = time.time()
        for agent in self.agents:
            agent.update()
        self.timer_agent_updates = time.time() - timer_start

        """Collision detection"""

        timer_start = time.time()
        # Iterate over all agents and obstacles
        for agent in self.agents:
            for obstacle in self.obstacles:

                # Check collision of agent with environment
                if obstacle.rect.collidepoint(agent.location[0], agent.location[1]):
                    # If collision is detected, calculate collision coords and move agent to them
                    agent_travel_line = (agent.prev_location, agent.location)
                    collision_coordinates = self.calculate_collision_point(agent_travel_line, obstacle)
                    if collision_coordinates is not None:
                        agent.move(collision_coordinates)

                    # Old agent sensors environment obstacle detection (much slower)
                    """
                    if self.show_agent_sensors:
                        for i, sensor_coords in enumerate(agent.sensor_coords):
                            sensor_line = (agent.location, sensor_coords)
                            collision_coordinates = self.calculate_collision_point(sensor_line, obstacle,
                                                                                   multiple_collision_points=True)
                            if len(collision_coordinates) != 0:
                                collision_candidates = collision_coordinates
                                if agent.sensor_collisions[i] is not None:
                                    collision_candidates.append(agent.sensor_collisions[i])

                                distances = []
                                for col in collision_candidates:
                                    distances.append(self.calculate_distance(col, agent.location))

                                smallest_distance_index = distances.index(min(distances))
                                agent.sensor_collisions[i] = collision_candidates[smallest_distance_index]
                    """

        # Check collisions of agent sensors with environment
        if self.show_agent_sensors:  # TODO for debug reasons only calculate collisions if shown on screen
            for agent in self.agents:
                agent.sensor_collision_detection()

        self.timer_collision_handling = time.time() - timer_start

    def display_frame(self, screen, delta_time_last_frame, show_debug_info=True):
        """
        Draw all current game objects to a screen
        :param screen: pygame screen to draw the game objects on
        :param delta_time_last_frame: time since last frame draw. used to display fps in debug infos
        :param show_debug_info: show debug values at top left of screen
        """
        timer_start = time.time()

        # Reset screen
        screen.fill(black)

        # Draw obstacles
        self.obstacles.draw(screen)

        # Draw agents
        for agent in self.agents:

            # Draw entity info
            if self.show_agent_debug_info:
                pygame.draw.circle(screen, red, (agent.location[0], agent.location[1]), 2, 2)

                text_surface = self.entity_info_font.render(f"({agent.location[0]},{agent.location[1]}) {agent.rotation}°",
                                                            False, white)
                screen.blit(text_surface, (agent.location[0] + 5, agent.location[1] - 15))

            # Draw sensors
            if self.show_agent_sensors:
                for i, sensor in enumerate(agent.vision_sensor.sensor_coords):
                    if agent.vision_sensor.sensor_collisions[i] is not None:
                        pygame.draw.line(screen, red, start_pos=agent.location, end_pos=agent.vision_sensor.sensor_collisions[i])
                        pygame.draw.circle(screen, red, agent.vision_sensor.sensor_collisions[i], 2, 2)
                    else:
                        pygame.draw.line(screen, green, start_pos=agent.location, end_pos=sensor)

            # Rotate entity polygon to entities rotation and add its current location
            entity_polygon = self.rotate_polygon(Simulation.entity_polygon, agent.rotation)
            for i, coords in enumerate(entity_polygon):
                entity_polygon[i] = (coords[0] + agent.location[0], coords[1] + agent.location[1])

            # Draw entity polygon
            pygame.draw.polygon(screen, agent.color, entity_polygon)

        # Display simulation infos
        if show_debug_info:
            # FPS
            text_surface = self.debug_font.render(f"FPS: {round(1 / delta_time_last_frame)}", True, white)
            screen.blit(text_surface, (2, 0))
            # Number of entities
            text_surface = self.debug_font.render(f"Num Entities: {len(self.agents)}", True, white)
            screen.blit(text_surface, (2, 14))
            # Timers
            text_surface = self.debug_font.render(f"Agent Updates: {round(self.timer_agent_updates * 1000)}ms", True, white)
            screen.blit(text_surface, (140, 0))
            text_surface = self.debug_font.render(f"Collision Handling: {round(self.timer_collision_handling * 1000)}ms", True, white)
            screen.blit(text_surface, (140, 14))
            text_surface = self.debug_font.render(f"Draw Time: {round(self.timer_draw_frame * 1000)}ms", True, white)
            screen.blit(text_surface, (140, 28))

        # Display hotkey infos
        if self.show_control_hotkeys:
            text_surface = self.debug_font.render("(T) Toggle Agent Info", True, blue)
            screen.blit(text_surface, (2, self.size[1] - 18))

            text_surface = self.debug_font.render("(R) Toggle Agent Sensors", True, blue)
            screen.blit(text_surface, (2, self.size[1] - 34))

        self.timer_draw_frame = time.time() - timer_start

    def add_obstacle(self, position: (int, int), width: int, height: int):
        new_obstacle = Obstacle(position, width, height)
        self.obstacles.add(new_obstacle)

    def calculate_collision_point(self, line, obstacle, multiple_collision_points=False):
        """

        :param line:
        :param obstacle:
        :param multiple_collision_points: Enable, if multiple collisions points are possible with the obstacle.
                                          Togglable because of performance gains.
        :return:
        """
        # Obstacle edge points
        top_left = (obstacle.rect.x, obstacle.rect.y)
        top_right = (obstacle.rect.x + obstacle.rect.width, obstacle.rect.y)
        bottom_left = (obstacle.rect.x, obstacle.rect.y + obstacle.rect.height)
        bottom_right = (obstacle.rect.x + obstacle.rect.width, obstacle.rect.y + obstacle.rect.height)

        # Obstacle edge lines
        edge_top = (top_left, top_right)
        edge_right = (top_right, bottom_right)
        edge_bottom = (bottom_left, bottom_right)
        edge_left = (top_left, bottom_left)
        obstacle_lines = (edge_top, edge_right, edge_bottom, edge_left)

        if multiple_collision_points:
            intersections = []

        # Check every obstacle edge with the travel line of the agent
        for obstacle_edge in obstacle_lines:
            intersection = self.line_intersection(obstacle_edge, line)
            if intersection is not None:
                if multiple_collision_points:
                    intersections.append(intersection)
                else:
                    return intersection

        if multiple_collision_points:
            return intersections
        else:
            return None

    def add_border(self, thickness: int = 20):
        self.add_obstacle(position=(0, 0), width=thickness, height=self.size[1])
        self.add_obstacle(position=(0, 0), width=self.size[0], height=thickness)
        self.add_obstacle(position=(self.size[0]-thickness, 0), width=thickness, height=self.size[1])
        self.add_obstacle(position=(0, self.size[1]-thickness), width=self.size[0], height=thickness)

    @staticmethod
    def calculate_distance(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    @staticmethod
    def rotate_polygon(polygon, angle):
        # Convert angle to radians
        angle_rad = math.radians(angle)
        # Define the rotation matrix
        rotation_matrix = [
            [math.cos(angle_rad), -math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ]
        # Apply the rotation matrix to each point
        rotated_polygon = []
        for point in polygon:
            rotated_point = [
                point[0] * rotation_matrix[0][0] + point[1] * rotation_matrix[0][1],
                point[0] * rotation_matrix[1][0] + point[1] * rotation_matrix[1][1]
            ]
            rotated_polygon.append(rotated_point)
        return rotated_polygon

    @staticmethod
    def line_intersection(line1, line2, finite_line=True):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)

        # Lines do not intersect
        if div == 0:
            return None

        d = (det(*line1), det(*line2))
        x = round(det(d, xdiff) / div)
        y = round(det(d, ydiff) / div)

        if finite_line:
            # Check if the intersection is within the bounds of line1
            if not (min(line1[0][0], line1[1][0]) <= x <= max(line1[0][0], line1[1][0]) and
                    min(line1[0][1], line1[1][1]) <= y <= max(line1[0][1], line1[1][1])):
                return None

            # Check if the intersection is within the bounds of line2
            if not (min(line2[0][0], line2[1][0]) <= x <= max(line2[0][0], line2[1][0]) and
                    min(line2[0][1], line2[1][1]) <= y <= max(line2[0][1], line2[1][1])):
                return None

        return x, y

    def get_obstacle_edges(self):
        obstacle_edges = []

        for obstacle in self.obstacles:
            # Obstacle edge points
            top_left = (obstacle.rect.x, obstacle.rect.y)
            top_right = (obstacle.rect.x + obstacle.rect.width, obstacle.rect.y)
            bottom_left = (obstacle.rect.x, obstacle.rect.y + obstacle.rect.height)
            bottom_right = (obstacle.rect.x + obstacle.rect.width, obstacle.rect.y + obstacle.rect.height)

            # Obstacle edge lines
            edge_top = (top_left, top_right)
            edge_right = (top_right, bottom_right)
            edge_bottom = (bottom_left, bottom_right)
            edge_left = (top_left, bottom_left)

            obstacle_edges += [edge_top, edge_right, edge_bottom, edge_left]

        return obstacle_edges


if __name__ == '__main__':
    run_simulation((1280, 720), simulation_fps=60, number_of_agents=100, player_controlled_agent=True)
