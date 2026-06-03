// Маска телефона для поля phone (формат 8(XXX)XXX-XX-XX)
function initPhoneMask() {
    const phoneInput = document.querySelector('.phone-mask');
    if (!phoneInput) return;

    phoneInput.addEventListener('input', function(e) {
        let x = this.value.replace(/\D/g, '');  // только цифры
        if (x.length === 0) {
            this.value = '';
            return;
        }
        // Ограничиваем 11 цифрами (начиная с 8)
        if (x.length > 11) x = x.slice(0, 11);
        let formatted = '';
        // Первая цифра 8
        if (x.length > 0) formatted = '8';
        if (x.length > 1) formatted += ' (' + x.slice(1, 4);
        if (x.length > 4) formatted += ') ' + x.slice(4, 7);
        if (x.length > 7) formatted += '-' + x.slice(7, 9);
        if (x.length > 9) formatted += '-' + x.slice(9, 11);
        this.value = formatted;
        // Перемещаем курсор в конец
        this.selectionStart = this.selectionEnd = this.value.length;
    });

    // При фокусе, если поле пустое, ставим 8
    phoneInput.addEventListener('focus', function() {
        if (this.value === '') {
            this.value = '8';
        }
    });

    // При потере фокуса, если введено менее 11 цифр, показываем ошибку
    phoneInput.addEventListener('blur', function() {
        let digits = this.value.replace(/\D/g, '');
        if (digits.length > 0 && digits.length !== 11) {
            this.style.borderColor = '#ff6b6b';
        } else {
            this.style.borderColor = '';
        }
    });
}

// Показать/скрыть пароль
function initPasswordToggles() {
    document.querySelectorAll('.toggle-password').forEach(icon => {
        icon.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const input = document.getElementById(targetId);
            if (input) {
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                this.classList.toggle('fa-eye-slash');
            }
        });
    });
}

// Валидация перед отправкой (необязательно, но улучшает UX)
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    form.addEventListener('submit', function(e) {
        let isValid = true;
        // Пример: проверка телефона на странице регистрации
        const phoneField = document.querySelector('#id_phone');
        if (phoneField && formId === 'registerForm') {
            const phoneRegex = /^8\(\d{3}\)\d{3}-\d{2}-\d{2}$/;
            if (!phoneRegex.test(phoneField.value)) {
                showFieldError(phoneField, 'Введите телефон в формате 8(XXX)XXX-XX-XX');
                e.preventDefault();
                isValid = false;
            } else {
                clearFieldError(phoneField);
            }
        }
        return isValid;
    });
}

function showFieldError(field, message) {
    let errorDiv = field.parentElement.querySelector('.field-error');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'form-error field-error';
        field.parentElement.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
    field.style.borderColor = '#ff6b6b';
}

function clearFieldError(field) {
    const errorDiv = field.parentElement.querySelector('.field-error');
    if (errorDiv) errorDiv.remove();
    field.style.borderColor = '';
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    initPhoneMask();
    initPasswordToggles();
    validateForm('loginForm');
    validateForm('registerForm');
});