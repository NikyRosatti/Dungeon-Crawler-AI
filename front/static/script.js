// Obtener la matriz desde el atributo de datos del div
const grid = document.getElementById('grid');
const mapaOriginal = JSON.parse(grid.getAttribute('data-mapa-original'));

// El resto del código JS para manejar la matriz
const n = Math.sqrt(mapaOriginal.length);

const mapaConParedes = [];

mapaConParedes.push(...Array(n + 2).fill(1));

for (let i = 0; i < n; i++) {
    mapaConParedes.push(1);
    mapaConParedes.push(...mapaOriginal.slice(i * n, (i + 1) * n));
    mapaConParedes.push(1);
}

mapaConParedes.push(...Array(n + 2).fill(1));

grid.style.gridTemplateColumns = `repeat(${n + 2}, 1fr)`;
grid.style.gridTemplateRows = `repeat(${n + 2}, 1fr)`;

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
