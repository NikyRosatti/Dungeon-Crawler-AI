document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('grid-container');
    const generateButton = document.getElementById('generate');
    const exportButton = document.getElementById('export');
    const sizeInput = document.getElementById('size');
    let selectedBlockType = null;
    let mapData = [];
    let startPlaced = false;
    let endPlaced = false;

    // Función para agregar bordes de pared
    const createMapWithBorders = (originalMap, n) => {
        const mapWithWalls = [];

        // Agregar fila superior de paredes
        mapWithWalls.push(...Array(n + 2).fill("wall"));

        // Agregar paredes laterales y el mapa original
        for (let i = 0; i < n; i++) {
            mapWithWalls.push("wall");  // Borde izquierdo
            mapWithWalls.push(...originalMap.slice(i * n, (i + 1) * n));
            mapWithWalls.push("wall");  // Borde derecho
        }

        // Agregar fila inferior de paredes
        mapWithWalls.push(...Array(n + 2).fill("wall"));

        return mapWithWalls;
    };

    // Manejo de selección de tipo de bloque
    document.querySelectorAll('.controls button').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.controls button').forEach(btn => {
                btn.classList.remove('active');
            });
            button.classList.add('active');
            selectedBlockType = button.getAttribute('data-block');
        });
    });

    // Generar mapa dinámico con paredes alrededor
    generateButton.addEventListener('click', () => {
        const size = parseInt(sizeInput.value);
        const totalCells = size * size;

        // Crear mapa vacío con suelo
        const originalMap = Array(totalCells).fill("floor");
        mapData = createMapWithBorders(originalMap, size);

        grid.style.gridTemplateColumns = `repeat(${size + 2}, 50px)`; // +2 para los bordes
        grid.style.gridTemplateRows = `repeat(${size + 2}, 50px)`;
        grid.innerHTML = '';  // Limpiar el grid

        // Generar celdas con bordes de pared fijos
        mapData.forEach((value, index) => {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            const row = Math.floor(index / (size + 2));
            const col = index % (size + 2);

            switch (value) {
                case "wall":
                    cell.classList.add('wall');
                    break;
                case "floor":
                    cell.classList.add('floor');
                    // Permitir modificar celdas que no son paredes
                    cell.addEventListener('click', () => {
                        if (selectedBlockType) {
                            if (selectedBlockType == 'start' && startPlaced) {
                                alert('Solo se permite una entrada (inicio)');
                                return;
                            }
                            if (selectedBlockType == 'end' && endPlaced) {
                                alert('Solo se permite una salida (fin)');
                                return;
                            }
                            if (selectedBlockType === 'start') startPlaced = true;
                            if (selectedBlockType === 'end') endPlaced = true;
                            
                             // Si la celda tiene una clase "start" o "end" y cambia de tipo, permitir colocar otra entrada/salida
                            if (cell.classList.contains('start')) {
                                startPlaced = false; // Permitir colocar otra entrada si se reemplaza
                            }
                            if (cell.classList.contains('end')) {
                                endPlaced = false; // Permitir colocar otra salida si se reemplaza
                            }
                            mapData[index] = selectedBlockType;
                            cell.className = 'cell';  // Limpiar clases previas
                            cell.classList.add(selectedBlockType);
                        }
                    });
                    break;
            }

            grid.appendChild(cell);
        });
    });

    // Exportar mapa sin las paredes añadidas
    exportButton.addEventListener('click', () => {
        const size = parseInt(sizeInput.value);
        const innerMap = [];

        // Eliminar las paredes: recorremos las filas del centro, excluyendo las paredes
        for (let i = 1; i <= size; i++) {
            innerMap.push(...mapData.slice(i * (size + 2) + 1, (i + 1) * (size + 2) - 1));
        }

        const mapToValidate = innerMap.flat(); // Aplanar el arreglo para enviarlo fácilmente

        fetch('/validate_map', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ map: mapToValidate }), // Enviar el mapa a Python
        })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                alert('OK');
            } else {
                alert('No');
            }
        })
        .catch(error => console.error('Error al validar el mapa:', error));

        console.log('Mapa exportado:', innerMap);
    });
});
