(function() {
    // ----------------------------------------------------------------
    // 1. СТАТИЧНАЯ КОНФИГУРАЦИЯ ЗАЛОВ
    // ----------------------------------------------------------------
    const HALLS_CONFIG = [
        {
            id: 1,
            name: 'Зал Стандарт',
            max_capacity: 13,
            matrix: [
                [
                    { type: 'pc', spotNumber: 1 },
                    { type: 'pc', spotNumber: 2 },
                    { type: 'pc', spotNumber: 3 },
                    { type: 'pc', spotNumber: 4 },
                    { type: 'pc', spotNumber: 5 },
                    { type: 'spacer' },
                    { type: 'con', spotNumber: 11 }
                ],
                [
                    { type: 'pc', spotNumber: 6 },
                    { type: 'pc', spotNumber: 7 },
                    { type: 'pc', spotNumber: 8 },
                    { type: 'pc', spotNumber: 9 },
                    { type: 'pc', spotNumber: 10 },
                    { type: 'con', spotNumber: 12 },
                    { type: 'con', spotNumber: 13 }
                ]
            ]
        },
        {
            id: 2,
            name: 'VIP зал',
            max_capacity: 12,
            matrix: [
                [
                    { type: 'spacer' },
                    { type: 'pc', spotNumber: 1 },
                    { type: 'pc', spotNumber: 2 },
                    { type: 'pc', spotNumber: 3 },
                    { type: 'pc', spotNumber: 4 },
                    { type: 'pc', spotNumber: 5 },
                    { type: 'spacer' }
                ],
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
    ];

    const statusRussian = {
        'available': 'Свободен 🟢',
        'reserved': 'Забронирован 🔵',
        'maintenance': 'Обслуживание 🟡',
        'in_use': 'Используется 🔴'
    };

    let devicesData = {};
    let autoRefreshEnabled = true;
    let autoRefreshInterval = null;

    // ----------------------------------------------------------------
    // 2. ГЕНЕРАЦИЯ HTML-СЕТКИ
    // ----------------------------------------------------------------
    function renderStaticGrid() {
        const container = document.getElementById('hallsContainer');
        container.innerHTML = '';

        HALLS_CONFIG.forEach(hall => {
            // Счетчики сбрасываются индивидуально для каждого зала
            let pcCounter = 0;
            let conCounter = 0;

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

                    const deviceKey = `${hall.id}_${cellData.spotNumber}`;
                    let label = '';
                    let iconSrc = '';

                    // Раздельный инкремент ПК и Консолей
                    if (cellData.type === 'pc') {
                        pcCounter++;
                        label = `PC ${pcCounter}`;
                        iconSrc = STATIC_IMAGES.pc;
                        cell.className = 'grid-cell computer';
                    } else if (cellData.type === 'con') {
                        conCounter++;
                        label = `CON ${conCounter}`;
                        iconSrc = STATIC_IMAGES.console;
                        cell.className = 'grid-cell console';
                    }

                    cell.setAttribute('data-device-key', deviceKey);
                    cell.innerHTML = `
                        <div class="status-dot"></div>
                        <div class="cell-icon"><img src="${iconSrc}" alt="${label}"></div>
                        <div class="cell-label">${label}</div>
                    `;

                    devicesData[deviceKey] = {
                        type: cellData.type,
                        label: label,
                        status: 'available',
                        inventory: '',
                        hallName: hall.name,
                        spotNumber: cellData.spotNumber,
                        info: null
                    };

                    cell.setAttribute('title', `${label} – ${statusRussian['available']}`);

                    // Привязка клика к открытию модального окна
                    cell.addEventListener('click', () => {
                        openDeviceModal(deviceKey);
                    });

                    rowDiv.appendChild(cell);
                });

                li.appendChild(rowDiv);
                gridUl.appendChild(li);
            });

            const totalDevices = Object.keys(devicesData).filter(k => k.startsWith(`${hall.id}_`)).length;
            document.getElementById(`total-${hall.id}`).textContent = totalDevices;
        });
    }

    // ----------------------------------------------------------------
    // 3. ЗАГРУЗКА СТАТУСОВ ИЗ API
    // ----------------------------------------------------------------
    async function loadStatusesFromDB() {
        try {
            const response = await fetch('/api/statuses/all/');
            const data = await response.json();
            if (data.success && data.statuses) {
                for (const [key, info] of Object.entries(data.statuses)) {
                    if (devicesData[key]) {
                        devicesData[key].status = info.status;
                        devicesData[key].inventory = info.inventory || '';
                        devicesData[key].info = info;
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
    // 4. ОБНОВЛЕНИЕ ВИЗУАЛА И СКРЫТИЕ СКЛАДА
    // ----------------------------------------------------------------
    function updateVisuals() {
        for (const [key, device] of Object.entries(devicesData)) {
            const cell = document.querySelector(`.grid-cell[data-device-key="${key}"]`);
            if (!cell) continue;

            // Проверка: находится ли устройство на складе
            const info = device.info;
            if (info && (info.is_warehouse || info.spot === null || info.spot === 'Склад')) {
                cell.style.visibility = 'hidden';
                cell.style.pointerEvents = 'none';
                continue;
            } else {
                cell.style.visibility = 'visible';
                cell.style.pointerEvents = 'auto';
            }

            const status = device.status;
            cell.classList.remove('available', 'reserved', 'maintenance', 'in_use');
            cell.classList.add(status);

            cell.setAttribute('title', `${device.label} (Инв. №${device.inventory || '—'}) – ${statusRussian[status] || status}`);
        }

        HALLS_CONFIG.forEach(hall => {
            const cells = document.querySelectorAll(`#grid-${hall.id} .grid-cell:not(.spacer)`);
            let counts = { available: 0, reserved: 0, maintenance: 0, in_use: 0 };
            cells.forEach(cell => {
                if (cell.style.visibility === 'hidden') return; // Не учитываем скрытые складские устройства
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
    // 5. УПРАВЛЕНИЕ РАБОТОЙ МОДАЛЬНОГО ОКНА
    // ----------------------------------------------------------------
    function openDeviceModal(deviceKey) {
        const device = devicesData[deviceKey];
        if (!device) return;

        const info = device.info || {};
        const modal = document.getElementById('specModal');
        const modalName = document.getElementById('modalDeviceName');
        const modalLocation = document.getElementById('modalDeviceLocation');
        const specsTable = document.getElementById('specsTable');
        const bookBtn = document.getElementById('bookBtn');

        // Название с инвентарным номером
        modalName.textContent = info.inventory ? `${device.label} (Инв. № ${info.inventory})` : device.label;

        const statusText = statusRussian[device.status] || device.status;
        modalLocation.textContent = `${device.hallName} • Место ${device.spotNumber} (${statusText})`;

        let tableHTML = '';
        if (device.type === 'pc') {
            tableHTML = `
                <tr><td>Процессор (CPU)</td><td>${info.cpu || info.specCpu || '—'}</td></tr>
                <tr><td>Видеокарта (GPU)</td><td>${info.gpu || info.specGpu || '—'}</td></tr>
                <tr><td>Оперативная память</td><td>${info.ram_gb || info.ram || info.specRam || '—'}</td></tr>
                <tr><td>Накопитель</td><td>${info.storage_gb || info.storage || info.specStorage || '—'}</td></tr>
                <tr><td>Операционная система</td><td>${info.os || info.specOs || '—'}</td></tr>
            `;
        } else if (device.type === 'con') {
            tableHTML = `
                <tr><td>Тип консоли</td><td>${info.console_type || info.get_console_type_display || info.specCtype || '—'}</td></tr>
                <tr><td>Геймпады (кол-во)</td><td>${info.controller_count || info.specGamepads || '—'} шт.</td></tr>
                <tr><td>Объем памяти</td><td>${info.storage_gb || info.storage || info.specStorage || '—'}</td></tr>
                <tr><td>Поддержка VR</td><td>${info.has_vr_support || info.specVr || 'Нет'}</td></tr>
            `;
        }
        specsTable.innerHTML = tableHTML;

        // Передача ID для формы бронирования / сессии
        const dbId = info.id || info.deviceId;
        const reserveBtn = document.getElementById('reserveBtn');
        const startBtn = document.getElementById('startBtn');
        const modalBody = document.getElementById('modalBodyContent');

        if (dbId) {
            reserveBtn.style.display = 'inline-block';
            startBtn.style.display = 'inline-block';
            reserveBtn.dataset.deviceId = dbId;
            startBtn.dataset.deviceId = dbId;
            // remove previous handlers by cloning
            reserveBtn.replaceWith(reserveBtn.cloneNode(true));
            startBtn.replaceWith(startBtn.cloneNode(true));
        } else {
            reserveBtn.style.display = 'none';
            startBtn.style.display = 'none';
        }

        // attach listeners
        const newReserveBtn = document.getElementById('reserveBtn');
        const newStartBtn = document.getElementById('startBtn');
        if (newReserveBtn) {
            newReserveBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                if (!newReserveBtn.dataset.deviceId) return;
                modalBody.innerHTML = '<p>Загрузка формы...</p>';
                try {
                    const res = await fetch(`/booking/reserve-form/?device_id=${newReserveBtn.dataset.deviceId}`);
                    const html = await res.text();
                    modalBody.innerHTML = html;
                } catch (err) {
                    modalBody.innerHTML = '<p>Ошибка загрузки формы.</p>';
                }
            });
        }
        if (newStartBtn) {
            newStartBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                if (!newStartBtn.dataset.deviceId) return;
                modalBody.innerHTML = '<p>Загрузка формы...</p>';
                try {
                    const res = await fetch(`/booking/session-form/?device_id=${newStartBtn.dataset.deviceId}`);
                    const html = await res.text();
                    modalBody.innerHTML = html;
                } catch (err) {
                    modalBody.innerHTML = '<p>Ошибка загрузки формы.</p>';
                }
            });
        }

        modal.classList.add('active');
    }

    const hideModal = () => {
        document.getElementById('specModal').classList.remove('active');
    };

    // ----------------------------------------------------------------
    // 6. УПРАВЛЕНИЕ ОБНОВЛЕНИЕМ И ИНИЦИАЛИЗАЦИЯ
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
        toggleBtn.classList.add('hmbtn--primary');
    }

    function stopAutoRefresh() {
        if (autoRefreshInterval) clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        const toggleBtn = document.getElementById('autoRefreshToggle');
        toggleBtn.innerHTML = 'Автообновление: ВЫКЛ';
        toggleBtn.classList.remove('hmbtn--primary');
    }

    function init() {
        renderStaticGrid();

        // Слушатели модального окна
        const closeModal = document.getElementById('closeModal');
        const modalElement = document.getElementById('specModal');
        if (closeModal) closeModal.addEventListener('click', hideModal);
        if (modalElement) {
            modalElement.addEventListener('click', (e) => {
                if (e.target === modalElement) hideModal();
            });
        }

        document.getElementById('refreshBtn').addEventListener('click', refreshData);
        document.getElementById('autoRefreshToggle').addEventListener('click', () => {
            autoRefreshEnabled = !autoRefreshEnabled;
            autoRefreshEnabled ? startAutoRefresh() : stopAutoRefresh();
        });
        refreshData();
        startAutoRefresh();
    }

    document.addEventListener('DOMContentLoaded', init);
})();