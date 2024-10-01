import heapq

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils import seeding
from enum import IntEnum


class Action(IntEnum):
    """
    Enum que representa las posibles acciones que el agente puede realizar en el laberinto.

    Las acciones incluyen:
        DOWN: Moverse hacia abajo.
        RIGHT: Moverse hacia la derecha.
        UP: Moverse hacia arriba.
        LEFT: Moverse hacia la izquierda.
    """

    DOWN = 0
    RIGHT = 1
    UP = 2
    LEFT = 3


def generate_random_map(size=8, p=0.8, seed=None):
    """
    Genera un mapa aleatorio para el laberinto.

    Parámetros:
        size (int): El tamaño del laberinto (número de filas y columnas). Por defecto es 8.
        p (float): Probabilidad de que una celda sea un espacio libre (0) frente a una pared (1). Por defecto es 0.8.
        seed (int): Semilla para la generación aleatoria. Si se proporciona, se usa para reproducibilidad.

    Devuelve:
        numpy.ndarray: Un arreglo 2D que representa el laberinto generado.
    """
    valid = False
    board = []

    np_random, _ = seeding.np_random(seed)

    while not valid:
        p = min(1, p)
        board = np_random.choice([0, 1], (size, size), p=[p, 1 - p])
        board[0][0] = 2
        board[-1][-1] = 3
        start_point = (0, 0)
        exit_point = (size - 1, size - 1)
        valid = Maze(board, size, start_point, exit_point).is_winneable()
    return board


class Maze(gym.Env):
    """
    Clase que representa un laberinto, heredando de `gym.Env`.

    Atributos:
        grid (numpy.ndarray): La cuadrícula del laberinto, donde 0 representa un espacio libre,
                              1 representa una pared, 2 es el punto de inicio y 3 es la salida.
        size (tuple): Tamaño del laberinto (número de filas y columnas).
        start_point (tuple): Coordenadas del punto de inicio en el laberinto.
        exit_point (tuple): Coordenadas del punto de salida en el laberinto.
        action_space (gym.spaces.Discrete): Espacio de acciones, representando 4 posibles movimientos.
        observation_space (gym.spaces.Box): Espacio de observación, representando la posición actual en el laberinto.
        state (tuple): Estado actual del agente en el laberinto.
        visitadas (set): Conjunto de celdas visitadas durante la exploración.

    Métodos:
        reset: Reinicia el entorno y devuelve el estado inicial.
        step: Realiza una acción y devuelve el nuevo estado, la recompensa, si el episodio ha terminado y más información.
        render: Visualiza el estado actual del laberinto.
        close: Cierra el entorno y realiza limpieza.
        is_winneable: Verifica si el laberinto es resolvible.
        get_current_map_state: Devuelve el estado actual del laberinto como una lista 1D.

    Métodos Privados:
        _find_points: Busca los puntos de inicio y salida en la cuadrícula.
        _get_min_reward: Calcula el camino mínimo desde el inicio hasta la salida usando el algoritmo A*.
        _heuristica: Calcula la distancia de Manhattan entre dos puntos.
        _normalize: Normaliza un valor entre 0 y 1.
    """

    def __init__(self, grid, size=None, start_point=None, exit_point=None):
        """
        Inicializa el entorno del laberinto.

        Parámetros:
            grid (numpy.ndarray): La cuadrícula del laberinto, donde 0 representa un espacio libre,
                                  1 representa una pared, 2 es el punto de inicio y 3 es la salida.
            size (tuple | None): Tamaño del laberinto (número de filas y columnas). Si es None, se usa el tamaño de la cuadrícula.
            start_point (tuple | None): Coordenadas del punto de inicio. Si es None, se busca en la cuadrícula.
            exit_point (tuple | None): Coordenadas del punto de salida. Si es None, se busca en la cuadrícula.
        """
        super(Maze, self).__init__()

        self.grid = np.array(grid)
        if isinstance(size, int):
            self.size = size
        else:
            self.size = np.shape(self.grid)

        start_point_present = start_point is None
        exit_point_present = exit_point is None
        if start_point_present:
            self.start_point = start_point
        if exit_point_present:
            self.exit_point = exit_point

        if start_point is None or exit_point is None:
            self.start_point, self.exit_point = self._find_points(
                grid, start_point, exit_point
            )
        else:
            self.start_point = start_point
            self.exit_point = exit_point

        # Definir espacio de acción: 4 posibles movimientos (abajo, derecha, arriba, izquierda)
        self.action_space = spaces.Discrete(4)

        # Reward minima para pasar el maze
        if not isinstance(self.size, int):
            self.minimum_reward = min(self.size)
        self.minimum_reward = len(self._get_min_reward()) - 1
        self.maximum_reward = self.size * self.size

        # Definir espacio de observación: posición actual en el laberinto
        # La observación será la coordenada (fila, columna), representada como una tupla
        # low = Limites inferiores de posiciones
        # high = Limites superiores de posiciones
        # dtype = El tipo que pertenece a las observaciones
        self.observation_space = spaces.Box(
            low=np.array([0, 0]),
            high=np.array([self.size - 1, self.size - 1]),
            dtype=np.int32,
        )

        # Estado inicial
        self.state = self.start_point

        self.visitadas = set()
        self.visitadas.add(self.start_point)  # Agregar la celda inicial como visitada

    def _find_points(self, grid, start_point, exit_point):
        """
        Método privado para buscar los puntos en la grilla.

        Además asegura que el start_point y el exit_point sean tuplas.

        Parámetros:
            grid (numpy.ndarray): La grilla del laberinto.
            start_point (tuple | None): Tupla con la posición de inicio o None.
            exit_point (tuple | None): Tupla con la posición de salida o None.

        Devuelve:
            tuple: Tuplas que representan el punto de inicio y el punto de salida.
        """
        found_start = found_exit = False
        if isinstance(self.size, int):
            size = (self.size, self.size)
        cant_rows, cant_cols = size

        for row in range(cant_rows):
            for col in range(cant_cols):
                if grid[row][col] == 2 and start_point is None:
                    start_point = (row, col)
                    found_start = True
                if grid[row][col] == 3 and exit_point is None:
                    exit_point = (row, col)
                    found_exit = True
                if found_start and found_exit:
                    break

        return start_point, exit_point

    def _get_min_reward(self):
        """
        Método privado que implementa el algoritmo A* para encontrar el camino mínimo.

        Busca la cantidad mínima de pasos para recorrer el laberinto, evitando paredes.

        Devuelve:
            list: Un arreglo que contiene el camino más corto desde el punto de inicio al punto de salida.
        """
        filas = len(self.grid)
        columnas = len(self.grid[0])

        # Lista abierta (nodos por explorar) y cerrada (nodos explorados)
        lista_abierta = []
        # Agregar el nodo inicial a la lista abierta
        heapq.heappush(lista_abierta, (0, self.start_point))
        lista_cerrada = set()

        # Diccionarios para almacenar costos y padres (para reconstruir el camino)
        g_score = {self.start_point: 0}  # Costo desde el inicio hasta cada nodo
        padres = {self.start_point: 0}  # Para reconstruir el camino

        while lista_abierta:
            # Obtener el nodo con el menor costo estimado (f_score)
            _, actual = heapq.heappop(lista_abierta)

            # Si llegamos al destino, reconstruimos el camino
            if actual == self.exit_point:
                camino = []
                while actual:
                    camino.append(actual)
                    actual = padres[actual]
                return camino[::-1]  # Retornar el camino del inicio al fin

            lista_cerrada.add(actual)

            # Movimientos posibles: arriba, abajo, izquierda, derecha
            vecinos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for mov in vecinos:
                vecino = (actual[0] + mov[0], actual[1] + mov[1])

                # Verificar que el vecino está dentro de los límites de la matriz
                if 0 <= vecino[0] < filas and 0 <= vecino[1] < columnas:
                    # Verificar si el vecino es transitable (celdas con valor 0) y no es una pared
                    if self.grid[vecino[0]][vecino[1]] == 1 or vecino in lista_cerrada:
                        continue  # Si es una pared (1) o ya fue evaluado, lo saltamos

                    # Calcular g_score para el vecino (costo desde el inicio)
                    g_score_vecino = (
                        g_score[actual] + 1
                    )  # Cada movimiento tiene un costo de 1

                    # Si no hemos visto este vecino o encontramos un mejor camino
                    if vecino not in g_score or g_score_vecino < g_score[vecino]:
                        g_score[vecino] = g_score_vecino
                        f_score = g_score_vecino + self._heuristica(
                            vecino, self.exit_point
                        )  # f_score = g_score + heurística
                        heapq.heappush(lista_abierta, (f_score, vecino))
                        padres[vecino] = actual  # Guardamos el rastro del camino

        # Si no hay camino...
        # Pero si el mapa fue validado antes y pasa el metodo is_winneable,
        # no deberia devolver nunca None
        return None

    def _heuristica(self, a, b):
        """
        Función heurística que calcula la distancia de Manhattan.

        Método privado para el algoritmo A*.

        Parámetros:
            a (tuple): Coordenada de un nodo.
            b (tuple): Coordenada de otro nodo.

        Devuelve:
            int: La distancia de Manhattan entre los nodos a y b.
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


    def reset(self, start_point=None, seed=None):
        """
        Reinicia el entorno y devuelve el estado inicial.

        Parámetros:
            start_point (tuple | None): Coordenadas iniciales o None para usar el valor por defecto.
            seed (int | None): Semilla para la aleatoriedad. Si se proporciona, se usa para reiniciar.

        Devuelve:
            numpy.ndarray: El estado inicial del entorno.
        """
        if seed is not None:
            np.random.seed(seed)
        self.state = start_point if start_point is not None else self.start_point
        self.visitadas = {self.state}  # Reiniciar las celdas visitadas
        return np.array(self.state, dtype=np.int32)  # Devolver la observación inicial

    def step(self, action):
        """
        Realiza una acción en el entorno y devuelve el nuevo estado, la recompensa, si el episodio ha terminado y más información.

        Parámetros:
            action (Action): La acción a realizar.

        Devuelve:
            tuple: Estado actual (numpy.ndarray), recompensa (float), booleano que indica si el episodio ha terminado,
                   booleano que indica si fue truncado, y un diccionario de información adicional.
        """
        row, col = self.state
        row_new, col_new = row, col
        # Definir los movimientos basados en la acción (abajo, derecha, arriba, izquierda)
        if action == Action.DOWN:  # Abajo
            row_new = row + 1
        elif action == Action.RIGHT:  # Derecha
            col_new = col + 1
        elif action == Action.UP:  # Arriba
            row_new = row - 1
        elif action == Action.LEFT:  # Izquierda
            col_new = col - 1
        else:
            raise ValueError(f"Acción inválida: {action}")

        reward = -1

        # Verificar si las nuevas coordenadas están dentro de los límites
        if 0 <= row_new < self.size and 0 <= col_new < self.size:
            # El paso que dio fue ganador: corto directamente
            if self.grid[row_new][col_new] == 3:
                self.state = (row_new, col_new)
                return (
                    np.array(self.state, dtype=np.int32),
                    reward,
                    True,
                    False,
                    {},
                )
            # Verificar si la nueva celda es una pared
            if self.grid[row_new][col_new] != 1:
                # Actualizar el estado con las nuevas coordenadas
                self.state = (row_new, col_new)
                # Si el agente llega a una celda ya visitada, penalizar más
                if self.state in self.visitadas:
                    reward -= 35
                else:
                    self.visitadas.add(self.state)  # Marcar la nueva celda como visitada
                    reward -= 20
            else:
                reward -= 50
        else:
            # El paso se salio de la matriz
            reward -= 60

        

        done = False
        truncated = False
        info = {}
        # Devolver estado actual, reward y si el episodio terminó
        return (
            np.array(self.state, dtype=np.int32),
            reward,
            done,
            truncated,
            info,
        )

    def render(self, mode="human"):
        """
        Visualiza el estado actual del laberinto.

        Parámetros:
            mode (str): El modo de visualización para gym.Env, pero nosotros no lo usamos.
        """
        maze_render = np.copy(self.grid)

        # Marcar la posición actual
        row, col = self.state
        maze_render[row, col] = -1  # Por ejemplo, marcar con un 2 donde está el agente

        print(maze_render)

    def close(self):
        """
        Cierra el entorno y realiza cualquier limpieza necesaria.
        """
        pass

    def is_winneable(self):
        """
        Verifica si el laberinto es resolvible utilizando una búsqueda en profundidad.

        Un laberinto es resolvible si hay un camino disponible del punto de inicio y el punto de fin.

        Devuelve:
            bool: Verdadero si el laberinto es resolvible, falso en caso contrario.
        """
        # Pila del DFS para el camino por recorrer (empezamos desde el punto de inicio)
        # Asegúrate de que start_point sea una tupla, por ejemplo (0, 0)
        camino = [self.start_point]

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
                    if (
                        self.grid[row_new][col_new] != 1
                        and (row_new, col_new) not in visitados
                    ):
                        # Añadir la nueva celda al camino por recorrer
                        camino.append((row_new, col_new))

        # Si salimos del bucle sin encontrar la salida, el laberinto no es resolvible
        return False

    def get_current_map_state(self):
        """
        Devuelve el estado actual del laberinto como una lista unidimensional.

        Devuelve:
            list: Una lista 1D que representa el estado actual del laberinto.
        """
        maze_render = np.copy(self.grid)
        row, col = self.state
        maze_render[row, col] = -1  # Representación del agente
        return maze_render.flatten().tolist()  # Convertir el estado a 1D
