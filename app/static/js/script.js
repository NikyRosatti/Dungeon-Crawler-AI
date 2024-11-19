import { showModal } from './modal.js';

const socket = io();

document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname === '/map') {
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
                    case 4:
                        cell.classList.add('mine');
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
        
        // Escuchar el evento "lose_by_mine"
        socket.on('lose_by_mine', function(data) {
            // Buscar la celda del agente en el grid
            const pos = data.pos; // Esta es la posición de la mina
            const gridCells = document.querySelectorAll('.cell'); // Asegúrate de que este sea el selector correcto
            const [y, x] = pos;

            // Suponiendo que n es el tamaño original del mapa (sin bordes)
            const n = Math.sqrt(gridCells.length) - 2; // Número de celdas en una fila/columna del mapa original
            // Calcular el índice en el NodeList
            const index = (y + 1) * (n + 2) + (x + 1)
            
            const Cell = gridCells[index];
            
            // Cambiar la imagen de fondo de la celda del agente a explosion.gif
            if (Cell) {
                Cell.style.backgroundImage = "url('/static/gifs/explotion.gif'), url(/static/img/dirt.jpg)";
                Cell.style.backgroundSize = 'cover'; // Asegúrate de que la imagen cubra completamente la celda
                Cell.style.backgroundPosition = 'center'; // Centrar la imagen
                Cell.style.backgroundRepeat = 'no-repeat';

                showModal('mineExploded');

                // Ralentizar la reaparición del agente después de 2 segundos
                setTimeout(() => {
                    // Restaurar la imagen del agente después de la explosión
                    Cell.style.backgroundImage = `url('/static/img/mine.png'), url(/static/img/dirt.jpg)`;
                    Cell.style.backgroundSize = 'cover'; // Ajustar el tamaño del fondo
                    Cell.style.backgroundPosition = 'center bottom, center center';
                    Cell.style.backgroundRepeat = 'no-repeat, no-repeat';
                }, 1500); // Esperar 1.5 segundos
            }
        });
        document.addEventListener('keydown', function(event) {
            const key = event.key;
            if ((key == 'ArrowUp' || key == 'ArrowLeft' || key == 'ArrowDown' || key == 'ArrowRight')) {
                socket.emit('move', key);
            }
        });

        socket.on("lose_by_steps", (data) => {
            const {steps} = data;
            showModal("maximumSteps", steps);
        });

        // Escuchar el evento "win"
        socket.on("win", (data) => {
            const {points} = data;
            showModal('won', points);
        });

        // Escuchar el evento "lose"
        socket.on("lose", () => {
            showModal("maximumSteps");
        });
    }


    document.getElementById('trainBtn').addEventListener('click', function() {
        // Configuración inicial para restablecer el modal y el progreso
        const mazeId = document.body.getAttribute('data-maze-id');
        socket.emit('start_training', { maze_id: mazeId });

        // Mostrar overlay y modal, reiniciando visibilidad y barra de progreso
        const overlay = document.getElementById('overlay');
        const progressModal = document.getElementById('progressModal');
        const progressBar = document.getElementById('progressBar');
        
        overlay.classList.add('visible');           // Muestra el overlay
        overlay.style.visibility = 'visible';       // Asegura que esté visible en la segunda ejecución
        progressModal.style.display = 'block';      // Muestra la barra de progreso
        progressBar.style.width = '0%';             // Reinicia el ancho de la barra de progreso
        progressBar.textContent = '0%';             // Reinicia el texto de la barra

        // Evento para verificar si el entrenamiento finalizó
        socket.on('training_status', function(data) {
            if (data.status === "finished") {
                overlay.classList.remove('visible'); // Oculta el overlay
                setTimeout(() => {
                    progressModal.style.display = 'none'; // Oculta el modal con un pequeño retardo
                }, 500);
            }
        });

        // Actualizar barra de progreso
        socket.on('progress', function(data) {
            const progress = data.progress;
            progressBar.style.width = progress + '%';
            progressBar.textContent = Math.round(progress) + '%';

            // Ocultar el overlay y el modal al llegar al 100%
            if (progress >= 100) {
                setTimeout(() => {
                    overlay.style.visibility = 'hidden';
                    progressModal.style.display = 'none';
                }, 500);
            }
        });
    });


    document.getElementById('testTrainBtn').addEventListener('click', function() {
        // Obtener el maze_id del atributo data-maze-id del cuerpo
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
        const mazeId = document.body.getAttribute('data-maze-id');
        socket.emit('stopTraining', { maze_id: mazeId });
    });

    window.addEventListener('beforeunload', function() {
        const mazeId = document.body.getAttribute('data-maze-id');
        socket.emit('stopTraining', { maze_id: mazeId });
    });
});