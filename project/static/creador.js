document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('grid');
    const generateButton = document.getElementById('generate');
    const exportButton = document.getElementById('export');
    const sizeInput = document.getElementById('size');

    let mapData = [];

    // Generar mapa dinámico
    generateButton.addEventListener('click', () => {
        const size = parseInt(sizeInput.value);
        grid.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
        grid.innerHTML = '';  // Limpiar el grid
        mapData = Array.from({ length: size }, () => Array(size).fill(null));

        for (let i = 0; i < size * size; i++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');  // Inicialmente solo tiene la clase "cell"

            const cellOptions = document.createElement('div');
            cellOptions.classList.add('cell-options');

            // Tipos de celdas: floor, wall, start, end
            ['floor', 'wall', 'start', 'end'].forEach(type => {
                const option = document.createElement('div');
                option.dataset.type = type;
                option.textContent = type;  // Mostrar el nombre del tipo (floor, wall, etc.)
                option.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const row = Math.floor(i / size);
                    const col = i % size;
                    mapData[row][col] = type;

                    // Primero, eliminar cualquier clase tipo 'floor', 'wall', 'start', 'end'
                    cell.className = 'cell';  // Restablecer solo la clase base "cell"
                    cell.classList.add(type);  // Añadir la nueva clase "floor", "wall", etc.
                    cell.classList.remove('selected');  // Remover la clase 'selected'
                });
                cellOptions.appendChild(option);
            });

            cell.appendChild(cellOptions);

            cell.addEventListener('click', () => {
                cell.classList.toggle('selected');
            });

            grid.appendChild(cell);
        }
    });

    // Exportar el mapa como arreglo
    exportButton.addEventListener('click', () => {
        console.log('Mapa exportado:', mapData);
        alert(JSON.stringify(mapData));
    });
});
