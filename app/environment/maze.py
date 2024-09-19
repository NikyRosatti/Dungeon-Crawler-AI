
import gymnasium as gym
from gymnasium import spaces
import numpy as np


class Maze(gym.Env):
    
    def __init__(self, grid, size, start_point, exit_point):
        super(Maze, self).__init__()
        
        self.grid = grid
        self.size = size
        self.start_point = start_point
        self.exit_point = exit_point

        # Definir espacio de acción: 4 posibles movimientos (abajo, derecha, arriba, izquierda)
        self.action_space = spaces.Discrete(4)

        # Definir espacio de observación: posición actual en el laberinto
        # La observación será la coordenada (fila, columna), representada como una tupla
        # (puedes adaptar si quieres más información)
        self.observation_space = spaces.Box(
            low=np.array([0, 0]), 
            high=np.array([self.size - 1, self.size - 1]), 
            dtype=np.int32
        )

        # Estado inicial
        self.state = self.start_point
        
        self.visitadas = set()
        self.visitadas.add(self.start_point)  # Agregar la celda inicial como visitada


    def reset(self, start_point = None, seed = None):
        """Reinicia el entorno y devuelve el estado inicial"""
        if seed is not None:
            np.random.seed(seed)
        self.state = start_point if start_point is not None else self.start_point
        self.visitadas = {self.state}  # Reiniciar las celdas visitadas
        return np.array(self.state, dtype=np.int32)  # Devolver la observación inicial
    
    
    def step(self, action):
        """Realiza una acción en el entorno y devuelve el nuevo estado, recompensa, done y info"""
        row, col = self.state

        # Definir los movimientos basados en la acción (abajo, derecha, arriba, izquierda)
        if action == 0:  # Abajo
            row_new, col_new = row + 1, col
        elif action == 1:  # Derecha
            row_new, col_new = row, col + 1
        elif action == 2:  # Arriba
            row_new, col_new = row - 1, col
        elif action == 3:  # Izquierda
            row_new, col_new = row, col - 1
        else:
            raise ValueError(f"Acción inválida: {action}")

        recompensa = -1

        # Verificar si las nuevas coordenadas están dentro de los límites
        if 0 <= row_new < self.size and 0 <= col_new < self.size:
            # Verificar si la nueva celda es una pared
            if self.grid[row_new][col_new] != 1:
                # Actualizar el estado con las nuevas coordenadas
                self.state = (row_new, col_new)
            else:
                recompensa = -5
        else:
            recompensa = -5


        # Si el agente llega a una celda ya visitada, penalizar más
        if self.state in self.visitadas:
            recompensa = -10  # Penalización adicional por visitar una celda repetida
        else:
            self.visitadas.add(self.state)  # Marcar la nueva celda como visitada

        # Recompensa por llegar al punto de salida
        if self.state == self.exit_point:
            recompensa = 100
            done = True
        else:
            done = False

        truncated = False
        info = {}
        # Devolver estado actual, recompensa, si el episodio terminó y info adicional
        return np.array(self.state, dtype=np.int32), recompensa, done, truncated, info

    
    def render(self, mode='human'):
        """Visualiza el estado actual del laberinto"""
        maze_render = np.copy(self.grid)

        # Marcar la posición actual
        row, col = self.state
        maze_render[row, col] = -1  # Por ejemplo, marcar con un 2 donde está el agente

        print(maze_render)
    
    def close(self):
        """Cierra el entorno (limpieza)"""
        pass
        
    def is_winneable(self):
        # Pila del DFS para el camino por recorrer (empezamos desde el punto de inicio)
        camino = [self.start_point]  # Asegúrate de que start_point sea una tupla, por ejemplo (0, 0)
        
        # Set para almacenar las celdas visitadas
        visitados = set()

        # Mientras haya celdas en el camino por recorrer
        while camino:
            # Sacamos la celda actual del camino (DFS usa pop)
            current = camino.pop()

            # Verificar que current es una tupla
            if not isinstance(current, tuple):
                raise ValueError(f"Expected tuple, got {type(current)}: {current}")

            row, col = current  # Desempaquetar las coordenadas de la celda

            # Si esta celda ya ha sido visitada, la saltamos
            if (row, col) in visitados:
                continue
            
            # Marcar la celda como visitada
            visitados.add((row, col))

            # Si estamos en la celda de salida, significa que el laberinto es resolvible
            if (row, col) == self.exit_point:
                return True

            # Direcciones posibles (abajo, derecha, arriba, izquierda)
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

            # Explorar las direcciones
            for x, y in directions:
                # Nuevas coordenadas basadas en la dirección
                row_new = row + x
                col_new = col + y

                # Verificar que las nuevas coordenadas estén dentro de los límites del laberinto
                if 0 <= row_new < self.size and 0 <= col_new < self.size:
                    # Si la nueva celda no es una pared (asumiendo 1 = pared) y no ha sido visitada
                    if self.grid[row_new][col_new] != 1 and (row_new, col_new) not in visitados:
                        # Añadir la nueva celda al camino por recorrer
                        camino.append((row_new, col_new))

        # Si salimos del bucle sin encontrar la salida, el laberinto no es resolvible
        return False
    
    def get_current_map_state(self):
        """Devuelve el estado actual del laberinto como una lista 1D."""
        maze_render = np.copy(self.grid)
        row, col = self.state
        maze_render[row, col] = -1  # Representación del agente
        return maze_render.flatten().tolist()  # Convertir el estado a 1D
