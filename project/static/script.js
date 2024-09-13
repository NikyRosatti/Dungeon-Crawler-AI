// script.js

// Mapa original (0: piso, 2: inicio, 3: fin)
const mapaOriginal = [
    0, 1, 0, 0,
    0, 2, 0, 0,
    0, 0, 3, 0,
    0, 0, 0, 0,
];

// Tamaño del mapa original
const n = Math.sqrt(mapaOriginal.length);

// Crear un nuevo mapa con bordes de pared
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

// Establecer el tamaño de la cuadrícula basado en el número de celdas
grid.style.gridTemplateColumns = `repeat(${n + 2}, 1fr)`; // +2 para los bordes
grid.style.gridTemplateRows = `repeat(${n + 2}, 1fr)`; // +2 para los bordes

// Generar celdas de la cuadrícula
mapaConParedes.forEach(value => {
    const cell = document.createElement('div');
    cell.classList.add('cell');
    
    switch (value) {
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
