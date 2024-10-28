import numpy as np
import gymnasium as gym
from gymnasium import spaces
from app.environment.utils import get_min_steps, find_points, increment_position

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
        self.max_path_length = 2048
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
            low=np.array([0, 0, -np.inf, 0, 0, 0, 0, 0, 0, 0, 0] + [0, 0] * self.max_path_length),  # Mínimos
            high=np.array([self.nrow - 1, self.ncol - 1, np.inf, 4, 4, 4, 4, 4, 4, 4, 4] + [self.size()-1, self.size()-1] * self.max_path_length),  # Máximos
            dtype=np.float32,
        )

        # Estado inicial
        self.current_state = self.start_point
        self.total_steps_performed = 0
        self.reward = 0
        self.done = False
        self.path = []

    def size(self):
        return self.nrow if self.nrow == self.ncol else np.shape(self.grid)

    def reset(self, seed=None):
        if seed is not None:
            np.random.seed(seed)
        self.current_state = self.start_point
        self.total_steps_performed = 0
        self.reward = 0
        self.done = False
        self.path = []
        # Observacion1: estado actual, de tipo int32 los dos elementos de la tupla
        obs1 = np.array(self.current_state)
        # Observacion2: cantidad minima de pasos del Maze, de tipo int32
        obs2 = np.array([self.minimum_steps - self.total_steps_performed])

        x_pos, y_pos = self.current_state
        top_pos = 1 if x_pos == 0 else self.grid[x_pos - 1, y_pos]
        bottom_pos = 1 if x_pos == self.size() - 1 else self.grid[x_pos + 1, y_pos]
        left_pos = 1 if y_pos == 0 else self.grid[x_pos, y_pos - 1]
        right_pos = 1 if y_pos == self.size() - 1 else self.grid[x_pos, y_pos + 1]
        
        # Observacion1: estado actual, de tipo int32 los dos elementos de la tupla
        obs1 = np.array(self.current_state)
        # Observacion2: cantidad minima de pasos del Maze, de tipo int32
        obs2 = np.array([self.minimum_steps - self.total_steps_performed])

        x_pos, y_pos = self.current_state
        top_pos = 1 if x_pos == 0 else self.grid[x_pos - 1, y_pos]
        bottom_pos = 1 if x_pos == self.size() - 1 else self.grid[x_pos + 1, y_pos]
        left_pos = 1 if y_pos == 0 else self.grid[x_pos, y_pos - 1]
        right_pos = 1 if y_pos == self.size() - 1 else self.grid[x_pos, y_pos + 1]
        if x_pos == 0:
            top_left_pos = 1     
        elif y_pos == 0:
            top_left_pos = 1
        else:
            top_left_pos = self.grid[x_pos + 1, y_pos - 1]
        if x_pos == 0:
            top_right_pos = 1     
        elif y_pos == self.size() - 1:
            top_right_pos = 1
        else:
            top_right_pos = self.grid[x_pos + 1, y_pos + 1]
        if x_pos == self.size() - 1:
            bottom_rigth_pos = 1  
        elif y_pos == self.size() - 1:
            bottom_rigth_pos = 1
        else:
            bottom_rigth_pos = self.grid[x_pos - 1, y_pos + 1]
        if y_pos == 0:
            bottom_left_pos = 1     
        elif x_pos == self.size() - 1:
            bottom_left_pos = 1
        else:
            bottom_left_pos = self.grid[x_pos - 1, y_pos - 1]
        # Observacion3: lo que hay a la izquierda del agente
        obs3 = np.array([left_pos])
        # Observacion4: lo que hay a la derecha del agente
        obs4 = np.array([right_pos])
        # Observacion5: lo que hay arriba del agente
        obs5 = np.array([top_pos])
        # Observacion6: lo que hay abajo del agente
        obs6 = np.array([bottom_pos])
        # Observacion7: lo que hay abajo y a la derecha del agente
        obs7 = np.array([bottom_rigth_pos])
        # Observacion8: lo que hay abajo y a la iquierda del agente
        obs8 = np.array([bottom_left_pos])
        # Observacion9: lo que hay arriba y a la derecha del agente
        obs9 = np.array([top_right_pos])
        # Observacion10: lo que hay arriba y a la izquierda del agente
        obs10 = np.array([top_left_pos])

        # Devolver la observacion: estado actual y cantidad minima de pasos del Maze
        visitados_array = np.array(self.path, dtype=np.int32).flatten() 
        visitados_array = np.pad(visitados_array, (0, (self.max_path_length * 2) - len(visitados_array)), 'constant')
        total_obs = np.concatenate([obs1, obs2, obs3, obs4, obs5, obs6, obs7, obs8, obs9, obs10, visitados_array])
        
        return np.array(total_obs, dtype=np.int32), {}

    def step(self, action):
        self.total_steps_performed += 1
        row, col = self.current_state
        if  not (len(self.path) > self.max_path_length - 1):
            new_state = self.update_state_and_reward(row, col, action)
            self.current_state = new_state
            self.path.append(new_state)
        else:
            self.done = True
                # new_state = self._update_state_and_reward(row, col, action)
                # self.current_state = new_state
        # truncation=False as the time limit is handled by the `TimeLimit` wrapper added during `make`
        
        obs1 = np.array(self.current_state)
        obs2 = np.array([self.minimum_steps - self.total_steps_performed])
        x_pos, y_pos = self.current_state
        top_pos = 1 if x_pos == 0 else self.grid[x_pos - 1, y_pos]
        bottom_pos = 1 if x_pos == self.size() - 1 else self.grid[x_pos + 1, y_pos]
        left_pos = 1 if y_pos == 0 else self.grid[x_pos, y_pos - 1]
        right_pos = 1 if y_pos == self.size() - 1 else self.grid[x_pos, y_pos + 1]
        if x_pos == 0:
            top_left_pos = 1     
        elif y_pos == 0:
            top_left_pos = 1
        else:
            top_left_pos = self.grid[x_pos - 1, y_pos - 1]
        if x_pos == 0:
            top_right_pos = 1     
        elif y_pos == self.size() - 1:
            top_right_pos = 1
        else:
            top_right_pos = self.grid[x_pos - 1, y_pos + 1]
        if x_pos == self.size() - 1:
            bottom_rigth_pos = 1  
        elif y_pos == self.size() - 1:
            bottom_rigth_pos = 1
        else:
            bottom_rigth_pos = self.grid[x_pos + 1, y_pos + 1]
        if y_pos == 0:
            bottom_left_pos = 1     
        elif x_pos == self.size() - 1:
            bottom_left_pos = 1
        else:
            bottom_left_pos = self.grid[x_pos + 1, y_pos - 1]
        # Observacion3: lo que hay a la izquierda del agente
        obs3 = np.array([left_pos])
        # Observacion4: lo que hay a la derecha del agente
        obs4 = np.array([right_pos])
        # Observacion5: lo que hay arriba del agente
        obs5 = np.array([top_pos])
        # Observacion6: lo que hay abajo del agente
        obs6 = np.array([bottom_pos])
        # Observacion7: lo que hay abajo y a la derecha del agente
        obs7 = np.array([bottom_rigth_pos])
        # Observacion8: lo que hay abajo y a la iquierda del agente
        obs8 = np.array([bottom_left_pos])
        # Observacion9: lo que hay arriba y a la derecha del agente
        obs9 = np.array([top_right_pos])
        # Observacion10: lo que hay arriba y a la izquierda del agente
        obs10 = np.array([top_left_pos])

        # Devolver la observacion: estado actual y cantidad minima de pasos del Maze
        visitados_array = np.array(self.path, dtype=np.int32).flatten() 
        visitados_array = np.pad(visitados_array, (0, (self.max_path_length * 2) - len(visitados_array)), 'constant')
        total_obs = np.concatenate([obs1, obs2, obs3, obs4, obs5, obs6, obs7, obs8, obs9, obs10, visitados_array])
        
        return np.array(total_obs, dtype=np.int32), self.reward, self.done, False, {}

    def update_state_and_reward(self, row, col, action):
        new_row, new_col = increment_position(self.grid, row, col, action)
        new_state = (new_row, new_col)

        new_cell_value = self.grid[new_row, new_col]

        if new_cell_value == WALL:
            self.reward -= 400
            # print("step sobre la pared")
        if new_cell_value == MINE:
            self.reward -= 25
        if new_cell_value == EXIT_DOOR:
            self.reward = 1
            # print("step sobre la exit door")
        if new_cell_value == FLOOR:
            self.reward -= 10
            # print("step sobre floor")
        if new_state in self.path:
            self.reward -= 100000

        self.done = new_cell_value in [MINE, EXIT_DOOR]
        self.reward = self.minimum_steps - self.total_steps_performed

        return new_state

    def get_current_map_state(self):
        maze_render = np.copy(self.grid)
        row, col = self.current_state
        maze_render[row, col] = AGENT  # Representación del agente
        return maze_render.flatten().tolist()  # Convertir el estado a 1D
