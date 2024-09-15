class Maze:
    def __init__(self, grid, size, start_point, exit_point):
        self.grid = grid
        self.size = size
        self.start_point = start_point  # (fila, columna) debería ser una tupla
        self.exit_point = exit_point    # (fila, columna) debería ser una tupla

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
