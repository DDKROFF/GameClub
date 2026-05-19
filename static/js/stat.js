document.addEventListener('DOMContentLoaded', () => {
    // ===== Автоматический просмотр новости через Intersection Observer =====
    const viewedNews = new Set(); // локальный кэш уже учтённых просмотров
    const viewTimers = new Map();  // новость id -> таймер

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const newsItem = entry.target;
            const newsId = newsItem.dataset.newsId;

            if (entry.isIntersecting) {
                // Начинаем таймер, если ещё не запущен и новость не просмотрена
                if (!viewedNews.has(newsId) && !viewTimers.has(newsId)) {
                    const timer = setTimeout(() => {
                        // Дополнительная проверка, что элемент всё ещё видим
                        if (isElementInViewport(newsItem)) {
                            sendView(newsId);
                            viewedNews.add(newsId);
                            observer.unobserve(newsItem); // прекращаем наблюдение
                        }
                        viewTimers.delete(newsId);
                    }, 3500); // 3.5 секунды

                    viewTimers.set(newsId, timer);
                }
            } else {
                // Элемент ушёл из зоны видимости – отменяем таймер, если был
                if (viewTimers.has(newsId)) {
                    clearTimeout(viewTimers.get(newsId));
                    viewTimers.delete(newsId);
                }
            }
        });
    }, { threshold: 0.6 }); // 60% элемента должно быть видно

    // Наблюдаем все новости
    document.querySelectorAll('.news-item').forEach(item => {
        observer.observe(item);
    });

    // Проверка видимости элемента (альтернатива, если нужно)
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        const windowWidth = window.innerWidth || document.documentElement.clientWidth;
        return (
            rect.top >= -rect.height * 0.4 &&
            rect.left >= -rect.width * 0.4 &&
            rect.bottom <= windowHeight + rect.height * 0.4 &&
            rect.right <= windowWidth + rect.width * 0.4
        );
    }

    // Отправка просмотра
    function sendView(newsId) {
        fetch(`/news/${newsId}/view/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const viewsSpan = document.querySelector(`.news-item[data-news-id="${newsId}"] .views-count span`);
                if (viewsSpan) viewsSpan.textContent = data.views;
            }
        })
        .catch(err => console.error('Ошибка просмотра:', err));
    }

    // ===== Лайки и дизлайки =====
    document.querySelectorAll('.like-btn, .dislike-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const newsItem = this.closest('.news-item');
            const newsId = newsItem.dataset.newsId;
            const action = this.dataset.action; // 'like' или 'dislike'

            // Проверяем, голосовали ли уже (localStorage)
            const storageKey = `voted_${newsId}`;
            if (localStorage.getItem(storageKey)) {
                alert('Вы уже голосовали за эту новость');
                return;
            }

            fetch(`/news/${newsId}/${action}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновляем счётчики
                    const likesSpan = newsItem.querySelector('.likes-count');
                    const dislikesSpan = newsItem.querySelector('.dislikes-count');
                    if (likesSpan) likesSpan.textContent = data.likes;
                    if (dislikesSpan) dislikesSpan.textContent = data.dislikes;
                    // Блокируем обе кнопки
                    newsItem.querySelectorAll('.like-btn, .dislike-btn').forEach(b => {
                        b.style.pointerEvents = 'none';
                        b.style.opacity = '0.6';
                    });
                    localStorage.setItem(storageKey, action);
                } else {
                    alert(data.message || 'Ошибка');
                }
            })
            .catch(err => console.error('Ошибка голосования:', err));
        });
    });

    // Функция получения CSRF-токена из cookie (стандартная для Django)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});