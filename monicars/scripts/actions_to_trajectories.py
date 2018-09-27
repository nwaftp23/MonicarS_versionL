#!/usr/bin/env python

from __future__ import print_function

import sys
import pickle
from monicars import Environment

if len(sys.argv) < 3:
    print("Usage:")
    print("\tpython actions_to_trjectories.py in_file out_file")
    sys.exit()

action_path = sys.argv[1]

with open(action_path, 'rb') as f:
    data = pickle.load(f)

env = Environment("two_lanes", tick=False, render=False)

observations = []

for action in data:
    obs, _, _ = env.step(action)
    observations.append(obs)

env.quit()

state_file = sys.argv[2]

with open(state_file, 'w') as f:
    pickle.dump(observations, f)
