import pygame
from pygame_agent import Agent
from pygame_obstacle import Obstacle
import math
from colors import *
import random


def run_simulation(screen_size_x: int, screen_size_y: int, number_of_agents: int = 20, simulation_fps: int = 30):

    # Initialize Pygame and set up the window
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("Simulation")
    screen = pygame.display.set_mode([screen_size_x, screen_size_y])

    # Create game loop variables
    done = False
    clock = pygame.time.Clock()
    delta_time_last_frame = 1

    # Create Game instance
    simulation = Simulation(size=(screen_size_x, screen_size_y), number_of_agents=number_of_agents)

    """ MAIN GAME LOOP """

    while not done:

        done = simulation.process_events()
        simulation.update()
        simulation.display_frame(screen, delta_time_last_frame)

        # Display updated screen
        pygame.display.flip()

        # Tick game and save time this frame took to render
        delta_time_last_frame = clock.tick(simulation_fps) / 1000


class Simulation:

    # Figures
    entity_polygon = [(0, 0), (-10, -5), (-8, 0), (-10, +5)]

    def __init__(self, size, number_of_agents):
        self.size = size
        self.agents = []
        self.obstacles = pygame.sprite.Group()

        # Initialize fonts
        self.debug_font = pygame.font.SysFont('Arial', 14)
        self.entity_info_font = pygame.font.SysFont("Arial", 12)

        # States
        self.show_agent_debug_info = False

        # TEMP Add random obstacles
        for _ in range(5):
            self.add_obstacle(position=(random.randint(0, self.size[0]-300), random.randint(0, self.size[1]-300)),
                              width=random.randint(50, 500),
                              height=random.randint(50, 500))

        # Add agents to simulation
        for _ in range(number_of_agents):
            self.agents.append(Agent(simulation=self, movement_speed=3))

    def process_events(self):
        """
        Process input events by the player
        """
        for event in pygame.event.get():

            # CASE: Game closed
            if event.type == pygame.QUIT:
                return True

            elif event.type == pygame.KEYDOWN:
                # CASE: Toggle agend debug info
                if event.key == pygame.K_t:
                    self.show_agent_debug_info = False if self.show_agent_debug_info else True

        return False

    def update(self):
        """
        Update/Step forward the simulation
        """

        # Step agent movements
        for agent in self.agents:
            agent.update()

        # Collision detection
        for agent in self.agents:
            for obstacle in self.obstacles:

                # If collision is detected, calculate collision coords and move agent to them
                if obstacle.rect.collidepoint(agent.location[0], agent.location[1]):
                    collision_coordinates = self.calculate_collision_point(agent, obstacle)
                    if collision_coordinates is not None:
                        agent.move(collision_coordinates)

    def display_frame(self, screen, delta_time_last_frame, show_debug_info=True):
        """
        Draw all current game objects to a screen
        :param screen: pygame screen to draw the game objects on
        :param delta_time_last_frame
        :param show_debug_info
        """

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

            # Rotate entity polygon to entities rotation and add its current location
            entity_polygon = self.rotate_polygon(Simulation.entity_polygon, agent.rotation)
            for i, coords in enumerate(entity_polygon):
                entity_polygon[i] = (coords[0] + agent.location[0], coords[1] + agent.location[1])

            # Draw entity polygon
            pygame.draw.polygon(screen, agent.color, entity_polygon)

        # Display simulation infos
        if show_debug_info:
            # FPS
            text_surface = self.debug_font.render(f"FPS: {round(1 / delta_time_last_frame)}", False, white)
            screen.blit(text_surface, (0, 0))
            # Number of entities
            text_surface = self.debug_font.render(f"Num Entities: {len(self.agents)}", False, white)
            screen.blit(text_surface, (0, 14))

        # Display hotkey infos
        text_surface = self.debug_font.render("(t) Toggle agent info", False, blue)
        screen.blit(text_surface, (0, self.size[1] - 14))

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

    def add_obstacle(self, position: (int, int), width: int, height: int):
        new_obstacle = Obstacle(position, width, height)
        self.obstacles.add(new_obstacle)

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
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div

        if finite_line:
            # Check if the intersection is within the bounds of line1
            if not (min(line1[0][0], line1[1][0]) <= x <= max(line1[0][0], line1[1][0]) and
                    min(line1[0][1], line1[1][1]) <= y <= max(line1[0][1], line1[1][1])):
                return None

            # Check if the intersection is within the bounds of line2
            if not (min(line2[0][0], line2[1][0]) <= x <= max(line2[0][0], line2[1][0]) and
                    min(line2[0][1], line2[1][1]) <= y <= max(line2[0][1], line2[1][1])):
                return None

        return round(x), round(y)

    def calculate_collision_point(self, agent, obstacle):
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

        # Agent line
        agent_travel_line = (agent.prev_location, agent.location)

        # Check every obstacle edge with the travel line of the agent
        for obstacle_edge in obstacle_lines:
            intersection = self.line_intersection(obstacle_edge, agent_travel_line)
            if intersection is not None:
                return intersection

        return None


if __name__ == '__main__':
    run_simulation(1280, 720, simulation_fps=60, number_of_agents=1000)
