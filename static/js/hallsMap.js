// hallsMap.js (обновлённый)
(function() {
    const HALLS_CONFIG = [
        {
            id: 1,
            name: 'Зал 1 (Стандарт)',
            max_capacity: 12,
            matrix: [
                ['pc', 'pc', 'pc', 'pc', 'pc', 'spacer', 'con'],
                ['pc', 'pc', 'pc', 'pc', 'pc', 'con', 'con']
            ]
        },
        {
            id: 2,
            name: 'VIP зал',
            max_capacity: 10,
            matrix: [
                ['spacer', 'pc', 'pc', 'pc', 'pc', 'pc', 'spacer'],
                ['con', 'pc', 'pc', 'pc', 'pc', 'pc', 'con']
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

    // Генерация статичной HTML-сетки
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
            let pcCounter = 1;
            let conCounter = 1;

            hall.matrix.forEach((row, rowIndex) => {
                const li = document.createElement('li');
                const rowDiv = document.createElement('div');
                rowDiv.className = 'grid-row';

                row.forEach((cellType, colIndex) => {
                    const cell = document.createElement('div');

                    if (cellType === 'spacer') {
                        cell.className = 'grid-cell spacer';
                        rowDiv.appendChild(cell);
                        return;
                    }

                    const deviceKey = `${hall.id}_${rowIndex}_${colIndex}`;
                    let label = '';
                    let iconSrc = '';

                    if (cellType === 'pc') {
                        label = `PC ${pcCounter++}`;
                        iconSrc = STATIC_IMAGES.pc;
                        cell.className = 'grid-cell computer';
                    } else if (cellType === 'con') {
                        label = `Console ${conCounter++}`;
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

                    devicesData[deviceKey] = {
                        type: cellType,
                        label: label,
                        status: 'available',
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

            const totalDevices = document.querySelectorAll(`#grid-${hall.id} .grid-cell:not(.spacer)`).length;
            document.getElementById(`total-${hall.id}`).textContent = totalDevices;
        });
    }

    async function loadStatusesFromDB() {
        try {
            const response = await fetch('/api/statuses/all/');
            const data = await response.json();
            if (data.success && data.statuses) {
                for (const [key, info] of Object.entries(data.statuses)) {
                    if (devicesData[key]) {
                        devicesData[key].status = info.status;
                        devicesData[key].inventory = info.inventory;
                    }
                }
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error loading statuses:', error);
            return false;
        }
    }

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

    function init() {
        renderStaticGrid();
        document.getElementById('refreshBtn').addEventListener('click', refreshData);
        document.getElementById('autoRefreshToggle').addEventListener('click', () => {
            autoRefreshEnabled = !autoRefreshEnabled;
            autoRefreshEnabled ? startAutoRefresh() : stopAutoRefresh();
        });
        refreshData();
        startAutoRefresh();
    }

    init();
})();