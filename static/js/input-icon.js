function eyeIcon(inputId, iconElement) {
    let passwordInput = document.getElementById(inputId);
    
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        iconElement.src = "/static/icons/eye.svg"; 
    } else {
        passwordInput.type = "password";    
        iconElement.src = "/static/icons/eye-slash.svg"; 
    }
}


function openModal() {
    let modal = document.querySelector('.passwordWindow');

    modal.style.display = 'flex';
    // Определяем позицию по центру с учетом текущей прокрутки
    let windowHeight = window.innerHeight;
    let modalHeight = modal.offsetHeight;
    let topPosition = window.scrollY + (windowHeight - modalHeight) / 2;
    
    modal.style.top = `${topPosition}px`; // Устанавливаем верхнее положение модального окна
    modal.style.left = '50%'; // Устанавливаем левое положение в центр
    modal.style.transform = 'translate(-50%, 0)'; // Центрируем модальное окно по горизонтали

    document.querySelector('.overlay').style = "display: flex;";
    document.querySelector('.content').style = "filter: blur(4px)";
    document.body.classList.add('modal-open');
}

function closeModal() {
    document.querySelector('.overlay').style.display = 'none';
    document.querySelector('.passwordWindow').style.display = 'none'; 
    document.body.classList.remove('modal-open');
    document.querySelector('.content').style = "filter: none";
}

// Закрываем модальное окно при клике вне его
document.querySelector('.overlay').addEventListener('click', closeModal);