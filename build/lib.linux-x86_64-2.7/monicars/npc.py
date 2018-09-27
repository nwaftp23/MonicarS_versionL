"""Non player characters for the game.

Special features: There is some randomness in their initial positions and speeds."""
import numpy as np
from agent import Agent
from variables import traffic, obstacle
from util import add_noise, input_to_action
from scipy.spatial.distance import euclidean

# TODO: Deal with NPC-NPC collisions


class Obstacle(Agent):
    """Obstacle object, which is useful for various situations where we need
    an obstacle in front of the agent. It has its own speed and initial location,
    and can also crash with certain probability."""

    def __init__(self):
        name = traffic.TYPES[np.random.randint(0, len(traffic.TYPES))]

        if obstacle.NOISE:
            x = add_noise(obstacle.X, obstacle.STD_X)
            y = add_noise(obstacle.Y, obstacle.STD_Y)
            speed = add_noise(obstacle.SPEED, obstacle.STD_SPEED)
        else:
            x = obstacle.X
            y = obstacle.Y
            speed = obstacle.SPEED

        self.init_x = x
        self.init_y = y
        self.init_speed = speed
        self.init_theta = obstacle.THETA

        super(Obstacle, self).__init__(self.init_x, self.init_y, self.init_theta, self.init_speed, name)

        self.crash = obstacle.CRASH and np.random.random() < obstacle.PROB_CRASH
        self.crash_y = obstacle.CRASH_Y
        self.crashing = False

    def move(self, acc, heading):
        # Check if there is a crash.
        if self.crash and self.get_y() >= self.crash_y:
            self.crashing = True

        # If the car is crashing, send a deceleration command.
        if self.crashing:
            if self.get_speed() > 0:
                return super(Obstacle, self).move(-2, 0)

        # Step the obstacle forward.
        return super(Obstacle, self).move(acc, heading)

    def reset(self, noise=True):
        theta = obstacle.THETA
        if obstacle.NOISE and noise:
            x = add_noise(obstacle.X, obstacle.STD_X)
            y = add_noise(obstacle.Y, obstacle.STD_Y)
            speed = add_noise(obstacle.SPEED, obstacle.STD_SPEED)
        else:
            x = self.init_x
            y = self.init_y
            speed = self.init_speed

        self.crash = obstacle.CRASH and np.random.random() < obstacle.PROB_CRASH
        self.crashing = False
        self.set_state(x, y, theta, speed)
        self.bounding_box.move_to(x, y, theta)


class NPCManager(object):
    """NPC Manager."""

    NEW = traffic.FREQ
    MAX = traffic.MAX_CARS
    DIRS = {"down": 0, "right": np.pi / 2, "up": np.pi, "left": -np.pi / 2}

    def __init__(self, starts, env_size, use_obstacle=False):
        """Initializes the NPC Manager.

        Args:
            starts: List of starting positions for NPCs.
            env_size: The size of the environment in the form (width, height).
            use_obstacle: Whether to use the special Obstacle NPC. Defaults to False.
        """
        self.starts = starts
        self.npcs = []
        self.env_size = env_size
        self.obstacle = use_obstacle
        self.obstacle_gone = False  # Flag to keep track of whether the obstacle is there.

        if self.obstacle:
            obstacle = Obstacle()
            self.npcs.append(obstacle)
            self.MAX += 1

    def step(self, agent_bb, actions=None):
        """Steps forward the NPCs.

        Args:
            agent_bb: The bounding box of the agent, for collision checking.
            actions: A list of actions to control the agent. Optional.
        """
        if actions is None:
            actions = [[0, 0] * len(self.npcs)]

        # Crop actions so they aren't too long.
        actions = actions[0:len(self.npcs)]
        # Pad actions with zero so they aren't too short.
        actions += [[0, 0] * (len(self.npcs) - len(actions))]

        # Apply actions to each NPC.
        for npc, action in zip(self.npcs, actions):
            acc, theta = input_to_action(action)
            npc.move(acc, theta)

        # Check whether to add a new NPC. New NPC is added with probability NEW
        # per frame, as long as there are less than MAX non-agent cars on the
        # road and there exists at least one start position defined.
        prob_new = np.random.random() < self.NEW
        not_full = len(self.npcs) < self.MAX
        start_exists = len(self.starts) > 0

        new_npc = prob_new and not_full and start_exists

        if new_npc:
            pos = np.random.randint(0, len(self.starts))
            start = self.starts[pos]["position"]
            theta = self.DIRS[self.starts[pos]["orientation"]]
            speed = traffic.SPEED
            colour = traffic.TYPES[np.random.randint(0, len(traffic.TYPES))]

            new = Agent(start[0], start[1], theta, speed, colour)

            # Only add if it doesn't collide with other NPCs.
            if not self.check_collision(new.bounding_box) and not new.bounding_box.overlaps(agent_bb):
                self.npcs.append(new)

        for i, npc in enumerate(self.npcs):
            if not npc.in_map(self.env_size[0], self.env_size[1]):
                if type(npc) == Obstacle:
                    self.obstacle_gone = True
                del self.npcs[i]

    def check_collision(self, bbox):
        """Checks for a collision with the bounding box provided.

        Args:
            bbox: The bounding box to check.
        """
        for npc in self.npcs:
            if npc.bounding_box.overlaps(bbox):
                return True

        return False

    def reset(self):
        """Resets the NPCs."""
        self.npcs = []

        if self.obstacle:
            self.obstacle_gone = False
            obstacle = Obstacle()
            self.npcs.append(obstacle)

    def get_obstacle(self):
        """Returns the obstacle object."""
        if self.obstacle and not self.obstacle_gone:
            return self.npcs[0]

        return None

    def get_closest(self, pos):
        """Returns the NPC closest to the provided position.

        Args:
            pos: The position to test.
        """
        if self.empty():
            return

        min_idx = 0
        min_dist = euclidean(pos, self.npcs[0].get_pos())

        for i in range(1, len(self.npcs)):
            dist = euclidean(pos, self.npcs[i].get_pos())
            if dist < min_dist:
                min_dist = dist
                min_idx = i

        return self.npcs[min_idx], min_dist

    def empty(self):
        """Returns True if the NPC list is empty, False otherwise."""
        if len(self.npcs) == 0:
            return True

        return False
