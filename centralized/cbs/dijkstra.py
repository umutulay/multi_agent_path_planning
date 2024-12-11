class Dijkstra:
    def __init__(self, environment):
        self.environment = environment

    def search(self, agent_name):
        start_state = self.environment.agent_dict[agent_name]['start']
        goal_state = self.environment.agent_dict[agent_name]['goal']

        open_set = {start_state}
        came_from = {}
        cost_so_far = {start_state: 0}  # Tracks the cost to reach each state

        while open_set:
            # Get the state with the smallest cost so far
            current = min(open_set, key=lambda state: cost_so_far.get(state, float('inf')))

            # If the goal is reached, reconstruct the path
            if self.environment.is_at_goal(current, agent_name):
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)

            # Explore neighbors
            for neighbor in self.environment.get_neighbors(current):
                new_cost = cost_so_far[current] + 1  # Assuming uniform cost
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current
                    open_set.add(neighbor)

        return None  # No path found

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        total_path.reverse()
        return total_path
