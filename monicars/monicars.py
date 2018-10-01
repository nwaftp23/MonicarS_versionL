#!/usr/bin/env python
from __future__ import print_function

import os
import yaml
import time
import pygame
from agent import Agent
from util import limit, input_to_action, is_close
from util import Rectangle, Line
from npc import NPCManager
from view import View
from variables import screen, global_var, agent, set_env


class Lane(Rectangle):
    """Lane zone. For now this is just a rectangle but it can hold imformation like
    which direction travel is allowed, speed limits, which rules the agent is violating, etc."""

    def __init__(self, corner, size, id):
        """Initializes the lane object.

        Args:
            corner: The top left corner of the lane.
            size: The width and height of the lane.
            id: The unique ID of the lane.
        """
        super(Lane, self).__init__((corner, (corner[0] + size[0], corner[1]),
                                   (corner[0] + size[0], corner[1] + size[1]),
                                   (corner[0], corner[1] + size[1])))
        self.id = id


class Intersection(Rectangle):
    """Intersection zone. For now this is just a rectangle but it can hold imformation like
    which direction travel is allowed, speed limits, which rules the agent is violating, etc."""

    def __init__(self, corner, size, id):
        """Initializes the Intersection object.

        Args:
            corner: The top left corner of the intersection.
            size: The width and height of the intersection.
            id: The unique ID of the intersection.
        """
        super(Intersection, self).__init__((corner, (corner[0] + size[0], corner[1]),
                                           (corner[0] + size[0], corner[1] + size[1]),
                                           (corner[0], corner[1] + size[1])))
        self.id = id


class Environment(object):
    """The simulation environment."""

    OBS_TYPES_NPC = ["closest_car", "closest_car_state", "all_cars", "obstacle_car_state"]
    OBS_TYPES_MAP = ["local", "global", "none"]

    def __init__(self, env_name, **kwargs):
        """Initializes the environment.

        Args:
            env_name: The name of the environment to display. This should have
                      a corresponding PNG image and YAML file with the same name
                      in the maps folder.

        Keyword Args:
            render: Whether the environment should be rendered. Defaults to True.
            vision: Whether to return raw pixel values as observations. Defaults to False.
            obstacle: Whether to use the special Obstacle NPC. Defaults to False.
            decimals: Number of decimals in the observations. Defaults to None (no rounding).
            reward_function: The reward funtion to use. Defaults to internal reward.
            feature_function: A function to transform observations to a feature vector.
            tick: Whether to tick the clock at the desired frequency when stepping the env. Defaults to False.
            flip: Whether to flip the display so that the user can control the car more easily. Defaults to False.
            scroll: Whether to follow the view of the agent or generate the whole environment. Defaults to True.
        """
        self.max_angle = global_var.MAX_ANGLE
        self.max_acc = global_var.MAX_ACC
        self.max_speed = global_var.MAX_SPEED

        set_env(env_name)

        # KEYWORD ARGS
        self.render = kwargs["render"] if "render" in kwargs else True
        self.vision = kwargs["vision"] if "vision" in kwargs else False
        self.obstacle = kwargs["obstacle"] if "obstacle" in kwargs else False
        self.decimals = kwargs["decimals"] if "decimals" in kwargs else None
        self.reward = kwargs["reward_function"] if "reward_function" in kwargs else self._default_reward
        self.feature_fn = kwargs["feature_function"] if "feature_function" in kwargs else self._default_feature_fn
        self.tick = kwargs["tick"] if "tick" in kwargs else False
        self.flip = kwargs["flip"] if "flip" in kwargs else False
        self.scroll = kwargs["scroll"] if "scroll" in kwargs else True

        # ZONES
        self.lanes = []
        self.intersections = []
        self.lane_markers = []

        with open(os.path.join(global_var.PATH, "maps", env_name + ".yaml")) as f:
            description = yaml.load(f)

        # Width and height of the actual environment.
        self.width = description["width"]
        self.height = description["height"]

        self._create_zones(description)

        # Choose whether to use the pos from the config or the default pos from the map.
        if agent.USE_POS:
            self.agent = Agent()
        else:
            pos = description["agent_start"]
            self.agent = Agent(pos["x"], pos["y"], pos["theta"])

        self._keep_agent_in_map()

        self.npc_manager = NPCManager(description["starts"], (self.width, self.height), self.obstacle)

        # Number of elements in the action and the observation vectors.
        self.observation_n = len(self._get_observation())
        self.action_n = 2

        self.clock = None
        self.display_surface = None

        # The PNG image of the map.
        if self.scroll:
            self.view = View(env_name, description["width"], description["height"],
                             screen.WIDTH, screen.HEIGHT, self.flip)
        else:
            self.view = View(env_name, description["width"], description["height"])

        self.setup()

    def setup(self):
        """Sets up the simulation environment and initializes the pygame environment."""
        if self.render or self.vision:
            self.display_surface = pygame.display.set_mode((self.view.screen_width, self.view.screen_height))

        if self.render:
            pygame.init()
            self.clock = pygame.time.Clock()
            pygame.display.set_caption('Traffic World')
            pygame.display.update()

    def quit(self):
        if self.render:
            pygame.quit()

    def step(self, action, npc_action=None):
        """Advances the environment forward by one time step.

        Args:
            action: The action the agent should take, in format (linear acceleration, angular acceleration).
            npc_action: A list of actions to control the NPCs. Optional.
        """
        # Bound the action values.
        limit(action[0], -1, 1)
        limit(action[1], -1, 1)

        # Convert the actions, which represent percentages, to the correct units.
        acc, theta = input_to_action(action)

        # Move the agent.
        self.agent.move(acc, theta)

        # Impose a limit on the agent's speed.
        self.agent.set_speed(limit(self.agent.get_speed(), -self.max_speed, self.max_speed))

        # Move the traffic.
        self.npc_manager.step(self.agent.bounding_box, npc_action)

        # Update the view if we're in rendering or vision mode.
        if self.render or self.vision:
            # Collect a list of all the cars and their images and states.
            cars = self._get_cars()

            # Get the view.
            surf = self.view.update(self.agent.get_x(), self.agent.get_y(), cars)

        # Render, if necessary.
        if self.render:
            self.display_surface.blit(surf, (0, 0))
            pygame.display.update()

        obs = self._get_observation()

        if self.tick:
            time.sleep(1.0 / global_var.FPS)

        done = self._get_done()

        self._keep_agent_in_map()
        collision = [self.collided()]
        if self.obstacle:
            stuck = [self.npc_manager.npcs[0].crash]

        return obs + collision +stuck, self.reward(obs), done

    def reset(self, state=None):
        """Resets the simulation.

        Args:
            state: The state to reset the environment to. Optional.

        Returns:
            Initial state.
        """
        self.agent.reset()
        self._keep_agent_in_map()
        self.npc_manager.reset()

        if self.render or self.vision:
            cars = self._get_cars()
            surf = self.view.update(self.agent.get_x(), self.agent.get_y(), cars)

        # Render, if necessary.
        if self.render:
            self.display_surface.blit(surf, (0, 0))
            pygame.display.update()

        if state is not None:
            self.set_state(state)

        return self._get_observation()

    def _create_zones(self, desc):
        """Populates all the necessary variables which create the environment.

        Args:
            desc: The environment description.
        """
        self.lanes = []
        self.intersections = []

        lane_i = 0
        int_i = 0
        for zone in desc["zones"]:
            if zone["label"] == "lane":
                self.lanes.append(Lane(zone["corner"], zone["size"], lane_i))
                lane_i += 1
            elif zone["label"] == "intersection":
                self.intersections.append(Intersection(zone["corner"], zone["size"], int_i))
                int_i += 1
            else:
                raise("Incorrect zone type provided.")

        for lane in desc["lane_markers"]:
            if lane["shape"] == "straight":
                self.lane_markers.append(Line(lane["points"]))
            else:
                raise("Unsupported lane marker shape.")

    def _get_lane(self):
        """Returns the lane ID of the the lane the agent is currently in. If
        the agent is not in a lane, returns None."""
        for lane in self.lanes:
            if lane.is_inside(self.agent.get_pos()):
                return lane.id

        return None

    def _get_intersection(self):
        """Returns the intersection ID of the the intersection the agent is
        currently in. If the agent is not in a intersection, returns None."""
        for intersection in self.intersections:
            if intersection.is_inside(self.agent.get_pos()):
                return intersection.id

        return None

    def get_zone(self):
        """Returns the zone which the agent is in using the format:

            ("type", ID)

        The types of zones are:
            - lane
            - intersection
            - on_road (for on an arbitrary type of road)
            - off_road
        """
        lane = self._get_lane()
        if lane is not None:
            return ("lane", lane)

        intersection = self._get_intersection()
        if intersection is not None:
            return ("intersection", intersection)

        colour = self._check_pixels()
        if colour in ["grey", "white"]:
            return ("on_road", 0)

        return ("off_road", 0)

    def on_road(self):
        """Returns True if the agent is on a road, False otherwise."""
        zone = self.get_zone()[0]

        if zone == "off_road":
            return False
        else:
            return True

    def _check_pixels(self):
        """Checks the colour of the pixel that the agent is on and returns the
        colour as a string. Supported colours are:
            - grey
            - black
            - white
            - green
            - unknown
        """
        c = self.view.get_colour(self.agent.get_x(), self.agent.get_y())

        r = c[0]
        g = c[1]
        b = c[2]

        # If the r, g and b values are close, the colour is grey, black or white.
        if is_close(r, g) and is_close(g, b):
            if r < 0.9 and r > 0.1:
                return "grey"
            elif r <= 0.1:
                return "black"
            else:
                return "white"

        # If g is sufficiently higher than r and b, the colour is green.
        if g - r > 0.2 and g - b > 0.2:
            return "green"

        return "unknown"

    def collided(self):
        """Returns True if the agent has collided with an NPC, False otherwise."""
        return self.npc_manager.check_collision(self.agent.bounding_box)

    def _get_closest_marker(self):
        """Returns the closest marker."""
        if len(self.lane_markers) == 0:
            return

        pos = self.agent.get_pos()

        min_idx = 0
        min_dist = self.lane_markers[min_idx].dist_to_point(pos)
        for i in range(1, len(self.lane_markers)):
            dist = self.lane_markers[i].dist_to_point(pos)
            if dist < min_dist:
                min_dist = dist
                min_idx = i

        return (min_dist, self.lane_markers[i].angle - self.agent.get_heading())

    def _get_done(self):
        """Returns whether the episode is done. Episode terminates if the agent
        collides with a car or leaves the map."""
        # Check if the agent is outside the map.
        outside = not self.agent.in_map(self.width, self.height)

        # Check if the agent has collided with another car.
        collision = self.collided()

        return outside or collision

    def _get_cars(self):
        """Gets a list of tuples where each tuple is of the form:

            (img, x, y, theta)

        for each car currently in the environment.
        """
        cars = [(self.agent.img, self.agent.get_x(), self.agent.get_y(), self.agent.get_heading())]
        for npc in self.npc_manager.npcs:
            cars.append((npc.img, npc.get_x(), npc.get_y(), npc.get_heading()))

        return cars

    def _get_observation(self):
        """The observation is either the raw pixels of the map, if the vision
        flag is True, or otherwise an array containing state information. All
        distances are in pixels, all angles are in radians and all speeds are
        in pixels/timestep. The array is a one dimentional array of length N,
        organized as follows:

            [AGENT STATE, NPC STATES]

        The components of the agent state are:

            x, y, theta, speed

        The NPC state is the state of all the NPC cars, zero padded if less
        than max cars are on the road:

                [x_i, y_i, theta_i, speed_i] x MAX CARS
        """
        if self.vision:
            return pygame.surfarray.array3d(self.display_surface)

        # AGENT STATE
        agent_state = list(self.agent.get_state())

        # NPC STATE
        npc_state = []

        for npc in self.npc_manager.npcs:
            npc_state += list(npc.get_state())

        # Pad with zeros.
        npc_state += [0, 0, 0, 0] * (self.npc_manager.MAX - len(self.npc_manager.npcs))

        observation = agent_state + npc_state

        if self.decimals is not None:
            observation = [round(float(x), self.decimals) for x in observation]

        return self.feature_fn(observation)

    def set_state(self, x_0):
        """Force set the initial state to a single state vector. Only all_cars
        and none observation type supported. Only one NPC car supported."""
        agent_state = x_0[0:4]
        npc_state = x_0[4:8]

        self.agent.set_state(agent_state[0], agent_state[1], agent_state[2], agent_state[3])

        if len(self.npc_manager.npcs) > 0:
            self.npc_manager.npcs[0].set_state(npc_state[0], npc_state[1], npc_state[2], npc_state[3])

    def _keep_agent_in_map(self):
        """Keeps the agent inside the map by limiting its position."""
        x = limit(self.agent.get_x(), 0, self.width)
        y = limit(self.agent.get_y(), 0, self.height)
        self.agent.set_x(x)
        self.agent.set_y(y)

    def _default_reward(self, observation):
        """Default reward function, which always returns no reward."""
        return 0

    def _default_feature_fn(self, observation):
        """Default feature function, which returns the full observation."""
        return observation


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        env_name = sys.argv[1]
    else:
        env_name = "two_lanes"

    env = Environment(env_name, obstacle=False, tick=True)

    env.reset()

    done = False
    quit = False
    while not done and not quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True

        obs, _, done = env.step([0, 0])
        print(obs, env.get_zone())

    env.quit()
