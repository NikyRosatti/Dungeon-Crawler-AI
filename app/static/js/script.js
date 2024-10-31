if (window.location.pathname === '/map') {
    const socket = io();

    // Emitir el evento para iniciar la simulación cuando se conecte al servidor


    // Escuchar las actualizaciones del mapa
    socket.on('map', function(mapaOriginal) {
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
                case -2:
                    cell.classList.add('end'); 
                    cell.style.backgroundImage = `url(${avatarUrl}), url(/static/img/salida.png),url(/static/img/dirt.jpg)`;
                    cell.style.backgroundSize = '73%, cover'; // Ajustar tamaño de fondo
                    cell.style.backgroundPosition = 'center bottom, center center'; // Posicionar ambas imágenes
                    cell.style.backgroundRepeat = 'no-repeat, no-repeat'; // Sin repetir ambas imágenes
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

    const showModal = (message) => {
        const modal = document.getElementById('modal');
        const modalMessage = document.getElementById('modal-message');
        modalMessage.textContent = message;
        modal.style.display = 'block';
    };
    
    const closeModal = () => {
        const modal = document.getElementById('modal');
        modal.style.display = 'none';
    };

    // Escuchar el evento "win"
    socket.on("win", (data) => {
        const points = data.points;
        showModal(`¡Ganaste! Has obtenido ${points} puntos.`);
    });
    document.getElementById('close-modal').addEventListener('click', closeModal);
    // Escuchar el evento "lose"
    socket.on("lose", () => {
        showModal("Tu agente no pudo completar el laberinto en el número máximo de pasos. ¡Inténtalo de nuevo!");
    });
}


document.getElementById('trainBtn').addEventListener('click', function() {
    // Obtener el maze_id del atributo data-maze-id del cuerpo
    const socket = io();
    const mazeId = document.body.getAttribute('data-maze-id');
    socket.emit('start_training', { maze_id: mazeId });

    document.getElementById('overlay').classList.add('visible'); // Muestra el overlay
    document.getElementById('progressModal').style.display = 'block'; // Muestra la barra de progreso
    document.getElementById('progressBar').style.width = '0%'; // Reinicia la barra de progreso
    document.getElementById('progressBar').textContent = '0%'; // Reinicia el texto

    // Mostrar el overlay y la barra de progreso
    socket.on('training_status', function(data) {
        const overlay = document.getElementById('overlay');
        if (data.status === "finished") {
            overlay.classList.remove('visible'); // Oculta el overlay
            setTimeout(() => {
                document.getElementById('progressModal').style.display = 'none'; // Ocultar la barra de progreso
            }, 500); // Retardo antes de ocultar (opcional)
        }
    });

    // Actualizar barra de progreso
    socket.on('progress', function(data) {
        const progress = data.progress;
        const progressBar = document.getElementById('progressBar');
        progressBar.style.width = progress + '%';
        progressBar.textContent = Math.round(progress) + '%';

        // Ocultar el overlay al llegar al 100%
        if (progress >= 100) {
            setTimeout(() => {
                document.getElementById('overlay').style.visibility = 'hidden';
                document.getElementById('progressModal').style.display = 'none'; // Ocultar la barra de progreso
            }, 500); // Retardo antes de ocultar (opcional)
        }
    });
});

document.getElementById('testTrainBtn').addEventListener('click', function() {
    // Obtener el maze_id del atributo data-maze-id del cuerpo
    const socket = io();
    const mazeId = document.body.getAttribute('data-maze-id');
    socket.emit('testTraining', { maze_id: mazeId });

    // Escuchar el progreso del entrenamiento
    socket.on('training_status', function(data) {
        console.log("Estado del entrenamiento:", data.status);
        if (data.status === 'finished') {
            console.log("Entrenamiento completado.");
        } else if (data.status === 'stopped') {
            console.log("Entrenamiento detenido.");
        } else if (data.status === 'error') {
            console.error("Error:", data.message);
        }
    });
});

document.getElementById('stopTrainBtn').addEventListener('click', function() {
    const socket = io();
    const mazeId = document.body.getAttribute('data-maze-id');
    socket.emit('stopTraining', { maze_id: mazeId });
});

window.addEventListener('beforeunload', function() {
    const socket = io();
    const mazeId = document.body.getAttribute('data-maze-id');
    socket.emit('stopTraining', { maze_id: mazeId });
});