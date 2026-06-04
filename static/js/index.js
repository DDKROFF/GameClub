document.addEventListener('DOMContentLoaded', function() {
    // ----- Анимации при прокрутке (оставляем как есть) -----
    const animatedElements = document.querySelectorAll('.fade-in, .fade-up');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.2, rootMargin: '0px 0px -50px 0px' });
    animatedElements.forEach(el => observer.observe(el));

    // ----- Пагинация новостей (3 + показать ещё + скрыть) -----
    const newsContainer = document.getElementById('news-list-container');
    if (!newsContainer) return;

    const newsItems = Array.from(newsContainer.querySelectorAll('.news-item'));
    const totalNews = newsItems.length;
    const SHOW_PER_CLICK = 3;          // показывать по 3 новости
    const INITIAL_SHOW = 3;             // изначально показано 3

    let currentlyShown = INITIAL_SHOW;   // сколько новостей сейчас видно (всегда первые N)
    let hasMore = totalNews > INITIAL_SHOW;

    // Элементы кнопок
    const loadMoreBtn = document.getElementById('load-more-news');
    const hideBtn = document.getElementById('hide-news');

    // Функция обновления видимости новостей (первые currentlyShown видны, остальные скрыты)
    function updateVisibility() {
        newsItems.forEach((item, idx) => {
            if (idx < currentlyShown) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    // Функция обновления состояния кнопок
    function updateButtons() {
        if (!loadMoreBtn || !hideBtn) return;

        const moreAvailable = totalNews > currentlyShown;
        const hasHidden = totalNews > INITIAL_SHOW && currentlyShown > INITIAL_SHOW; // есть ли подгруженные

        // Кнопка "Показать ещё"
        if (moreAvailable) {
            loadMoreBtn.style.display = 'inline-flex';
        } else {
            loadMoreBtn.style.display = 'none';
        }

        // Кнопка "Скрыть" показываем, если показано больше, чем INITIAL_SHOW
        if (hasHidden) {
            hideBtn.style.display = 'inline-flex';
        } else {
            hideBtn.style.display = 'none';
        }
    }

    // Инициализация: показываем первые INITIAL_SHOW новостей
    if (totalNews > 0) {
        currentlyShown = Math.min(INITIAL_SHOW, totalNews);
        updateVisibility();
        updateButtons();
    } else {
        // Если новостей нет – прячем обе кнопки
        if (loadMoreBtn) loadMoreBtn.style.display = 'none';
        if (hideBtn) hideBtn.style.display = 'none';
        return;
    }

    // Обработчик "Показать ещё"
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            // Показываем следующую порцию
            let nextShown = Math.min(currentlyShown + SHOW_PER_CLICK, totalNews);
            if (nextShown === currentlyShown) return;
            currentlyShown = nextShown;
            updateVisibility();
            updateButtons();
        });
    }

    // Обработчик "Скрыть" – скрываем все, кроме первых INITIAL_SHOW
    if (hideBtn) {
        hideBtn.addEventListener('click', function() {
            if (currentlyShown > INITIAL_SHOW) {
                currentlyShown = INITIAL_SHOW;
                updateVisibility();
                updateButtons();
            }
        });
    }
});