export const showModal = async (type_message, points) => {
    const modal = document.getElementById('modal');
    const modalMessage = document.getElementById('modal-message');
    const modalClose = document.getElementById('close-modal');
    
    // Get the browser language (only the 'es' prefix from 'es-US')
    const userLanguage = navigator.language.split('-')[0] || 'en';
    
    // Load translations
    const translations = await loadTranslations(userLanguage);
    
    console.log("Translations loaded:", translations); // Check if translations are loaded correctly
    
    // Check if the key exists in the translations and assign the translated message
    let translatedMessage = translations[type_message] ? translations[type_message][userLanguage] || translations[type_message].en : `Translation not found for key: ${type_message}`; 
    // Detailed error message if not found
    
    console.log("Valor de puntos:", points);

    // If there is a score, it is replaced by its value
    if (translatedMessage.includes('${points}')) {
        translatedMessage = translatedMessage.replace('${points}', points);
    }

    // Update the modal message with the translation
    modalMessage.textContent = translatedMessage;
    
    // Ensure the modal is visible
    modal.style.display = 'block';


    modalClose.onclick = () => {
        closeModal();
    };

    // Also allows closing the modal when clicking outside of it
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });
};

// Function to load the translation JSON file
const loadTranslations = async (language) => {
    console.log(`Loading translation file for language: ${language}`);
    try {
        const response = await fetch('/static/modals_translations/translates.json');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error loading translations:', error);
        return {}; // Empty object if loading fails
    }
};

export const closeModal = () => {
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
};
