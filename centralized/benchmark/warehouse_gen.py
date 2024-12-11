# File to generate benchmarks based on a warehouse environment
import sys
sys.path.insert(0, '../')
import argparse
import math
import random
import yaml
from itertools import combinations
from copy import deepcopy

def make_map(args):
    # Each warehouse "block" is 2x3, plus 1-wide paths, plus edges for robot starts
    dims = [4 * args.width + 3, 3 * args.height + 3]
    obstacles = [(0,0), (4 * args.width + 2,0), (0,3 * args.height + 2), (4 * args.width + 2,3 * args.height + 2)]
    for i in range(1, 4 * args.width + 1):
        for j in range(1, 3 * args.height + 1):
            if i % 4 != 1 and j % 3 != 1:
                obstacles.append((i, j))
    return {'dimensions': dims, 'obstacles': obstacles}

def generate_goals(args):
    feasible_goals = []
    # Add goals in internal rows and rows
    for j in range(args.height - 1):
        for i in range(2, 4 * args.width + 1):
            if i % 4 != 1:
                feasible_goals.append([i, 4 + 3*j])
    for i in range(args.width - 1):
        for j in range(2, 3 * args.height + 1):
            if j % 3 != 1:
                feasible_goals.append([5 + 4*i, j])
    if len(feasible_goals) < args.agents:
        print("Too many agents!")
        return []
    return random.sample(feasible_goals, args.agents)

def place_agents(args):
    feasible_starts = []
    max_agents = 6 * args.height + 8 * args.width + 4
    if args.agents > max_agents:
            print("Too many agents!")
            return []
    for i in range(max_agents):
        if i < 4 * args.width + 1:
            feasible_starts.append([i+1, 0])
        elif i < 3 * args.height + 4 * args.width + 2:
            feasible_starts.append([4 * args.width + 2, i-4*args.width])
        elif i < 3 * args.height + 8 * args.width + 3:
            feasible_starts.append([3 * args.height + 8 * args.width + 3 - i, 3 * args.height + 2])
        else:
            feasible_starts.append([0, 6 * args.height + 8 * args.width + 4 - i])
    starts = []
    if args.placement == 'adjacent':
        starts = feasible_starts[:args.agents]
    elif args.placement == 'spaced':
        starts = [feasible_starts[math.floor(i*max_agents/args.agents)] for i in range(args.agents)]
    elif args.placement == 'random':
        starts = random.sample(feasible_starts, args.agents)
    else:
        print("Invalid agent placement strategy")
        return []
    goals = generate_goals(args)
    if goals == []:
        return []
    agents = [{'start': starts[i], 'goal': goals[i], 'name': 'agent'+str(i)} for i in range(args.agents)]
    return agents

def tuple_representer(dumper, value):
    return dumper.represent_sequence('tag:yaml.org,2002:python/tuple', value)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("height", type=int, help="Number of warehouse columns to add")
    parser.add_argument("width", type=int, help="Number of warehouse rows to add")
    parser.add_argument("agents", type=int, help="Number of agents")
    parser.add_argument("--placement", type=str, default='adjacent', help="adjacent - agents placed next to each other, spaced - agents are evenly spaced, random - agents are placed randomly")
    args = parser.parse_args()

    if args.agents < 1:
        print("ERROR: Must have at least 1 agent")
    if args.width <= 1 or args.height <= 1:
        print("ERROR: width and height must be at least 2")

    warehouse_map = make_map(args)
    agents = place_agents(args)

    if agents == []:
        print("Agent placement failed")
        return

    # Write to file
    yaml_file = {'agents': agents, 'map': warehouse_map}
    yaml.add_representer(tuple, tuple_representer)
    # Note: only one map of each height/width/agent/placement configuration can exist at once at the moment
    file_name = "warehouse/map_" + str(args.height) + "by" + str(args.width) + "_agents" + str(args.agents) + "_" + args.placement + ".yaml"
    with open(file_name, 'w') as input_yaml:
        yaml.dump(yaml_file, input_yaml, default_flow_style=True)

if __name__ == "__main__":
    main()