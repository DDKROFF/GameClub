document.addEventListener('DOMContentLoaded', function () {
    function updateSpotOptions(hallSelectId, spotSelectId) {
        const hallSelect = document.querySelector(hallSelectId);
        const spotSelect = document.querySelector(spotSelectId);
        if (!hallSelect || !spotSelect) return;

        hallSelect.addEventListener('change', function () {
            const hallId = this.value;
            if (!hallId) {
                spotSelect.innerHTML = '<option value="">---------</option>';
                return;
            }
            // Запрашиваем свободные места для выбранного зала
            fetch(`/js/spots/available/?hall_id=${hallId}`)
                .then(response => response.json())
                .then(data => {
                    spotSelect.innerHTML = '<option value="">---------</option>';
                    data.spots.forEach(function (spot) {
                        const option = new Option(spot.label, spot.id);
                        spotSelect.appendChild(option);
                    });
                });
        });
    }

    // Применяем для компьютеров и консолей
    updateSpotOptions('#id_hall', '#id_spot');
});