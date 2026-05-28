document.addEventListener('DOMContentLoaded', function () {
    const typeSelect = document.querySelector('#id_device_type');
    const computerFields = document.querySelector('.computer-fields');
    const consoleFields = document.querySelector('.console-fields');

    function toggleDeviceFields() {
        const val = typeSelect.value;
        if (val === 'computer') {
            if (computerFields) computerFields.style.display = '';
            if (consoleFields) consoleFields.style.display = 'none';
        } else if (val === 'console') {
            if (computerFields) computerFields.style.display = 'none';
            if (consoleFields) consoleFields.style.display = '';
        } else {
            if (computerFields) computerFields.style.display = 'none';
            if (consoleFields) consoleFields.style.display = 'none';
        }
    }

    if (typeSelect) {
        typeSelect.addEventListener('change', toggleDeviceFields);
        // первоначальное состояние
        toggleDeviceFields();

        // Обработка динамической загрузки мест при смене зала
        const hallSelect = document.querySelector('#id_hall');
        const spotSelect = document.querySelector('#id_spot');
        if (hallSelect && spotSelect) {
            hallSelect.addEventListener('change', function () {
                const hallId = this.value;
                if (!hallId) {
                    spotSelect.innerHTML = '<option value="">---------</option>';
                    return;
                }
                fetch(`/js/spots/available/?hall_id=${hallId}`)
                    .then(response => response.json())
                    .then(data => {
                        spotSelect.innerHTML = '<option value="">---------</option>';
                        data.spots.forEach(spot => {
                            const option = new Option(spot.label, spot.id);
                            spotSelect.appendChild(option);
                        });
                    });
            });
        }
    }
});