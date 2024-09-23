if (window.location.pathname === '/map') {
    const socket = io();

    // Emitir el evento para iniciar la simulación cuando se conecte al servidor
    socket.emit('start_simulation');

    // Escuchar las actualizaciones del mapa
    socket.on('map_update', function(mapaConParedes) {
        const grid = document.getElementById('grid');
        grid.innerHTML = ''; // Limpiar el grid antes de generar uno nuevo

        // Tamaño del mapa con bordes
        const n = Math.sqrt(mapaConParedes.length);

        // Establecer el tamaño de la cuadrícula basado en el número de celdas
        grid.style.gridTemplateColumns = `repeat(${n}, 1fr)`;
        grid.style.gridTemplateRows = `repeat(${n}, 1fr)`;

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
            }

            grid.appendChild(cell);
        });
    });

    // Escuchar el evento cuando se resuelve el laberinto
    socket.on('finish_map', function(message){
        var sound = document.getElementById("winSound");
        sound.play();
    });
}
