import heapq
import numpy as np
from gymnasium.utils import seeding


def find_points(grid, start_point=None, exit_point=None):
    """
    Método privado para buscar los puntos en la grilla.

    Además asegura que el start_point y el exit_point sean tuplas.

    Parámetros:
        grid (numpy.ndarray): La grilla del laberinto.
        start_point (tuple | None): Tupla con la posición de inicio o None.
        exit_point (tuple | None): Tupla con la posición de salida o None.

    Devuelve:
        tuple: Dos tuplas que representan el punto de inicio y el punto de salida respectivamente.
    """

    def find_coordinates(matrix, value):
        """
        Dada una matriz y un valor, devuelve la posicion de ese valor en la matriz
        """
        for i, row in enumerate(matrix):
            for j, elem in enumerate(row):
                if elem == value:
                    return (
                        i,
                        j,
                    )  # Devuelve una tupla con las coordenadas (fila, columna)
        return None

    if start_point is None:
        start_point = find_coordinates(grid, 2)
    if exit_point is None:
        exit_point = find_coordinates(grid, 3)
    return start_point, exit_point


def get_min_steps(grid, start_point=None, exit_point=None):
    def heuristica(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    start_point, exit_point = find_points(grid, start_point, exit_point)
    start_point = tuple(start_point)  # Convertir a tupla
    exit_point = tuple(exit_point)  # Convertir a tupla
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
                if grid[vecino[0]][vecino[1]] == 1 or vecino in lista_cerrada:
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
    Verifica si el laberinto es resolvible utilizando una búsqueda en profundidad.

    Un laberinto es resolvible si hay un camino disponible del punto de inicio y el punto de fin.

    Devuelve:
        bool: Verdadero si el laberinto es resolvible, falso en caso contrario.
    """
    grid = np.array(grid)
    return get_min_steps(grid) is not None


# Utils de frozen_lake, usado para step() de ellos, nosotros no lo usamos
def categorical_sample(prob_n, np_random: np.random.Generator):
    """
    Muestra de una distribución categórica donde cada fila especifica las probabilidades de clase.

    Parámetros:
        prob_n (array_like): Arreglo de probabilidades por clase.
        np_random (np.random.Generator): Generador de números aleatorios de NumPy.

    Devuelve:
        int: Índice de la clase seleccionada.
    """
    prob_n = np.asarray(prob_n)
    csprob_n = np.cumsum(prob_n)
    return np.argmax(csprob_n > np_random.random())


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
        valid = is_winneable(board)
    return board
