from vector import Vector2
from queue import PriorityQueue


LOG_FILE = 'game.log'
def log(*args, sep=' ', end='\n'):
    with open(LOG_FILE, 'a') as f:
        f.write(sep.join([str(a) for a in args]) + end)


def only_alnum(string: str):
    return ''.join([i for i in string if i.isalnum()])


def get_path(start_pos: Vector2, target_pos: Vector2, is_traversable_func,
             move_dirs = [(0, 1), (0, -1), (2, 0), (-2, 0)]):
    # Define a helper function to calculate the heuristic distance between two points
    def heuristic_distance(pos1, pos2):
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    # Define a class to represent a node in the search graph
    class Node:
        def __init__(self, position, g_score=float('inf'), f_score=float('inf'), parent=None):
            self.position = position
            self.g_score = g_score
            self.f_score = f_score
            self.parent = parent

        def __lt__(self, other):
            return self.f_score < other.f_score

    # Initialize the open and closed sets
    open_set = PriorityQueue()
    closed_set = set()

    # Create the start and target nodes
    start_node = Node(start_pos, g_score=0, f_score=heuristic_distance(start_pos, target_pos))
    target_node = Node(target_pos)

    # Add the start node to the open set
    open_set.put(start_node)

    # Start the A* search
    while not open_set.empty():
        # Get the node with the lowest f_score from the open set
        current_node = open_set.get()

        # Check if the current node is the target node
        if current_node.position == target_node.position:
            # Reconstruct the path from the target node to the start node
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            path.reverse()
            return path

        # Add the current node to the closed set
        closed_set.add(current_node.position)

        # Generate the neighboring nodes
        neighbors = []
        for dx, dy in move_dirs:
            neighbor_pos = Vector2(current_node.position.x + dx, current_node.position.y + dy)
            if is_traversable_func(*neighbor_pos) and neighbor_pos not in closed_set:
                neighbors.append(neighbor_pos)

        # Process the neighboring nodes
        for neighbor_pos in neighbors:
            # Calculate the tentative g_score for the neighbor node
            tentative_g_score = current_node.g_score + 1

            # Check if the neighbor node is already in the open set
            neighbor_node = None
            for node in open_set.queue:
                if node.position == neighbor_pos:
                    neighbor_node = node
                    break

            if neighbor_node is None:
                # Create a new neighbor node
                neighbor_node = Node(neighbor_pos)

            if tentative_g_score < neighbor_node.g_score:
                # Update the neighbor node's g_score, f_score, and parent
                neighbor_node.g_score = tentative_g_score
                neighbor_node.f_score = tentative_g_score + heuristic_distance(neighbor_pos, target_pos)
                neighbor_node.parent = current_node

                # Add the neighbor node to the open set
                open_set.put(neighbor_node)

    # If the open set is empty and the target node has not been found, return an empty path
    return -1


def get_directions(start_pos: Vector2, target_pos: Vector2, is_traversable_func):
    path = get_path(start_pos, target_pos, is_traversable_func)
    if path == -1: return -1

    directions = []
    #raise Exception(path, *start_pos, *target_pos, is_wall_func)
    current_position = Vector2(*path[0])

    for next_position in path[1:]:
        next_position = Vector2(*next_position)

        directions.append(next_position-current_position)

        current_position = next_position

    return directions


if __name__ == '__main__':
    print(*get_directions(Vector2(0, 0), Vector2(10, 10), lambda x, y: False))
