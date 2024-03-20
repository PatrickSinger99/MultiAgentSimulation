import random
from abc import ABC, abstractmethod
from typing import Tuple, Union


class Policy(ABC):
    @staticmethod
    @abstractmethod
    def execute(agent) -> Tuple[Union[int, float], Union[int, float]]:
        """
        Takes the agent instance as input and uses its current parameters to determine the change in rotation and
        location for the agent. Needs to be defined as static method!
        :param agent: parent agent instance of the Agent class
        :return: Tuple[Union[float, int], Union[float, int]]: A tuple containing delta rotation and delta location
        """
        pass


class RandomPolicy(Policy):
    """
    Simple policy that randomly decides the change in rotation and location. Limited by the agents max speeds.
    """
    @staticmethod
    def execute(agent):
        delta_rotation = random.randint(-agent.turning_speed, agent.turning_speed)
        delta_location = random.randint(1, agent.movement_speed)

        return delta_rotation, delta_location


class SimpleCollisionAvoidancePolicy(Policy):
    """
    Simple obstacle avoidance policy that turns away if obstacles are detected on the furthest out sensors
    """

    @staticmethod
    def execute(agent):
        # Turn in the opposite direction if a obstacle is detected on the sensor furthest to one side
        if agent.vision_sensor.sensor_collisions[-1] is not None:
            delta_rotation = - agent.turning_speed

        elif agent.vision_sensor.sensor_collisions[0] is not None:
            delta_rotation = agent.turning_speed

        # If none are detected, decide randomly
        else:
            delta_rotation = random.randint(-agent.turning_speed, agent.turning_speed)

        # Always move forward at max speed
        delta_location = agent.movement_speed

        return delta_rotation, delta_location
