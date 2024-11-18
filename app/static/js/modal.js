export const showModal = (type_message) => {
    const modal = document.getElementById('modal');
    const modalMessage = document.getElementById('modal-message');
    const modalClose = document.getElementById('close-modal');

    
    modalMessage.textContent = type_message;
    modal.style.display = 'block';

    modalClose.onclick = () => {
        closeModal();
    };

    // También permite cerrar el modal al hacer clic fuera de él
    window.addEventListener('click', (event) => {
        const modal = document.getElementById('modal');
        if (event.target == modal) {
            closeModal();
        }
    });
};

export const closeModal = () => {
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
};