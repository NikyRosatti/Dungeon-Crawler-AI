if (window.location.pathname === '/map') {
    const socket = io();

    // Emitir el evento para iniciar la simulación cuando se conecte al servidor
    socket.emit('start_simulation');

    // Escuchar las actualizaciones del mapa
    socket.on('map_update', function(mapaOriginal) {
        const grid = document.getElementById('grid');
        grid.innerHTML = ''; // Limpiar el grid antes de generar uno nuevo

        const n = Math.sqrt(mapaOriginal.length); // Suponiendo que el grid es cuadrado
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

        // Establecer el tamaño de la cuadrícula basado en el número de celdas con bordes
        const gridSize = n + 2;
        grid.style.gridTemplateColumns = `repeat(${gridSize}, 1fr)`;
        grid.style.gridTemplateRows = `repeat(${gridSize}, 1fr)`;

        // Generar celdas de la cuadrícula con bordes
        mapaConParedes.forEach(value => {
            const cell = document.createElement('div');
            cell.classList.add('cell');

            switch (value) {
                case -1:
                    cell.classList.add('agent');  // Posición del agente
                    // Establecer la imagen de fondo del agente con el avatar del usuario
                    cell.style.backgroundImage = `url(${avatarUrl}), url(/static/img/dirt.jpg)`;
                    cell.style.backgroundSize = '73%, cover'; // Ajustar tamaño de fondo
                    cell.style.backgroundPosition = 'center bottom, center center'; // Posicionar ambas imágenes
                    cell.style.backgroundRepeat = 'no-repeat, no-repeat'; // Sin repetir ambas imágenes
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
