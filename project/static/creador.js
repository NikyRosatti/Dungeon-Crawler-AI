document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('grid-container');
    const generateButton = document.getElementById('generate');
    const exportButton = document.getElementById('export');
    const sizeInput = document.getElementById('size');
    let selectedBlockType = null;
    let mapData = [];
    let startPlaced = false; // Variable para verificar si ya hay una entrada
    let endPlaced = false;   // Variable para verificar si ya hay una salida

    // Agregar funcionalidad a los botones de selección de bloques
    document.querySelectorAll('.controls button').forEach(button => {
        button.addEventListener('click', () => {
            // Desactivar otros botones
            document.querySelectorAll('.controls button').forEach(btn => btn.classList.remove('active'));
            // Activar el botón seleccionado
            button.classList.add('active');
            selectedBlockType = button.getAttribute('data-block'); // Obtener el tipo de bloque seleccionado
        });
    });

    // Generar mapa dinámico
    generateButton.addEventListener('click', () => {
        const size = parseInt(sizeInput.value);
        grid.style.gridTemplateColumns = `repeat(${size}, 50px)`; // Ajusta el tamaño de cada celda
        grid.style.gridTemplateRows = `repeat(${size}, 50px)`;
        grid.innerHTML = '';  // Limpiar el grid
        mapData = Array.from({ length: size }, () => Array(size).fill(null));

        for (let i = 0; i < size * size; i++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');  // Inicialmente solo tiene la clase "cell"
            const row = Math.floor(i / size);
            const col = i % size;

            // Manejo del clic en la celda para aplicar el tipo de bloque seleccionado
            cell.addEventListener('click', () => {
                if (selectedBlockType) {
                    if (selectedBlockType == 'start'){
                        //no permitimos mas de una entrada
                        if (startPlaced) {
                            alert('Solo se permite una entrada (inicio)');
                            return
                        }
                        startPlaced = true;
                    } else if (selectedBlockType === 'end') {
                        // no permitir mas de una salida
                        if (endPlaced) {
                            alert('Solo se permite una salida (fin)');
                            return;
                        }
                        endPlaced = true; // Marcar como salida colocada
                    }

                    // Si la celda tiene una clase "start" o "end" y cambia de tipo, permitir colocar otra entrada/salida
                    if (cell.classList.contains('start')) {
                        startPlaced = false; // Permitir colocar otra entrada si se reemplaza
                    }
                    if (cell.classList.contains('end')) {
                        endPlaced = false; // Permitir colocar otra salida si se reemplaza
                    }

                    // Quitar todas las clases existentes y agregar solo la seleccionada
                    mapData[row][col] = selectedBlockType;
                    cell.className = 'cell'; // Eliminar todas las clases y aplicar solo la seleccionada
                    cell.classList.add(selectedBlockType);
                }
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
