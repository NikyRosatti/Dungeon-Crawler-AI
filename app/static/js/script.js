if (window.location.pathname === '/map') {
    const socket = io();

    // Mapa original (0: piso, 2: inicio, 3: fin)
    socket.on('map', function(data) {
        mapaOriginal = data.mapaOriginal
        n = data.n

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

        // Obtener el contenedor de la cuadrícula
        const grid = document.getElementById('grid');
        grid.innerHTML = ''; // Limpiar el grid antes de generar uno nuevo

        // Establecer el tamaño de la cuadrícula basado en el número de celdas
        grid.style.gridTemplateColumns = `repeat(${n + 2}, 1fr)`; // +2 para los bordes
        grid.style.gridTemplateRows = `repeat(${n + 2}, 1fr)`; // +2 para los bordes

        // Generar celdas de la cuadrícula
        mapaConParedes.forEach(value => {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            
            switch (value) {
                case -2: 
                    cell.classList.add('winner_agent');
                    break;
                case -1:
                    cell.classList.add('agent');
                    break;
                case 0:
                    cell.classList.add('floor');
                    break;
                case 1:
                    cell.classList.add('wall');
                    break;
                case 2:
                    cell.classList.add('start');
                    break;
                case 3:
                    cell.classList.add('end');
                    break;
            }
            
            grid.appendChild(cell);
        });

    });
    
    socket.on('finish_map', function(message){
        var sound = document.getElementById("winSound");
        sound.play();

        setTimeout(function(){
            socket.emit('restart_pos', 0);
        },1000);

    });
    
    document.addEventListener('keydown', function(event) {
        const key = event.key;
        if ((key == 'ArrowUp' || key == 'ArrowLeft' || key == 'ArrowDown' || key == 'ArrowRight')) {
            socket.emit('move', key);
        }
    });
}
