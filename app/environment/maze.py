import numpy as np
import gymnasium as gym
from gymnasium import spaces
from app.environment.utils import get_min_steps, find_points
from collections import deque

# Movimientos posibles: izquierda, abajo, derecha, arriba
LEFT = 0
DOWN = 1
RIGHT = 2
UP = 3

# Objetos presentes en cada celda de la grilla
AGENT = -1
FLOOR = 0
WALL = 1
INITIAL_DOOR = 2
EXIT_DOOR = 3
MINE = 4

# Cantidad maxima de pasos a realizar: Cuando el agente hace 100 acciones (pasos), termina (perdiendo).
N_MAX_STEPS = 100


class Maze(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, grid, start_point=None, exit_point=None):
        super(Maze, self).__init__()

        self.grid = np.array(grid)
        self.nrow, self.ncol = np.shape(self.grid)
        self.start_point, self.exit_point = find_points(grid, start_point, exit_point)

        # Distribución inicial del estado (empieza en el 2)
        self.initial_state_distribution = (self.grid == 2).astype("float64").ravel()
        self.initial_state_distribution /= self.initial_state_distribution.sum()

        # Cantidad minima de pasos para superar el laberinto
        self.minimum_steps = len(get_min_steps(self.grid)) - 1

        # Definir espacio de acción: 4 posibles movimientos (abajo, derecha, arriba, izquierda)
        self.action_space = spaces.Discrete(4)
        # Definir espacio de observación: posición actual en el laberinto
        # La observación será la coordenada (fila, columna), representada como una tupla
        # low = Limites inferiores de posiciones
        # high = Limites superiores de posiciones
        # dtype = El tipo que pertenece a las observaciones
        self.observation_space = spaces.Box(
            low=np.array([0, 0, -np.inf]),  # Limites mínimos para las tres dimensiones
            high=np.array([self.size() - 1, self.size() - 1, np.inf]),  # Limites máximos para las tres dimensiones
            dtype=np.int32
        )

        # Estado inicial
        self.current_state = self.start_point
        self.reward = 0
        self.total_steps_performed = 0
        self.prev_actions = deque(maxlen=N_MAX_STEPS)

    def size(self):
        return self.nrow if self.nrow == self.ncol else np.shape(self.grid)

    def reset(self, seed=None):
        if seed is not None:
            np.random.seed(seed)
        self.current_state = self.start_point
        self.total_steps_performed = 0
        self.reward = 0
        self.prev_actions = deque(maxlen=N_MAX_STEPS)
        for _ in range(N_MAX_STEPS):
            self.prev_actions.append(-1)
        # Observacion1: estado actual, de tipo int32 los dos elementos de la tupla
        obs1 = np.array(self.current_state)
        # Observacion2: cantidad minima de pasos del Maze, de tipo int32
        obs2 = np.array([self.minimum_steps - self.total_steps_performed])
        # Devolver la observacion: estado actual y cantidad minima de pasos del Maze
        total_obs = np.concatenate([obs1, obs2])
        return np.array(total_obs, dtype=np.int32), {}

    def step(self, action):
        self.total_steps_performed += 1
        row, col = self.current_state
        new_state, self.reward, done = self.update_state_and_reward(row, col, action)
        self.current_state = new_state
        self.prev_actions.append(action)
        # truncation=False as the time limit is handled by the `TimeLimit` wrapper added during `make`
        obs1 = np.array(self.current_state)
        obs2 = np.array([self.minimum_steps - self.total_steps_performed])
        total_obs = np.concatenate([obs1, obs2])
        return np.array(total_obs, dtype=np.int32), self.reward, done, False, {}

    def update_state_and_reward(self, row, col, action):
        new_row, new_col = self.increment_position(row, col, action)
        new_state = (new_row, new_col)
        if 5 < self.total_steps_performed + 1 - self.minimum_steps:
            self.reward -= 15
        if 0 <= new_row < self.size() and 0 <= new_col < self.size():
            # esta en los limites bien
            # reviso en new_cell_value sobre que cosa esta parado
            new_cell_value = self.grid[new_row, new_col]
            if new_cell_value == WALL:
                # si esta sobre una pared no me muevo de donde empece
                new_state = (row, col)
                self.reward -= 15
            if new_cell_value== MINE:
                # si esta sobre una mina no me muevo de donde empece
                # opcional, total aca ya pierde y termina
                new_state = (row, col)
                self.reward -= 25
            if (new_cell_value == EXIT_DOOR):
                self.reward += 10000
            if (new_cell_value == FLOOR):
                self.reward += 1
        else:
            # se salio de los limites de la grilla
            new_cell_value = -1
            self.reward -= 25
            new_state = (row, col)
        done = new_cell_value in [MINE, EXIT_DOOR]

        return new_state, self.reward, done

    def increment_position(self, row, col, action):
        row_new, col_new = row, col
        if action == DOWN:  # Abajo
            row_new += 1
        elif action == RIGHT:  # Derecha
            col_new += 1
        elif action == UP:  # Arriba
            row_new -= 1
        elif action == LEFT:  # Izquierda
            col_new -= 1
        else:
            raise ValueError(f"Acción inválida: {action}")

        # Si la nueva posición se sale de los límites, no permitir el movimiento
        if row_new < 0 or row_new >= self.size() or col_new < 0 or col_new >= self.size():
            return (row, col)  # Mantener la posición actual
        if self.grid[row_new, col_new] == WALL:
            return (row, col)  # Mantener la posición actual
        return (row_new, col_new)

    def get_current_map_state(self):
        maze_render = np.copy(self.grid)
        row, col = self.current_state
        maze_render[row, col] = AGENT  # Representación del agente
        return maze_render.flatten().tolist()  # Convertir el estado a 1D

    def close(self):
        pass
