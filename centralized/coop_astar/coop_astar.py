"""

Python implementation of Conflict-based search

author: Ashwin Bose (@atb033)

"""
import sys
sys.path.insert(0, '../')
import argparse
import yaml
from math import fabs
from itertools import combinations
from copy import deepcopy

from cbs.a_star import AStar

class Location(object):
    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __str__(self):
        return str((self.x, self.y))

class State(object):
    def __init__(self, time, location):
        self.time = time
        self.location = location
    def __eq__(self, other):
        return self.time == other.time and self.location == other.location
    def __hash__(self):
        return hash(str(self.time)+str(self.location.x) + str(self.location.y))
    def is_equal_except_time(self, state):
        return self.location == state.location
    def __str__(self):
        return str((self.time, self.location.x, self.location.y))
    
class Transition(object):
    def __init__(self, state_1, state_2):
        self.state_1 = state_1
        self.state_2 = state_2
        if state_1.time != state_2.time - 1:
            raise ValueError("Invalid transition -", str(state_1), "to", str(state_2))
    def __eq__(self, other):
        return self.state_1 == other.state_1 and self.state_2 == other.state_2
    def __hash__(self):
        return hash(str(self.state_1)+str(self.state_2))
    def __str__(self):
        return str((self.state_1, self.state_2))
    def reverse(self):
        return Transition(State(self.state_1.time, self.state_2.location),
                          State(self.state_2.time, self.state_1.location))

class Coop_Astar():
    def __init__(self, dimension, agents, obstacles):
        self.dimension = dimension
        self.obstacles = obstacles
        self.agent_obstacles = set()
        self.end_obstacles = set()
        self.max_t = 0

        self.agents = agents
        self.agent_dict = {}
        self.curr_agent = -1

        self.make_agent_dict()

        self.a_star = AStar(self)

    def get_neighbors(self, state):
        neighbors = []

        # Wait action
        n = State(state.time + 1, state.location)
        if self.state_valid(n):
            neighbors.append(n)
        # Up action
        n = State(state.time + 1, Location(state.location.x, state.location.y+1))
        if self.state_valid(n) and self.transition_valid(state, n):
            neighbors.append(n)
        # Down action
        n = State(state.time + 1, Location(state.location.x, state.location.y-1))
        if self.state_valid(n) and self.transition_valid(state, n):
            neighbors.append(n)
        # Left action
        n = State(state.time + 1, Location(state.location.x-1, state.location.y))
        if self.state_valid(n) and self.transition_valid(state, n):
            neighbors.append(n)
        # Right action
        n = State(state.time + 1, Location(state.location.x+1, state.location.y))
        if self.state_valid(n) and self.transition_valid(state, n):
            neighbors.append(n)
        return neighbors

    def get_state(self, agent_name, solution, t):
        if t < len(solution[agent_name]):
            return solution[agent_name][t]
        else:
            return solution[agent_name][-1]

    def state_valid(self, state):
        in_bounds = state.location.x >= 0 and state.location.x < self.dimension[0] \
            and state.location.y >= 0 and state.location.y < self.dimension[1]
        end_collision = False
        for goal in self.end_obstacles:
            if goal.location == state.location and goal.time <= state.time:
                end_collision = True
        if state.location == self.agent_dict[self.curr_agent]['goal'].location:
            for t in range(state.time, self.max_t):
                if State(t, state.location) in self.agent_obstacles:
                    end_collision = True
        return in_bounds \
            and (state.location.x, state.location.y) not in self.obstacles \
            and State(state.time, Location(state.location.x, state.location.y)) not in self.agent_obstacles \
            and not end_collision

    def transition_valid(self, state_1, state_2):
        return Transition(state_1, state_2).reverse() not in self.agent_obstacles

    def admissible_heuristic(self, state, agent_name):
        goal = self.agent_dict[agent_name]["goal"]
        return fabs(state.location.x - goal.location.x) + fabs(state.location.y - goal.location.y)

    def is_at_goal(self, state, agent_name):
        goal_state = self.agent_dict[agent_name]["goal"]
        return state.is_equal_except_time(goal_state)

    def make_agent_dict(self):
        for agent in self.agents:
            start_state = State(0, Location(agent['start'][0], agent['start'][1]))
            goal_state = State(0, Location(agent['goal'][0], agent['goal'][1]))

            self.agent_dict.update({agent['name']:{'start':start_state, 'goal':goal_state}})

    def compute_solution(self):
        solution = {}
        for agent in self.agent_dict.keys():
            self.curr_agent = agent
            local_solution = self.a_star.search(agent)
            if not local_solution:
                return False
            solution.update({agent:local_solution})
            for i, state in enumerate(local_solution):
                self.agent_obstacles.add(state)
                if i > 0:
                    self.agent_obstacles.add(Transition(local_solution[i-1], state))
            self.end_obstacles.add(local_solution[-1])
            self.max_t = max(self.max_t, local_solution[-1].time)
        if not solution:
            return {}
        plan = {}
        for agent, path in solution.items():
            path_dict_list = [{'t':state.time, 'x':state.location.x, 'y':state.location.y} for state in path]
            plan[agent] = path_dict_list
        return plan

    def compute_solution_cost(self, solution):
        return sum([len(path) for path in solution.values()])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("param", help="input file containing map and obstacles")
    parser.add_argument("output", help="output file with the schedule")
    args = parser.parse_args()

    # Read from input file
    with open(args.param, 'r') as param_file:
        try:
            param = yaml.load(param_file, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)

    dimension = param["map"]["dimensions"]
    obstacles = param["map"]["obstacles"]
    agents = param['agents']

    ca = Coop_Astar(dimension, agents, obstacles)

    solution = ca.compute_solution()
    if not solution:
        print(" Solution not found" )
        return

    # Write to output file
    output = dict()
    output["schedule"] = solution
    output["cost"] = ca.compute_solution_cost(solution)
    with open(args.output, 'w') as output_yaml:
        yaml.safe_dump(output, output_yaml)


if __name__ == "__main__":
    main()
