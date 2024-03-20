import pygame
import math
import time

from src.colors import *
from src.sim_objects.agent_policy import *
from src.sim_objects.agent import Agent, PlayerControlledAgent
from src.sim_objects.obstacle import Obstacle
from src import utils
from src.gui_objects.agent_camera import AgentCameraSurface


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
        self.show_agent_pov = True  # TODO TEST

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
            # TODO: TEMP test with randowm agent parameter values
            rand_speed = random.randint(1, 5)
            rand_fov = random.randint(30, 120)
            rand_sensor_length = random.randint(10, 100)
            rand_num_sensors = random.randint(1, 10)
            new_agent = Agent(simulation=self, movement_speed=rand_speed, vision_sensors_fov=rand_fov,
                              vision_sensors_length=rand_sensor_length, num_vision_sensors=rand_num_sensors)
            new_agent.color = (280 - rand_speed * 25, 280 - rand_speed * 25, 255)
            self.agents.append(new_agent)

        # Add player controlled agent
        if player_controlled_agent:
            self.user_controlled_agent = PlayerControlledAgent(self, movement_speed=3, turning_speed=2, color=green,
                                                               vision_sensors_fov=75, vision_sensors_length=300,
                                                               num_vision_sensors=100)  # Add more sensors for user agent
            self.agents.append(self.user_controlled_agent)

        # Add agent vision pov surface
        self.agent_camera_dimensions = (320, 180)
        self.agent_camera_surface = AgentCameraSurface(size=self.agent_camera_dimensions,
                                                       agent=self.user_controlled_agent)

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

        # TODO TEMP Agents use policy depending on if sensors are shown
        use_policy = RandomPolicy if not self.show_agent_sensors else SimpleCollisionAvoidancePolicy

        # Step agent movements
        timer_start = time.time()
        for agent in self.agents:
            agent.update(policy=use_policy)
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

        # Display obstacles
        self.obstacles.draw(screen)

        # Display agents
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
            entity_polygon = utils.rotate_polygon(Simulation.entity_polygon, agent.rotation)
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

        # Display the agent camera (POV) in the bottom right corner of the screen
        if self.show_agent_pov:
            draw_coords = (self.size[0] - self.agent_camera_dimensions[0],
                           self.size[1] - self.agent_camera_dimensions[1])
            self.agent_camera_surface.display()  # Update camera display
            screen.blit(self.agent_camera_surface, draw_coords)

        self.timer_draw_frame = time.time() - timer_start

    def add_obstacle(self, position: (int, int), width: int, height: int):
        """
        Add an obstacle to the simulation and its sprite group.
        :param position: (x, y) coordinates for top left position of the obstacle.
        :param width: Width of the obstacle.
        :param height: Height of the obstacle.
        """
        new_obstacle = Obstacle(position, width, height)
        self.obstacles.add(new_obstacle)

    @staticmethod
    def calculate_collision_point(line, obstacle, multiple_collision_points=False):
        """
        Calculate the collision(s) between a line and an obstacle. Runs line intersections for all edges of the obstacle
        :param line: Line with its start and end coordinates.
        :param obstacle: Obstacle object from the simulation.
        :param multiple_collision_points: Enable, if multiple collisions points are possible with the obstacle.
                                          Togglable because of performance gains.
        :return: List or Point of collision(s) depending on the multiple_collision_points parameter.
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

        # List of collisions. Only used when multiple_collision_points is true
        intersections = []

        # Check every obstacle edge with the travel line of the agent
        for obstacle_edge in obstacle_lines:
            intersection = utils.line_intersection(obstacle_edge, line)
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
        """
        Adds a border of obstacle objects around the simulation area.
        :param thickness: width of the border.
        """
        self.add_obstacle(position=(0, 0), width=thickness, height=self.size[1])
        self.add_obstacle(position=(0, 0), width=self.size[0], height=thickness)
        self.add_obstacle(position=(self.size[0]-thickness, 0), width=thickness, height=self.size[1])
        self.add_obstacle(position=(0, self.size[1]-thickness), width=self.size[0], height=thickness)

    def get_obstacle_edges(self):
        """
        Calculate and store all edges that the objects in the simulation have. This is intended to be run once at the
        beginning of the simulation. By storing all edges as coordinates, collision detection is sped up.
        :return: List of obstacle edge coordinates.
        """
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
