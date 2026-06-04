document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.tariff__card');
    const ids = ['card__one', 'card__two', 'card__three', 'card__four', 'card__five', 'card__six'];

    cards.forEach((card, index) => {
        // Циклически выбираем id: 0 -> card__one, 1 -> card__two, ... 5 -> card__six, 6 -> card__one и т.д.
        const id = ids[index % ids.length];
        card.id = id;
    });
});