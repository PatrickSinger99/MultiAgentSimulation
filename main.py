import pygame
from pygame_agent import Agent
import math


def run_simulation(screen_size_x: int, screen_size_y: int, number_of_agents: int = 20, simulation_fps = 30):

    # Initialize Pygame and set up the window
    pygame.init()
    pygame.font.init()
    debug_font = pygame.font.SysFont('Arial', 14)
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
        simulation.display_frame(screen)

        # Display FPS
        text_surface = debug_font.render(f"FPS: {round(1 / delta_time_last_frame)}", False, (255, 255, 255))
        screen.blit(text_surface, (0, 20))

        # Display updated screen
        pygame.display.flip()

        # Tick game and save time this frame took to render
        delta_time_last_frame = clock.tick(simulation_fps) / 1000


class Simulation:

    entity_polygon = [(0, 0), (-10, -5), (-8, 0), (-10, +5)]

    def __init__(self, size, number_of_agents):
        self.size = size
        self.agents = []

        self.entity_info_font = pygame.font.SysFont("Arial", 12)

        for _ in range(number_of_agents):
            self.agents.append(Agent(simulation=self))


    def process_events(self):
        """
        Process input events by the player
        """
        for event in pygame.event.get():

            # CASE: Game closed
            if event.type == pygame.QUIT:
                return True

        return False

    def update(self):
        """
        Update/Step forward the simulation
        """

        # Step agent movements
        for agent in self.agents:
            agent.update()

    def display_frame(self, screen):
        """
        Draw all current game objects to a screen
        :param screen: pygame screen to draw the game objects on
        """

        # Reset screen
        screen.fill((0, 0, 0))


        # Draw agents
        for agent in self.agents:
            pygame.draw.circle(screen, (255, 0, 0), (agent.location[0], agent.location[1]), 2, 2)

            # Draw entity info
            text_surface = self.entity_info_font.render(f"x={agent.location[0]}, y={agent.location[1]}, rot={agent.rotation}",
                                                        False, (255, 255, 255))
            screen.blit(text_surface, (agent.location[0] + 5, agent.location[1] - 15))

            # Rotate entity polygon to entities rotation and add its current location
            entity_polygon = self.rotate_polygon(Simulation.entity_polygon, agent.rotation)
            for i, coords in enumerate(entity_polygon):
                entity_polygon[i] = (coords[0] + agent.location[0], coords[1] + agent.location[1])

            # Draw entity polygon
            pygame.draw.polygon(screen, (255, 255, 255), entity_polygon)

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


if __name__ == '__main__':
    run_simulation(1280, 720, simulation_fps=5)
