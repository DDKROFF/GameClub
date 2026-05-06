// JavaScript для анимаций при прокрутке (Intersection Observer)
document.addEventListener('DOMContentLoaded', function() {
    // Выбираем все элементы с классами fade-in и fade-up
    const animatedElements = document.querySelectorAll('.fade-in, .fade-up');

    // Создаём наблюдатель
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            // Если элемент появился в области видимости
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Можно продолжать наблюдать, но обычно после появления класс остаётся
                // observer.unobserve(entry.target); // Раскомментировать, если анимация должна сработать только раз
            }
        });
    }, {
        threshold: 0.2, // Срабатывает, когда 20% элемента видно
        rootMargin: '0px 0px -50px 0px' // Небольшой отступ снизу
    });

    // Наблюдаем за каждым элементом
    animatedElements.forEach(el => observer.observe(el));
});