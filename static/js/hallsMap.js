document.addEventListener('DOMContentLoaded', function() {
    function attachTooltips() {
        const tooltip = document.createElement('div');
        tooltip.classList.add('tooltip-club');
        document.body.appendChild(tooltip);
        tooltip.style.display = 'none';

        const allVisibleCells = document.querySelectorAll('.grid-cell.pc, .grid-cell.con, .grid-cell.entrance');
        allVisibleCells.forEach(cell => {
            let infoText = cell.getAttribute('data-info') || '';
            if (infoText) {
                // уже есть
            } else if (cell.classList.contains('pc')) infoText = '🖥️ ПК-место | Высокая производительность';
            else if (cell.classList.contains('con')) infoText = '🎮 Консольная станция';
            else if (cell.classList.contains('entrance')) infoText = '🚪 Вход/Выход';

            cell.addEventListener('mousemove', (e) => {
                tooltip.style.display = 'block';
                tooltip.innerHTML = `<i class="fas ${cell.classList.contains('pc') ? 'fa-desktop' : (cell.classList.contains('con') ? 'fa-gamepad' : 'fa-door-open')}" style="margin-right: 8px;"></i> ${infoText}`;
                tooltip.style.left = (e.clientX + 15) + 'px';
                tooltip.style.top = (e.clientY - 35) + 'px';
            });
            cell.addEventListener('mouseleave', () => {
                tooltip.style.display = 'none';
            });
            cell.addEventListener('click', () => {
                let typeName = cell.classList.contains('pc') ? 'PC' : (cell.classList.contains('con') ? 'CONSOLE' : 'ВХОД');
                alert(`🔹 ${typeName} — забронировать можно у администратора. Свободно!`);
            });
        });
    }
    attachTooltips();
});