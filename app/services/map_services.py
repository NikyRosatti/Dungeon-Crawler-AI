import heapq
import json
import numpy as np
from gymnasium.utils import seeding
from app.models import MazeBd

# Possible movements: left, down, right, up
LEFT = 0
DOWN = 1
RIGHT = 2
UP = 3


def find_player_position(maze_map):
    """
    Finds the player's position in the map.

    Parameters:
        maze_map (list): A list representation of the map.

    Returns:
        int: The index of the player's position, or the position of the value 2 if -1 is not found.
    """
    try:
        return maze_map.index(-1)  # Buscar la posición del jugador (-1)
    except ValueError:
        return maze_map.index(2)  # Si no hay -1, devolver la posición de 2


def move_player(direction, maze_map, map_size):
    """
    Moves the player in the specified direction if possible.

    Parameters:
        direction (str): Direction of movement (ArrowUp, ArrowDown, ArrowLeft, ArrowRight).
        maze_map (list): A list representing the map state.
        maze_size (int): The size of the map grid.
    """
    player_pos = find_player_position(maze_map)

    if direction == "ArrowUp":
        new_pos = player_pos - map_size if player_pos >= map_size else player_pos
    elif direction == "ArrowDown":
        new_pos = (
            player_pos +
            map_size if player_pos < len(map) - map_size else player_pos
        )
    elif direction == "ArrowLeft":
        new_pos = player_pos - 1 if player_pos % map_size != 0 else player_pos
    elif direction == "ArrowRight":
        new_pos = player_pos + \
            1 if (player_pos + 1) % map_size != 0 else player_pos
    else:
        new_pos = player_pos

    if maze_map[new_pos] == 0:
        maze_map[player_pos] = 0
        maze_map[new_pos] = -1
    elif maze_map[new_pos] == 3:
        maze_map[player_pos] = 0
        maze_map[new_pos] = -2


def change_door(maze_map):
    """
    Changes the door's position in the map by replacing the value 2 with -1.

    Parameters:
        maze_map (list): The map list containing the door value 2.
    """
    if isinstance(maze_map, list) and 2 in maze_map:
        i = maze_map.index(2)
        maze_map[i] = -1
    else:
        print("Error: map no es una lista o no contiene el valor 2")


def create_grid(map_grid, size):
    """
    Converts a flat array into a 2D matrix.

    Parameters:
        map_grid (list): The flat array of the map.
        size (int): Size of the grid.

    Returns:
        list: A 2D list representation of the grid.
    """
    return [map_grid[i: i + size] for i in range(0, len(map_grid), size)]


def are_points_valid(start_point, exit_point):
    """
    Validates the existence of both start and exit points.

    Parameters:
        start_point (tuple | None): Starting position.
        exit_point (tuple | None): Exit position.

    Returns:
        bool: True if both points are valid, False otherwise.
    """
    return start_point is not None and exit_point is not None


def load_maze_from_db(maze_id):
    """
    Loads the maze from the database.

    Parameters:
        maze_id (int): ID of the maze to be loaded.

    Returns:
        tuple: A tuple containing the maze object, its grid as a list, and its size.
    """
    maze = MazeBd.query.filter_by(id=maze_id).first()
    grid1 = json.loads(maze.grid)
    size = maze.maze_size
    grid = [grid1[i: i + size] for i in range(0, len(grid1), size)]

    return maze, grid, size


def find_points(grid, start_point=None, exit_point=None):
    """
    Method to find points in the grid.

    Also ensures that start_point and exit_point are tuples.

    Parameters:
        grid (numpy.ndarray): The maze grid.
        start_point (tuple | None): Tuple with the starting position or None.
        exit_point (tuple | None): Tuple with the exit position or None.

    Returns:
        tuple: Two tuples representing the starting point and exit point, respectively.
    """

    def find_coordinates(matrix, value):
        """
        Finds the coordinates of a value in the matrix.

        Parameters:
            matrix (list): 2D list representing the maze.
            value (int): Value to search for.

        Returns:
            tuple: Coordinates (row, column) of the value if found, else None.
        """
        for i, row in enumerate(matrix):
            for j, elem in enumerate(row):
                if elem == value:
                    # Devuelve una tupla con las coordenadas (fila, columna)
                    return (i, j)
        return None

    if start_point is None:
        start_point = find_coordinates(grid, 2)
    if exit_point is None:
        exit_point = find_coordinates(grid, 3)
    return start_point, exit_point


def get_min_steps(grid, start_point=None, exit_point=None):
    """
    A* Algorithm.

    Parameters:
        grid (numpy.ndarray): The maze grid.
        start_point (tuple | None): Tuple with the starting position or None.
        exit_point (tuple | None): Tuple with the exit position or None.

    Returns:
        list: List of nodes to traverse to go from start to exit.
        None: If no path is available.
    """

    def heuristica(a, b):
        """
        Manhattan distance between two points on the grid.

        Parameters:
            a (tuple): Coordinate of the first point.
            b (tuple): Coordinate of the second point.

        Returns:
            int: Manhattan distance between `a` and `b`.
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    start_point, exit_point = find_points(grid, start_point, exit_point)
    start_point = tuple(start_point)
    exit_point = tuple(exit_point)
    filas, columnas = np.shape(grid)

    lista_abierta = []
    heapq.heappush(lista_abierta, (0, start_point))
    lista_cerrada = set()

    g_score = {start_point: 0}
    padres = {start_point: None}

    while lista_abierta:
        _, actual = heapq.heappop(lista_abierta)

        if actual == exit_point:
            camino = []
            while actual is not None:
                camino.append(actual)
                actual = padres[actual]
            return camino[::-1]

        lista_cerrada.add(actual)

        vecinos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for mov in vecinos:
            vecino = (actual[0] + mov[0], actual[1] + mov[1])

            if 0 <= vecino[0] < filas and 0 <= vecino[1] < columnas:
                if (
                    grid[vecino[0]][vecino[1]] == 1
                    or grid[vecino[0]][vecino[1]] == 4
                    or vecino in lista_cerrada
                ):
                    continue

                g_score_vecino = g_score[actual] + 1

                if vecino not in g_score or g_score_vecino < g_score[vecino]:
                    g_score[vecino] = g_score_vecino
                    f_score = g_score_vecino + heuristica(vecino, exit_point)
                    heapq.heappush(lista_abierta, (f_score, vecino))
                    padres[vecino] = actual

    return None


def is_winneable(grid):
    """
    Checks if the maze is solvable using the A* algorithm.

    A maze is solvable if there is an available path from the start point to the end point.

    Parameters:
        grid (numpy.ndarray | list): The maze grid.

    Returns:
        bool: True if the maze is solvable, False otherwise.
    """
    grid = np.array(grid)
    return get_min_steps(grid) is not None


def generate_random_map(size=8, p=0.8, seed=None):
    """
    Generates a random map for the maze.

    Parameters:
        size (int): The size of the maze (number of rows and columns). Default is 8.
        p (float): Probability that a cell is free space (0) versus a wall (1). Default is 0.8.
        seed (int): Seed for random generation. If provided, it is used for reproducibility.

    Returns:
        numpy.ndarray: A 2D array representing the generated maze.
    """
    valid = False
    board = []

    np_random, _ = seeding.np_random(seed)

    while not valid:
        p = min(1, p)
        board = np_random.choice([0, 1], (size, size), p=[p, 1 - p])
        board[0][0] = 2
        board[-1][-1] = 3
        valid = is_winneable(board)
    return board


def increment_position(current_row, current_col, action):
    """
    Moves within a grid given a row and column.

    Parameters:
        current_row (tuple): Row of the current state.
        current_col (tuple): Column of the current state.
        action (int): Movement to perform (up, down, left, right) 
        according to the corresponding integer.

    Returns:
        tuple: The new row and column after the action is performed.
        ValueError Exception if the action is not registered as valid.
    """
    row_new, col_new = current_row, current_col

    if action == DOWN:
        row_new += 1
    elif action == RIGHT:
        col_new += 1
    elif action == UP:
        row_new -= 1
    elif action == LEFT:
        col_new -= 1
    else:
        raise ValueError(f"Acción inválida: {action}")

    return (row_new, col_new)


def size(grid):
    """
    Size of a given grid.

    Parameters:
        grid (numpy.ndarray | list): The grid of the maze.

    Returns:
        (int | tuple): int if the grid size is square,
                       tuple if the grid is not square, in the form of (NRows, NCols).
    """
    grid = np.array(grid)
    nrow, ncol = np.shape(grid)
    return nrow if nrow == ncol else np.shape(grid)


def action_to_string(action):
    """
    String representation of actions for the environment. 
    Returns 'UNKNOWN' in case of an invalid action.
    """
    if action == 0:
        return "LEFT"
    if action == 1:
        return "DOWN"
    if action == 2:
        return "RIGHT"
    if action == 3:
        return "UP"
    return "UNKNOWN"


def object_to_string(obj):
    """
    String representation of environment objects. 
    Returns 'UNKNOWN_OBJ' in case of an invalid object.
    """
    if obj == -1:
        return "AGENT"
    if obj == 0:
        return "FLOOR"
    if obj == 1:
        return "WALL"
    if obj == 2:
        return "INITIAL_DOOR"
    if obj == 3:
        return "EXIT_DOOR"
    if obj == 4:
        return "MINE"
    return "UNKNOWN_OBJ"
