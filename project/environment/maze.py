class Maze:
    def __init__(self, grid, size, start_point, exit_point):
        self.grid = grid
        self.size = size
        self.start_point = start_point
        self.end_point = exit_point

    def is_winneable(self):
        # Arreglo del camino recorrido
        camino = []
        # Set visitados del DFS
        visitados = set()
        # Anyade primer elemento al camino grid[0][0]
        camino.append((0, 0))
        # Mientras haya algo en camino
        while camino:
            # Saco el primer elemento del camino (row, col)
            row, col = camino.pop()
            # Si no esta visitado
            if not (row, col) in visitados:
                # Lo agrega como visitado
                visitados.add((row, col))
                # Arreglo de direcciones: moverse 1 en x, 1 en y, -1 en x, -1 en y
                directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                # Recorrer el arreglo de direcciones
                for x, y in directions:
                    # La nueva posicion row_new = row + movimiento hecho
                    # col_new = col + movimiento hecho
                    row_new = row + x
                    col_new = col + y
                    # Si se pasa a los negativos o llega al tamanyo maximo, busca otros visitados
                    if row_new < 0 or row_new >= self.size or col_new < 0 or col_new >= self.size:
                        continue
                    # Si pudo llegar a la salida, hay un camino posible
                    if self.grid[row_new][col_new] == 3:
                        return True
                    # Si no se piso una mina, ni se llego a la salida, y esta dentro de los limites
                    # Agrega al camino por recorrer el nuevo row y col
                    if self.grid[row_new][col_new] != 4:
                        camino.append((row_new, col_new))
        # Si despues de recorrer todos los caminos posibles no se encontro la salida, devuelve False
        return False