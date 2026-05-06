(function($) {
    $(document).ready(function() {
        function toggleFields() {
            var type = $('#id_device_type').val();

            // Сначала скрываем оба блока
            $('.computer-fields').hide();
            $('.console-fields').hide();

            // Показываем нужный блок
            if (type === 'computer') {
                $('.computer-fields').show();
            } else if (type === 'console') {
                $('.console-fields').show();
            }
        }

        // Вызываем функцию при загрузке
        toggleFields();

        // И при изменении типа
        $('#id_device_type').change(toggleFields);
    });
})(django.jQuery);