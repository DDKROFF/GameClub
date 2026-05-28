// hallsMap.js – финальная версия (статика в JS, склад скрыт)
(function() {
    // ----------------------------------------------------------------
    // 1. СТАТИЧНАЯ КОНФИГУРАЦИЯ ЗАЛОВ
    //    id зала должно совпадать с Hall.id в БД
    //    spotNumber = Spot.number (место в зале)
    // ----------------------------------------------------------------
    const HALLS_CONFIG = [
        {
            id: 1,                     // id зала «Стандарт»
            name: 'Зал Стандарт',
            max_capacity: 13,
            matrix: [
                // Ряд 1: 5 ПК, пусто, консоль
                [
                    { type: 'pc', spotNumber: 1 },
                    { type: 'pc', spotNumber: 2 },
                    { type: 'pc', spotNumber: 3 },
                    { type: 'pc', spotNumber: 4 },
                    { type: 'pc', spotNumber: 5 },
                    { type: 'spacer' },
                    { type: 'con', spotNumber: 6 }
                ],
                // Ряд 2: 5 ПК, 2 консоли
                [
                    { type: 'pc', spotNumber: 7 },
                    { type: 'pc', spotNumber: 8 },
                    { type: 'pc', spotNumber: 9 },
                    { type: 'pc', spotNumber: 10 },
                    { type: 'pc', spotNumber: 11 },
                    { type: 'con', spotNumber: 12 },
                    { type: 'con', spotNumber: 13 }
                ]
            ]
        },
        {
            id: 2,                     // id зала «VIP»
            name: 'VIP зал',
            max_capacity: 12,
            matrix: [
                // Ряд 1: spacer, 5 ПК, spacer
                [
                    { type: 'spacer' },
                    { type: 'pc', spotNumber: 1 },
                    { type: 'pc', spotNumber: 2 },
                    { type: 'pc', spotNumber: 3 },
                    { type: 'pc', spotNumber: 4 },
                    { type: 'pc', spotNumber: 5 },
                    { type: 'spacer' }
                ],
                // Ряд 2: консоль, 5 ПК, консоль
                [
                    { type: 'con', spotNumber: 6 },
                    { type: 'pc', spotNumber: 7 },
                    { type: 'pc', spotNumber: 8 },
                    { type: 'pc', spotNumber: 9 },
                    { type: 'pc', spotNumber: 10 },
                    { type: 'pc', spotNumber: 11 },
                    { type: 'con', spotNumber: 12 }
                ]
            ]
        }
        // Склад (id=3) намеренно отсутствует – не показываем пользователям
    ];

    const statusRussian = {
        'available': 'Свободен 🟢',
        'reserved': 'Забронирован 🔵',
        'maintenance': 'Обслуживание 🟡',
        'in_use': 'Используется 🔴'
    };

    let devicesData = {};            // { "зал_место": { type, label, status, inventory } }
    let autoRefreshEnabled = true;
    let autoRefreshInterval = null;

    // ----------------------------------------------------------------
    // 2. ГЕНЕРАЦИЯ HTML-СЕТКИ (чистая статика)
    // ----------------------------------------------------------------
    function renderStaticGrid() {
        const container = document.getElementById('hallsContainer');
        container.innerHTML = '';

        HALLS_CONFIG.forEach(hall => {
            const hallSection = document.createElement('div');
            hallSection.className = 'map-section';
            hallSection.dataset.hallId = hall.id;
            hallSection.innerHTML = `
                <div class="hall-title">
                    <i class="fas fa-layer-group"></i> ${hall.name}
                    <span class="hall-capacity">(макс. ${hall.max_capacity} мест)</span>
                </div>
                <div class="stats-row">
                    <div class="stat-chip available"><i class="fas fa-circle"></i> Свободно: <strong id="available-${hall.id}">0</strong></div>
                    <div class="stat-chip reserved"><i class="fas fa-bookmark"></i> Забронировано: <strong id="reserved-${hall.id}">0</strong></div>
                    <div class="stat-chip maintenance"><i class="fas fa-tools"></i> Обслуживание: <strong id="maintenance-${hall.id}">0</strong></div>
                    <div class="stat-chip in_use"><i class="fas fa-ban"></i> Используется: <strong id="in_use-${hall.id}">0</strong></div>
                    <div class="stat-chip total"><i class="fas fa-cube"></i> Всего: <strong id="total-${hall.id}">0</strong></div>
                </div>
                <div class="map-grid-wrapper">
                    <div class="club-grid">
                        <ul id="grid-${hall.id}"></ul>
                    </div>
                </div>
            `;
            container.appendChild(hallSection);

            const gridUl = document.getElementById(`grid-${hall.id}`);

            hall.matrix.forEach((row) => {
                const li = document.createElement('li');
                const rowDiv = document.createElement('div');
                rowDiv.className = 'grid-row';

                row.forEach((cellData) => {
                    const cell = document.createElement('div');

                    if (cellData.type === 'spacer') {
                        cell.className = 'grid-cell spacer';
                        rowDiv.appendChild(cell);
                        return;
                    }

                    // Ключ для связи с API: id_зала_номерМеста
                    const deviceKey = `${hall.id}_${cellData.spotNumber}`;
                    let label = '';
                    let iconSrc = '';

                    if (cellData.type === 'pc') {
                        label = `PC ${cellData.spotNumber}`;
                        iconSrc = STATIC_IMAGES.pc;
                        cell.className = 'grid-cell computer';
                    } else if (cellData.type === 'con') {
                        label = `Console ${cellData.spotNumber}`;
                        iconSrc = STATIC_IMAGES.console;
                        cell.className = 'grid-cell console';
                    }

                    cell.setAttribute('data-device-key', deviceKey);
                    cell.innerHTML = `
                        <div class="cell-tooltip"></div>
                        <div class="status-dot"></div>
                        <div class="cell-icon"><img src="${iconSrc}" alt="${label}"></div>
                        <div class="cell-label">${label}</div>
                    `;

                    // Инициализируем запись в devicesData
                    devicesData[deviceKey] = {
                        type: cellData.type,
                        label: label,
                        status: 'available',   // по умолчанию
                        inventory: ''
                    };

                    cell.addEventListener('click', () => {
                        const status = devicesData[deviceKey]?.status || 'available';
                        alert(`${label}\nСтатус: ${statusRussian[status]}`);
                    });

                    rowDiv.appendChild(cell);
                });

                li.appendChild(rowDiv);
                gridUl.appendChild(li);
            });

            // Подсчитываем реальные устройства (не spacer'ы) в этом зале
            const totalDevices = Object.keys(devicesData).filter(k => k.startsWith(`${hall.id}_`)).length;
            document.getElementById(`total-${hall.id}`).textContent = totalDevices;
        });
    }

    // ----------------------------------------------------------------
    // 3. ЗАГРУЗКА СТАТУСОВ ИЗ API
    //    API отдаёт объект: { "зал_место": { status, type, label, inventory } }
    // ----------------------------------------------------------------
    async function loadStatusesFromDB() {
        try {
            const response = await fetch('/api/statuses/all/');
            const data = await response.json();
            if (data.success && data.statuses) {
                // Обновляем только те ключи, которые есть в нашей статике
                for (const [key, info] of Object.entries(data.statuses)) {
                    if (devicesData[key]) {
                        devicesData[key].status = info.status;
                        devicesData[key].inventory = info.inventory;
                        // type и label не трогаем – они статичны
                    }
                }
                return true;
            }
            return false;
        } catch (error) {
            console.error('Ошибка загрузки статусов:', error);
            return false;
        }
    }

    // ----------------------------------------------------------------
    // 4. ОБНОВЛЕНИЕ ВИЗУАЛА (цвета, счётчики)
    // ----------------------------------------------------------------
    function updateVisuals() {
        for (const [key, device] of Object.entries(devicesData)) {
            const cell = document.querySelector(`.grid-cell[data-device-key="${key}"]`);
            if (!cell) continue;

            const status = device.status;
            cell.classList.remove('available', 'reserved', 'maintenance', 'in_use');
            cell.classList.add(status);

            const tooltip = cell.querySelector('.cell-tooltip');
            if (tooltip) {
                tooltip.textContent = `${device.label} – ${statusRussian[status]}`;
            }
        }

        // Счётчики по залам
        HALLS_CONFIG.forEach(hall => {
            const cells = document.querySelectorAll(`#grid-${hall.id} .grid-cell:not(.spacer)`);
            let counts = { available: 0, reserved: 0, maintenance: 0, in_use: 0 };
            cells.forEach(cell => {
                const key = cell.getAttribute('data-device-key');
                const status = devicesData[key]?.status || 'available';
                if (counts.hasOwnProperty(status)) counts[status]++;
            });
            document.getElementById(`available-${hall.id}`).textContent = counts.available;
            document.getElementById(`reserved-${hall.id}`).textContent = counts.reserved;
            document.getElementById(`maintenance-${hall.id}`).textContent = counts.maintenance;
            document.getElementById(`in_use-${hall.id}`).textContent = counts.in_use;
        });
    }

    // ----------------------------------------------------------------
    // 5. УПРАВЛЕНИЕ ОБНОВЛЕНИЕМ
    // ----------------------------------------------------------------
    async function refreshData() {
        const refreshBtn = document.getElementById('refreshBtn');
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> Загрузка...';
        const success = await loadStatusesFromDB();
        if (success) {
            updateVisuals();
            document.getElementById('lastUpdatedTime').textContent = new Date().toLocaleTimeString('ru-RU');
        }
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Обновить';
    }

    function startAutoRefresh() {
        if (autoRefreshInterval) clearInterval(autoRefreshInterval);
        autoRefreshInterval = setInterval(async () => {
            const success = await loadStatusesFromDB();
            if (success) updateVisuals();
        }, 30000);
        const toggleBtn = document.getElementById('autoRefreshToggle');
        toggleBtn.innerHTML = 'Автообновление: ВКЛ';
        toggleBtn.classList.add('btn--primary');
    }

    function stopAutoRefresh() {
        if (autoRefreshInterval) clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        const toggleBtn = document.getElementById('autoRefreshToggle');
        toggleBtn.innerHTML = 'Автообновление: ВЫКЛ';
        toggleBtn.classList.remove('btn--primary');
    }

    // ----------------------------------------------------------------
    // 6. ИНИЦИАЛИЗАЦИЯ
    // ----------------------------------------------------------------
    function init() {
        renderStaticGrid();
        document.getElementById('refreshBtn').addEventListener('click', refreshData);
        document.getElementById('autoRefreshToggle').addEventListener('click', () => {
            autoRefreshEnabled = !autoRefreshEnabled;
            autoRefreshEnabled ? startAutoRefresh() : stopAutoRefresh();
        });
        refreshData();          // первая загрузка
        startAutoRefresh();     // автообновление каждые 30 сек
    }

    init();
})();