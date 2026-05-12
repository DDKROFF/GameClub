(function() {
        // ── Конфигурация залов (матрицы) ──────────────
        const hallsData = [
            {
                name: 'Зал 1 (Стандарт)',
                matrix: [
                    // 1 ряд: 5 ПК, заглушка, 1 консоль
                    ['pc','pc','pc','pc','pc','spacer','con'],
                    // 2 ряд: 5 ПК, 1 консоль, заглушка
                    ['pc','pc','pc','pc','pc','con','con']
                ]
            },
            {
                name: 'VIP зал',
                matrix: [
                    // 1 ряд: заглушка, 5 ПК, заглушка
                    ['spacer','pc','pc','pc','pc','pc','spacer'],
                    // 2 ряд: консоль, 5 ПК, консоль
                    ['con','pc','pc','pc','pc','pc','con']
                ]
            }
        ];

        // Генерация ID и номеров для устройств
        const deviceMap = new Map(); // id -> { type, label, hallIdx }
        const hallDeviceIds = [];     // массив массивов ID по залам

        hallsData.forEach((hall, hallIdx) => {
            const idsInHall = [];
            let pcNumber = 1;          // нумерация ПК внутри зала
            let consoleNumber = 1;
            hall.matrix.forEach((row, rowIdx) => {
                row.forEach((cellType, colIdx) => {
                    if (cellType === 'pc' || cellType === 'con') {
                        const id = `${hallIdx}-${rowIdx}-${colIdx}`;
                        let label = '';
                        if (cellType === 'pc') {
                            label = `PC ${pcNumber++}`;
                        } else {
                            label = `Console ${consoleNumber++}`;
                        }
                        deviceMap.set(id, {
                            type: cellType,
                            label: label,
                            hallIdx,
                            row: rowIdx,
                            col: colIdx
                        });
                        idsInHall.push(id);
                    }
                });
            });
            hallDeviceIds.push(idsInHall);
        });

        // Состояние занятости
        let occupancy = {};

        // DOM элементы
        const hallsContainer = document.getElementById('hallsContainer');
        const refreshBtn = document.getElementById('refreshBtn');
        const autoRefreshBtn = document.getElementById('autoRefreshToggle');
        const lastUpdatedSpan = document.getElementById('lastUpdatedTime');
        let autoRefreshEnabled = true;
        let autoRefreshInterval = null;

        // Рендер всех залов (с номерами ПК)
        function renderAllHalls() {
            hallsContainer.innerHTML = '';
            hallsData.forEach((hall, hallIdx) => {
                const hallDiv = document.createElement('div');
                hallDiv.className = 'map-section';
                hallDiv.innerHTML = `
                    <div class="hall-title">
                        <i class="fas fa-layer-group"></i> ${hall.name}
                    </div>
                    <div class="stats-row" id="stats-hall-${hallIdx}">
                        <div class="stat-chip free"><i class="fas fa-circle"></i> Свободно: <strong id="free-${hallIdx}">0</strong></div>
                        <div class="stat-chip occupied"><i class="fas fa-circle"></i> Занято: <strong id="occupied-${hallIdx}">0</strong></div>
                        <div class="stat-chip total"><i class="fas fa-cube"></i> Всего устройств: <strong id="total-${hallIdx}">0</strong></div>
                    </div>
                    <div class="map-grid-wrapper">
                        <div class="club-grid" id="grid-hall-${hallIdx}"></div>
                    </div>
                `;
                hallsContainer.appendChild(hallDiv);

                const grid = document.getElementById(`grid-hall-${hallIdx}`);
                // Временные счётчики для подстановки номеров
                let pcCounter = 1;
                let conCounter = 1;
                hall.matrix.forEach(row => {
                    const rowDiv = document.createElement('div');
                    rowDiv.className = 'grid-row';
                    row.forEach(cellType => {
                        const cell = document.createElement('div');
                        cell.className = `grid-cell ${cellType}`;
                        if (cellType === 'pc' || cellType === 'con') {
                            const label = cellType === 'pc' ? `PC ${pcCounter++}` : `Console ${conCounter++}`;
                            const icon = cellType === 'pc' ? 'fa-desktop' : 'fa-playstation';
                            cell.innerHTML = `
                                <div class="cell-tooltip"></div>
                                <div class="status-dot"></div>
                                <div class="cell-icon"><i class="fas ${icon}"></i></div>
                                <div class="cell-label">${label}</div>
                            `;
                            cell.style.cursor = 'pointer';
                            cell.addEventListener('click', () => {
                                const devId = cell.dataset.deviceId;
                                if (devId && deviceMap.has(devId)) {
                                    const dev = deviceMap.get(devId);
                                    const status = occupancy[devId] ? 'Занято 🔴' : 'Свободно 🟢';
                                    alert(`${dev.label}\nСтатус: ${status}`);
                                }
                            });
                        } else if (cellType === 'entrance') {
                            cell.innerHTML = `<div class="cell-icon"><i class="fas fa-door-open"></i></div><div class="cell-label">ВХОД</div>`;
                        }
                        // spacer остаётся пустым
                        rowDiv.appendChild(cell);
                    });
                    grid.appendChild(rowDiv);
                });
            });
        }

        // Привязка deviceId к ячейкам
        function bindDeviceIds() {
            hallsData.forEach((hall, hallIdx) => {
                const grid = document.getElementById(`grid-hall-${hallIdx}`);
                if (!grid) return;
                const cells = grid.querySelectorAll('.grid-cell.pc, .grid-cell.con');
                const ids = hallDeviceIds[hallIdx];
                cells.forEach((cell, idx) => {
                    if (idx < ids.length) {
                        cell.dataset.deviceId = ids[idx];
                    }
                });
            });
        }

        // Обновление статусов и счётчиков
        function updateStatuses() {
            hallsData.forEach((hall, hallIdx) => {
                const ids = hallDeviceIds[hallIdx];
                let free = 0, occupied = 0;
                ids.forEach(id => {
                    if (occupancy[id]) occupied++; else free++;
                });
                document.getElementById(`free-${hallIdx}`).textContent = free;
                document.getElementById(`occupied-${hallIdx}`).textContent = occupied;
                document.getElementById(`total-${hallIdx}`).textContent = ids.length;

                const grid = document.getElementById(`grid-hall-${hallIdx}`);
                if (!grid) return;
                const cells = grid.querySelectorAll('.grid-cell.pc, .grid-cell.con');
                cells.forEach(cell => {
                    const devId = cell.dataset.deviceId;
                    if (!devId || !deviceMap.has(devId)) return;
                    const isOccupied = occupancy[devId] === true;
                    cell.classList.remove('free-status', 'occupied-status');
                    cell.classList.add(isOccupied ? 'occupied-status' : 'free-status');
                    const tooltip = cell.querySelector('.cell-tooltip');
                    if (tooltip) {
                        const dev = deviceMap.get(devId);
                        tooltip.textContent = `${dev.label} – ${isOccupied ? 'Занято 🔴' : 'Свободно 🟢'}`;
                    }
                });
            });
        }

        // Имитация запроса к API
        async function fetchOccupancy() {
            await new Promise(r => setTimeout(r, 400 + Math.random() * 400));
            const result = {};
            deviceMap.forEach((_, id) => {
                result[id] = Math.random() < 0.35; // ~35% занято
            });
            // Чтобы не все сразу были свободны/заняты
            const ids = Array.from(deviceMap.keys());
            const occCount = Object.values(result).filter(Boolean).length;
            if (occCount === ids.length) {
                ids.slice(0, Math.min(3, ids.length)).forEach(id => result[id] = false);
            } else if (occCount === 0 && ids.length > 1) {
                ids.slice(0, Math.min(2, ids.length)).forEach(id => result[id] = true);
            }
            return result;
        }

        async function refreshData() {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> Загрузка...';
            try {
                occupancy = await fetchOccupancy();
                updateStatuses();
                lastUpdatedSpan.textContent = new Date().toLocaleTimeString('ru-RU');
            } catch (e) {
                alert('Ошибка загрузки данных');
            } finally {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Обновить';
            }
        }

        function startAutoRefresh() {
            if (autoRefreshInterval) clearInterval(autoRefreshInterval);
            autoRefreshInterval = setInterval(refreshData, 30000);
            autoRefreshBtn.innerHTML = 'Автообновление: ВКЛ';
            autoRefreshBtn.classList.add('btn--primary');
        }
        function stopAutoRefresh() {
            if (autoRefreshInterval) clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
            autoRefreshBtn.innerHTML = 'Автообновление: ВЫКЛ';
            autoRefreshBtn.classList.remove('btn--primary');
        }

        autoRefreshBtn.addEventListener('click', () => {
            autoRefreshEnabled = !autoRefreshEnabled;
            autoRefreshEnabled ? startAutoRefresh() : stopAutoRefresh();
        });
        refreshBtn.addEventListener('click', refreshData);

        // Инициализация
        async function init() {
            renderAllHalls();
            bindDeviceIds();
            deviceMap.forEach((_, id) => occupancy[id] = false);
            updateStatuses();
            lastUpdatedSpan.textContent = '—';
            await refreshData();
            startAutoRefresh();
        }

        init();
    })();