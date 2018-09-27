# MonicarS

A simple 2D environment for autonomous driving in the style of OpenAI Gym environments.

# NOTE

Made altercations to get the behavior that I want. -Lucas Berry September 2018

## Installation

Clone the simulation package from GitHub. To install, do:

```bash
cd MonicarS
sudo pip install -e .
```

The `-e` installs the files using simlinks, which means that if you want to update the code using `git pull`, you can do so without reinstalling.

## Usage

Use the code as follows:

```python
from monicars import Environment

env = Environment("intersection")
```

You can quickly visualize the current setup of the environment by running:
```bash
python -m monicars.monicars [ENV_NAME]
```
Provide your environment name of choice as `ENV_NAME`. If you don't provide one, the `two_lane` environment is used.

## Basic Usage

MonicarS has a very similar interface to OpenAI gym, but allows for more control over the environment and the agent configuration. There are two important objects needed, instead of just one: the environment and the agent. The current agent, a unicycle model, can be used out of the box. In the future, more help will be provided to create your own agent.

Here is a simple example usage:

```python
from monicars import Environment
from monicars.variables import global_var

env = Environment("intersection")

env.reset()

done = False
while not done:
    obs, reward, done = env.step([0, 0])
    env.clock.tick(global_var.FPS)

env.quit()
```

You have to pass a string with the name of the environment and an agent object when instantiating the environment. The name must match an image and a YAML in the `maps` folder.

When you `step` the environment, you must pass a list containing the acceleration and the angular acceleration you want to apply to the car. This function returns the state, the reward (currently not implemented) and a boolean indicating if the episode is terminated.

### Environment Options

A number of keyword arguments control certain common behaviours of the environment.

* `render`: Whether the environment should be rendered. Defaults to True.
* `vision`: Whether to return raw pixel values as the observation. Defaults to False.
* `obstacle`: Whether to use the special Obstacle NPC. Defaults to False.
* `decimals`: How many decimals to round to for observations. Defaults to no rounding.
* `reward_function`: Reward function to use. Defaults to a reward function that returns zero.
* `feature_function`: A function to transform observations to a feature vector. Defaults to return the observations without modification.
* `tick`: Whether to tick the clock at the desired frequency when stepping the env. Defaults to False.
* `flip`: Whether to flip the display so that the user can control the car more easily. Defaults to False.
* `scroll`: Whether to follow the view of the agent or generate the whole environment. Defaults to True.

### Observation

The observation contains by default all the information possible. It is not necessarily usable as a feature vector, unless you provide a feature function (more on that below). All distances are in pixels, all angles are in radians and all speeds are in pixels/timestep. The array is a one dimentional array of length N, organized as follows:

```
[AGENT STATE, NPC STATES]
```
The components of the agent state are:

```
x, y, theta, speed
```

The NPC states contain the state of all the cars, zero padded if less than max cars are on the road. If you are using the Obstacle NPC, it will always be the first object in the NPC list.

#### Custom Feature Functions

If you would like the environment to return a feature vector of your own design to you, you can pass in a function through the keyword argument `feature_function`. The function should accept a list of observations and return a list of features, for example:

```python
def custom_feature_fn(observation):
    return [observation[3], abs(observation[0])]

env = Environment("two_lanes", feature_function=custom_feature_fn)
```

### Custom Reward Functions

You can define a custom reward function to calculate the reward at each step of the simulation. The function has to accept a single argument, the observation list, and return a number. Here is an example of a not-so-useful reward function that returns the sum of the observation as a reward:

```python
def custom_reward(observation):
    return sum(observation)

env = Environment("two_lanes", reward_funtion=custom_reward)
```

## Configuration File

The configuration file is located in `config/config.yaml`. This is the file you should change to modify the behaviour of the simulation. Don't push changes to this file unless it is to add a new field.

Internally, the module `variables.py` loads the YAML and creates usable representations of the parameters. These variables should be used in any other module as opposed to accessing the YAML directly for consistency and readability. For example, to get the frame rate, do:

```python
from monicars.variables import global_var

frame_rate = global_var.FPS
```

You can also create your own `config.yaml` file. To use it, reload the default variables by calling the `monicars.variables.load_variables(PATH)` where `PATH` is the path to your config file.

### Initial Agent Parameters

The config file contains parameters which initialize the agent, including the initial position, speed and parameters used for optionally adding noise to these. Since it is cumbersome to change the starting position of the agent for each simulation environment, each map YAML file also contains a default starting position which makes most sense for the environment. The `use_pos` parameter controls which to use: if `False`, the default starting position from the map will be used, and if `True` the initial position in the config will be used.

### Traffic

This controls the traffic in the simulation. The NPC manager adds a new car to one of a set of start positions specified in the map configuration file with a probability of `freq` per frame. These use the speed of the agent for now. The maximum number of NPCs on the map at one time can be changed with parameter `max_cars`. If you don't want any other traffic on the road, set this to zero.

Currently, the cars will just travel at a constant speed across the map, disappearing when the exit the map. Crashing into an NPC car will end the episode.

### Obstacle Mode

In general, NPCs will appear at the beginning of lanes randomly. For certain scenarios, it is helpful to have an obstacle in front of the agent which has special behaviour. To use the obstacle, use the `obstacle=True` keyword argument when initializing the environment.

You can control the obstacle's starting position and orientation (you'll probably want it to be in front of the agent, facing the same direction), as well as its speed. You can also add Gaussian noise to its starting position by setting the `noise` parameter to `True` and assigning standard deviations for the x and y coordinates (note that all units are in pixels).

The obstacle has the added optional behaviour of occasionally crashing with some probability. To use this behaviour, set `crash: True` and use `crash_prob` to specify the probability that the obstacle will crash in each frame.

## Maps

Maps are in the `maps` directory and consist of a visual representation of the map, as a PNG image, and a description of the map as a YAML. For now, these are both manually generated.

## Running Tests

The tests are to ensure that the Rectangle geometry functions work. To run, in the `MonicarS` folder, do:

```bash
python -m test.geometry_test
```

## TODO

- [ ] Deal with NPC-NPC collisions
- [ ] Make NPCs plan paths in a reasonable way
- [ ] Better representation for map YAMLs
- [ ] Map YAML creation/visualization tool
- [ ] Remote control of car
- [x] Add noise to speed
- [x] Control NPC speed
