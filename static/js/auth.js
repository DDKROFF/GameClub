document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('authModal');
    const openBtn = document.getElementById('openAuthModal');
    const closeBtn = document.getElementById('closeModal');
    const tabs = document.querySelectorAll('.modal-tab');
    const forms = document.querySelectorAll('.modal-form');

    // Открыть модальное окно
    openBtn.addEventListener('click', () => {
        modal.classList.add('active');
    });

    // Закрыть по крестику
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    // Закрыть по клику на затемнение
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
    });

    // Переключение вкладок
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Убираем active у всех вкладок и форм
            tabs.forEach(t => t.classList.remove('active'));
            forms.forEach(f => f.classList.remove('active'));

            // Активируем нужную вкладку и форму
            tab.classList.add('active');
            const formId = tab.dataset.tab === 'login' ? 'loginForm' : 'registerForm';
            document.getElementById(formId).classList.add('active');
        });
    });

    // Закрытие по Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            modal.classList.remove('active');
        }
    });
});