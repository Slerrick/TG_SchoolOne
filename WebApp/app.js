// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;

// Элементы DOM
const pollForm = document.getElementById('pollForm');
const submitBtn = document.getElementById('submitBtn');
const aboutBtn = document.getElementById('aboutBtn');
const aboutModal = document.getElementById('aboutModal');
const closeBtn = aboutModal.querySelector('.close-btn');
const notification = document.getElementById('notification');

// Флаг отправки формы
let isSubmitting = false;

// Инициализация приложения
function initApp() {
    tg.expand();
    tg.enableClosingConfirmation();
    
    // Восстановить данные формы, если они были сохранены
    restoreFormData();
}

// Сохранить данные формы
function saveFormData() {
    const formData = {};
    const inputs = document.querySelectorAll('.answer-input');
    
    inputs.forEach(input => {
        formData[input.dataset.question] = input.value;
    });
    
    localStorage.setItem('poll_data', JSON.stringify(formData));
}

// Восстановить данные формы
function restoreFormData() {
    const savedData = localStorage.getItem('poll_data');
    if (savedData) {
        const formData = JSON.parse(savedData);
        const inputs = document.querySelectorAll('.answer-input');
        
        inputs.forEach(input => {
            const question = input.dataset.question;
            if (formData[question]) {
                input.value = formData[question];
            }
        });
    }
}

// Показать уведомление
function showNotification(message, type = 'success') {
    notification.textContent = message;
    notification.className = 'notification';
    
    if (type === 'error') {
        notification.classList.add('error');
    }
    
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Обработчик отправки формы
pollForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (isSubmitting) {
        return;
    }
    
    // Проверка заполнения всех полей
    const inputs = document.querySelectorAll('.answer-input');
    let allFilled = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            allFilled = false;
            input.style.borderColor = '#e74c3c';
        } else {
            input.style.borderColor = '';
        }
    });
    
    if (!allFilled) {
        showNotification('Пожалуйста, заполните все поля!', 'error');
        return;
    }
    
    // Сбор данных формы
    const formData = {};
    inputs.forEach(input => {
        formData[input.dataset.question] = input.value.trim();
    });
    
    // Добавить информацию о пользователе
    const userData = {
        userId: tg.initDataUnsafe.user?.id,
        username: tg.initDataUnsafe.user?.username,
        firstName: tg.initDataUnsafe.user?.first_name,
        lastName: tg.initDataUnsafe.user?.last_name,
        timestamp: new Date().toISOString()
    };
    
    const fullData = {
        ...userData,
        answers: formData
    };
    
    // Установить флаг отправки
    isSubmitting = true;
    
    // Показать индикатор загрузки
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="btn-text">Отправка...</span>';
    
    try {
        // Отправка данных через Telegram WebApp
        tg.sendData(JSON.stringify(fullData));
        
        // Показать уведомление об успехе
        showNotification('Спасибо! Ваши ответы отправлены.');
        
        // Очистить сохраненные данные
        localStorage.removeItem('poll_data');
        
        // Сбросить форму
        setTimeout(() => {
            pollForm.reset();
            isSubmitting = false;
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span class="btn-text">Отправить ответы</span><span class="btn-icon">📤</span>';
        }, 2000);
        
        // Закрыть приложение через 3 секунды
        setTimeout(() => {
            tg.close();
        }, 3000);
        
    } catch (error) {
        console.error('Ошибка при отправке данных:', error);
        showNotification('Ошибка при отправке. Попробуйте еще раз.', 'error');
        
        // Сбросить флаг отправки
        isSubmitting = false;
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="btn-text">Отправить ответы</span><span class="btn-icon">📤</span>';
    }
});

// Автосохранение при вводе
const inputs = document.querySelectorAll('.answer-input');
inputs.forEach(input => {
    input.addEventListener('input', saveFormData);
});

// Открытие модального окна about
aboutBtn.addEventListener('click', () => {
    aboutModal.style.display = 'flex';
});

// Закрытие модального окна
closeBtn.addEventListener('click', () => {
    aboutModal.style.display = 'none';
});

// Закрытие модального окна по клику вне его
aboutModal.addEventListener('click', (e) => {
    if (e.target === aboutModal) {
        aboutModal.style.display = 'none';
    }
});

// Готовность приложения
tg.ready();

// Инициализация приложения
initApp();