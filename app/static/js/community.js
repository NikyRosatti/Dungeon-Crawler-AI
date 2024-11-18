document.addEventListener('DOMContentLoaded', function () {
    const gridElement = document.getElementById('mazes-grid');

    // Extraer el JSON serializado desde el atributo data-mazes
    const mazes = JSON.parse(gridElement.dataset.mazes);

    // Iterar sobre cada maze y generar la cuadrícula
    mazes.forEach(maze => {
        const mapaOriginal = maze.grid;
        const n = Math.sqrt(mapaOriginal.length); // Suponiendo que el grid sea cuadrado
        const mapaConParedes = [];

        // Agregar borde superior
        mapaConParedes.push(...Array(n + 2).fill(1));

        // Agregar bordes laterales y filas centrales del mapa original
        for (let i = 0; i < n; i++) {
            mapaConParedes.push(1); // Borde izquierdo
            mapaConParedes.push(...mapaOriginal.slice(i * n, (i + 1) * n)); // Mapa original
            mapaConParedes.push(1); // Borde derecho
        }

        // Agregar borde inferior
        mapaConParedes.push(...Array(n + 2).fill(1));

        // Crear un nuevo div para el maze
        const mazeCard = document.createElement('div');
        mazeCard.classList.add('maze-card');

        // Crear el grid
        const mazeGrid = document.createElement('div');
        mazeGrid.classList.add('grid');
        mazeGrid.style.gridTemplateColumns = `repeat(${n + 2}, 1fr)`;
        mazeGrid.style.gridTemplateRows = `repeat(${n + 2}, 1fr)`;

        // Generar celdas de la cuadrícula
        mapaConParedes.forEach(value => {
            const cell = document.createElement('div');
            cell.classList.add('cell');

            switch (value) {
                case -1:
                    cell.classList.add('agent');  // Posición del agente
                    break;
                case 0:
                    cell.classList.add('floor');  // Piso
                    break;
                case 1:
                    cell.classList.add('wall');  // Pared
                    break;
                case 2:
                    cell.classList.add('start');  // Inicio
                    break;
                case 3:
                    cell.classList.add('end');    // Final
                    break;
                case 4:
                    cell.classList.add('mine');
                    break;
            }

            mazeGrid.appendChild(cell);
        });

        // Crear el título para la tarjeta
        const mazeTitle = document.createElement('div');
        mazeTitle.classList.add('maze-title');
        mazeTitle.textContent = `Maze ${maze.id}`; // Título del laberinto

        // Crear el enlace para jugar el laberinto
        const playButton = document.createElement('a');
        playButton.href = `/map?maze_id=${maze.id}`; // Enlace al laberinto
        playButton.classList.add('btn');
        playButton.textContent = 'Play maze';

        const username = document.createElement('p');
        username.textContent = `Creado por: ${maze.username}`; // Nombre de usuario

        // Crear el párrafo para la fecha de creación
        const createdAt = document.createElement('p');
        createdAt.textContent = `Creado el: ${new Date(maze.created_at).toLocaleDateString()}`; // Formato de la fecha

        // Añadir el título, el grid, el botón y la fecha a la tarjeta
        mazeCard.appendChild(mazeTitle);
        mazeCard.appendChild(mazeGrid);
        mazeCard.appendChild(playButton);
        mazeCard.appendChild(username);
        mazeCard.appendChild(createdAt);
        // Añadir la tarjeta generada al contenedor
        gridElement.appendChild(mazeCard);
    });
});
