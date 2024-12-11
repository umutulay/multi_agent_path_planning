import yaml

def count_agent_movements(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    movements = {}

    if 'schedule' in data:
        for agent, positions in data['schedule'].items():
            count = 0
            for i in range(1, len(positions)):
                prev = positions[i - 1]
                current = positions[i]

                # Check if position has changed
                if prev['x'] != current['x'] or prev['y'] != current['y']:
                    count += 1

            movements[agent] = count

    return movements

def total_movements(movements):
    return sum(movements.values())

# Example usage
if __name__ == "__main__":
    file_name = "output.yaml"
    movements = count_agent_movements(file_name)
    # comment out to see the number of movement counts by different agents
    # for agent, count in movements.items():
        # print(f"{agent}: {count} movements")

    total = total_movements(movements)
    print(f"Total movements of all agents: {total}")