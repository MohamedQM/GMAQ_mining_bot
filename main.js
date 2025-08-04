// Global variables
let activeMiningCount = 0;

// Device detection
function detectDevice() {
    const userAgent = navigator.userAgent;
    let device = 'غير معروف';
    let deviceIcon = 'fas fa-desktop';

    if (/Mobi|Android/i.test(userAgent)) {
        device = 'هاتف ذكي';
        deviceIcon = 'fas fa-mobile-alt';
    } else if (/iPad|Tablet/i.test(userAgent)) {
        device = 'تابلت';
        deviceIcon = 'fas fa-tablet-alt';
    } else {
        device = 'كمبيوتر';
        deviceIcon = 'fas fa-desktop';
    }

    document.getElementById('deviceInfo').innerHTML = `<i class="${deviceIcon}"></i> ${device}`;
}

// Toggle User Agent details
function toggleUserAgent() {
    const details = document.getElementById('userAgentDetails');
    const toggleText = document.getElementById('uaToggleText');

    if (details.style.display === 'none') {
        details.style.display = 'block';
        toggleText.textContent = 'إخفاء التفاصيل';
    } else {
        details.style.display = 'none';
        toggleText.textContent = 'عرض التفاصيل';
    }
}

// Start mining function
async function startMining(miningType) {
    const urlInput = document.getElementById(`${miningType.toLowerCase()}Url`);
    const url = urlInput.value.trim();
    const useCustomUA = document.getElementById('useCustomUA').checked;

    if (!url) {
        showNotification('يرجى إدخال رابط التعدين أولاً', 'error');
        return;
    }

    if (!url.includes('tgWebAppData=')) {
        showNotification('رابط غير صحيح. يجب أن يحتوي على tgWebAppData', 'error');
        return;
    }

    try {
        showLoading(miningType, 'start');

        const response = await fetch('/api/start_mining', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                mining_type: miningType,
                init_data: url,
                use_custom_ua: useCustomUA
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
            updateMiningStatus();
            loadUrlHistory(); // تحديث سجل الروابط
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('حدث خطأ في الاتصال', 'error');
        console.error('Error:', error);
    } finally {
        hideLoading(miningType, 'start');
    }
}

// Stop mining function
async function stopMining(miningType) {
    try {
        showLoading(miningType, 'stop');

        const response = await fetch('/api/stop_mining', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                mining_type: miningType
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
            updateMiningStatus();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('حدث خطأ في الاتصال', 'error');
        console.error('Error:', error);
    } finally {
        hideLoading(miningType, 'stop');
    }
}

// Stop all mining
async function stopAllMining() {
    if (!confirm('هل أنت متأكد من إيقاف جميع أنواع التعدين؟')) {
        return;
    }

    try {
        const response = await fetch('/api/stop_all_mining', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
            updateMiningStatus();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('حدث خطأ في الاتصال', 'error');
        console.error('Error:', error);
    }
}

// Update mining status
async function updateMiningStatus() {
    try {
        const response = await fetch('/api/mining_status');
        const data = await response.json();

        if (data.success) {
            const status = data.status;
            const stats = data.stats;
            activeMiningCount = 0;

            // Update status badges
            ['COIN', 'BANAN', 'TRX', 'SHIB', 'BEAMX'].forEach(type => {
                const statusElement = document.getElementById(`${type.toLowerCase()}Status`);
                const tasksElement = document.getElementById(`${type.toLowerCase()}Tasks`);

                if (status[type]) {
                    statusElement.textContent = 'يعمل';
                    statusElement.className = 'status-badge active';
                    activeMiningCount++;
                } else {
                    statusElement.textContent = 'متوقف';
                    statusElement.className = 'status-badge';
                }

                // Update task counts
                if (tasksElement) {
                    tasksElement.textContent = stats.mining_types[type] || 0;
                }
            });

            // Update active mining count
            const activeMiningElement = document.getElementById('activeMining');
            if (activeMiningElement) {
                activeMiningElement.textContent = activeMiningCount;
            }
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Show loading state
function showLoading(miningType, action) {
    const buttons = document.querySelectorAll(`[onclick*="${miningType}"]`);
    buttons.forEach(button => {
        if (button.textContent.includes(action === 'start' ? 'بدء' : 'إيقاف')) {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.innerHTML = `<span class="loading"></span> ${action === 'start' ? 'جاري البدء...' : 'جاري الإيقاف...'}`;
            button.dataset.originalText = originalText;
        }
    });
}

// Hide loading state
function hideLoading(miningType, action) {
    const buttons = document.querySelectorAll(`[onclick*="${miningType}"]`);
    buttons.forEach(button => {
        if (button.disabled && button.dataset.originalText) {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText;
            delete button.dataset.originalText;
        }
    });
}

function showNotification(message, type = 'success') {
    const toast = document.getElementById('notificationToast');
    const toastBody = toast.querySelector('.toast-body');

    toastBody.textContent = message;
    toast.className = `toast text-white bg-${type === 'success' ? 'success' : 'danger'}`;

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

function updateOperationLogs() {
    fetch('/api/operation_logs')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayOperationLogs(data.logs);
            }
        })
        .catch(error => {
            console.error('خطأ في تحميل سجل العمليات:', error);
        });
}

function displayOperationLogs(logs) {
    const logsContainer = document.getElementById('operationLogs');

    if (!logs || logs.length === 0) {
        logsContainer.innerHTML = '<p class="text-muted">لا توجد عمليات مسجلة</p>';
        return;
    }

    let html = '';
    // عرض آخر 10 سجلات
    const recentLogs = logs.slice(-10).reverse();

    recentLogs.forEach(log => {
        const date = new Date(log.timestamp);
        const timeString = date.toLocaleTimeString('ar-EG');

        let statusClass = '';
        let statusIcon = '';

        if (log.status === 'نجح') {
            statusClass = 'text-success';
            statusIcon = 'fas fa-check-circle';
        } else if (log.status === 'فشل') {
            statusClass = 'text-danger';
            statusIcon = 'fas fa-times-circle';
        } else if (log.status === 'جاري') {
            statusClass = 'text-warning';
            statusIcon = 'fas fa-spinner fa-spin';
        }

        html += `
            <div class="operation-log-entry border-bottom pb-2 mb-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center gap-2 mb-1">
                            <span class="badge bg-secondary">${log.mining_type}</span>
                            <small class="text-muted">${timeString}</small>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <i class="${statusIcon} ${statusClass}"></i>
                            <strong>${log.step}</strong>
                        </div>
                        <small class="text-muted">${log.details}</small>
                    </div>
                    <div class="text-end">
                        <span class="badge ${statusClass.replace('text-', 'bg-')}">${log.status}</span>
                    </div>
                </div>
            </div>
        `;
    });

    logsContainer.innerHTML = html;

    // التمرير لأسفل لعرض أحدث السجلات
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

function clearOperationLogs() {
    if (confirm('هل أنت متأكد من مسح سجل العمليات؟')) {
        fetch('/api/clear_operation_logs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('تم مسح سجل العمليات بنجاح');
                updateOperationLogs();
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('خطأ في مسح سجل العمليات:', error);
            showNotification('حدث خطأ في مسح السجل', 'error');
        });
    }
}

// Admin functions
async function loadUsers() {
    try {
        const response = await fetch('/api/admin/users');
        const data = await response.json();

        if (data.success) {
            displayUsers(data.users);
            document.getElementById('usersContainer').style.display = 'block';
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('حدث خطأ في تحميل المستخدمين', 'error');
        console.error('Error:', error);
    }
}

function displayUsers(users) {
    const tbody = document.getElementById('usersTable');
    tbody.innerHTML = '';

    users.forEach(user => {
        const row = document.createElement('tr');

        // Active mining types
        const activeMining = Object.entries(user.is_running || {})
            .filter(([type, active]) => active)
            .map(([type, active]) => type)
            .join(', ') || 'لا يوجد';

        row.innerHTML = `
            <td>${user.user_id}</td>
            <td>${user.total_tasks}</td>
            <td>${activeMining}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-danger" onclick="adminStopUserMining('${user.user_id}', 'all')">
                        إيقاف الكل
                    </button>
                    <button class="btn btn-warning" onclick="adminStopUserMining('${user.user_id}', 'BANAN')">
                        إيقاف BANAN
                    </button>
                    <button class="btn btn-info" onclick="adminStopUserMining('${user.user_id}', 'TRX')">
                        إيقاف TRX
                    </button>
                </div>
            </td>
        `;

        tbody.appendChild(row);
    });
}

async function adminStopUserMining(userId, miningType) {
    if (!confirm(`هل أنت متأكد من إيقاف التعدين للمستخدم ${userId}؟`)) {
        return;
    }

    try {
        const response = await fetch('/api/admin/stop_user_mining', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                mining_type: miningType
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
            loadUsers(); // Refresh the user list
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('حدث خطأ في الاتصال', 'error');
        console.error('Error:', error);
    }
}

// Copy text to clipboard
function copyText(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('تم نسخ النص بنجاح!', 'success');
    }).catch(function() {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('تم نسخ النص بنجاح!', 'success');
    });
}

// Add fade-in animation to cards
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.mining-card, .stat-card, .donation-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
});

// Load URL History
async function loadUrlHistory() {
    try {
        const response = await fetch('/api/url_history');
        const data = await response.json();

        if (data.success) {
            displayUrlHistory(data.history);
            document.getElementById('urlHistoryContainer').style.display = 'block';
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('حدث خطأ في تحميل السجل', 'error');
        console.error('Error:', error);
    }
}

function displayUrlHistory(history) {
    const tbody = document.getElementById('urlHistoryTable');
    tbody.innerHTML = '';

    if (history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">لا توجد روابط محفوظة</td></tr>';
        return;
    }

    history.reverse().forEach((entry, index) => {
        const row = document.createElement('tr');
        const date = new Date(entry.timestamp).toLocaleString('ar-EG');

        row.innerHTML = `
            <td><span class="badge bg-primary">${entry.mining_type}</span></td>
            <td>${date}</td>
            <td><span class="badge ${entry.status === 'started' ? 'bg-success' : 'bg-secondary'}">${entry.status === 'started' ? 'بدأ' : 'متوقف'}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="copyText('${entry.url}')">
                    <i class="fas fa-copy"></i> نسخ
                </button>
                <button class="btn btn-sm btn-outline-success" onclick="reuseUrl('${entry.mining_type}', '${entry.url}')">
                    <i class="fas fa-redo"></i> إعادة استخدام
                </button>
            </td>
        `;

        tbody.appendChild(row);
    });
}

function reuseUrl(miningType, url) {
    const urlInput = document.getElementById(`${miningType.toLowerCase()}Url`);
    if (urlInput) {
        urlInput.value = url;
        showNotification(`تم تحميل الرابط لـ ${miningType}`, 'success');
    }
}

async function clearUrlHistory() {
    if (!confirm('هل أنت متأكد من مسح جميع الروابط المحفوظة؟')) {
        return;
    }

    try {
        const response = await fetch('/api/clear_url_history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
            loadUrlHistory();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('حدث خطأ في مسح السجل', 'error');
        console.error('Error:', error);
    }
}

// Auto-refresh mining status
setInterval(updateMiningStatus, 30000); // Refresh every 30 seconds

// Operation logs variables
let autoRefreshEnabled = false;
let autoRefreshInterval = null;

// Load Operation Logs
async function loadOperationLogs() {
    try {
        const response = await fetch('/api/operation_logs');
        const data = await response.json();

        if (data.success) {
            displayOperationLogs(data.logs);
        } else {
            showNotification('حدث خطأ في تحميل سجل العمليات', 'error');
            console.error('Error:', data.message);
        }
    } catch (error) {
        showNotification('حدث خطأ في تحميل سجل العمليات', 'error');
        console.error('Error:', error);
    }
}

function displayOperationLogs(logs) {
    const tbody = document.getElementById('operationLogsTable');
    tbody.innerHTML = '';

    if (logs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    <i class="fas fa-info-circle"></i>
                    لا توجد عمليات مسجلة بعد
                </td>
            </tr>
        `;
        return;
    }

    // عرض آخر 20 سجل فقط مرتبة من الأحدث للأقدم
    const recentLogs = logs.slice(-20).reverse();

    recentLogs.forEach((log, index) => {
        const row = document.createElement('tr');
        const date = new Date(log.timestamp).toLocaleString('ar-EG');

        // تحديد لون الحالة
        let statusClass = 'badge ';
        switch(log.status) {
            case 'نجح':
                statusClass += 'bg-success';
                break;
            case 'فشل':
                statusClass += 'bg-danger';
                break;
            case 'جاري':
                statusClass += 'bg-warning text-dark';
                break;
            default:
                statusClass += 'bg-secondary';
        }

        // تقصير النص الطويل
        let details = log.details || '';
        if (details.length > 100) {
            details = details.substring(0, 100) + '...';
        }

        row.innerHTML = `
            <td><small>${date}</small></td>
            <td><span class="badge bg-primary">${log.mining_type}</span></td>
            <td>${log.step}</td>
            <td><span class="${statusClass}">${log.status}</span></td>
            <td><small class="text-muted">${details}</small></td>
        `;

        // إضافة تأثير للسجلات الجديدة
        if (index < 3) {
            row.classList.add('table-warning');
            setTimeout(() => {
                row.classList.remove('table-warning');
            }, 3000);
        }

        tbody.appendChild(row);
    });
}

async function clearOperationLogs() {
    if (!confirm('هل أنت متأكد من مسح سجل العمليات؟')) {
        return;
    }

    try {
        const response = await fetch('/api/clear_operation_logs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            showNotification(data.message, 'success');
            loadOperationLogs();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('حدث خطأ في مسح السجل', 'error');
        console.error('Error:', error);
    }
}

function toggleAutoRefresh() {
    const icon = document.getElementById('autoRefreshIcon');
    const text = document.getElementById('autoRefreshText');

    if (autoRefreshEnabled) {
        // إيقاف التحديث التلقائي
        autoRefreshEnabled = false;
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
        icon.className = 'fas fa-play';
        text.textContent = 'تفعيل التحديث التلقائي';
        showNotification('تم إيقاف التحديث التلقائي', 'info');
    } else {
        // تفعيل التحديث التلقائي
        autoRefreshEnabled = true;
        autoRefreshInterval = setInterval(loadOperationLogs, 5000); // كل 5 ثوان
        icon.className = 'fas fa-pause';
        text.textContent = 'إيقاف التحديث التلقائي';
        showNotification('تم تفعيل التحديث التلقائي', 'success');
    }
}

// Add pulse animation to active mining cards
function addPulseToActiveCards() {
    ['COIN', 'BANAN', 'TRX', 'SHIB', 'BEAMX'].forEach(type => {
        const statusElement = document.getElementById(`${type.toLowerCase()}Status`);
        const card = statusElement.closest('.mining-card');

        if (statusElement.classList.contains('active')) {
            card.classList.add('pulse');
        } else {
            card.classList.remove('pulse');
        }
    });
}

// Call pulse animation update after status update
const originalUpdateMiningStatus = updateMiningStatus;
updateMiningStatus = async function() {
    await originalUpdateMiningStatus();
    addPulseToActiveCards();
};

// تحديث سجل العمليات
function refreshOperationLogs() {
    fetch('/api/operation_logs')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayOperationLogs(data.logs);
            } else {
                showNotification('خطأ في جلب سجل العمليات: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('خطأ:', error);
            showNotification('خطأ في الاتصال', 'error');
        });
}

// تحديث حالة الإعلانات اليومية
function refreshDailyAdsStatus() {
    const statusContainer = document.getElementById('dailyAdsStatus');
    statusContainer.innerHTML = '<div class="text-center text-muted"><i class="fas fa-spinner fa-spin"></i> جاري التحديث...</div>';

    fetch('/api/daily_ads_status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayDailyAdsStatus(data.status);
                document.getElementById('lastUpdateTime').textContent = new Date().toLocaleString('ar-EG');
            } else {
                statusContainer.innerHTML = '<div class="alert alert-danger">خطأ في جلب البيانات: ' + data.message + '</div>';
            }
        })
        .catch(error => {
            console.error('خطأ:', error);
            statusContainer.innerHTML = '<div class="alert alert-danger">خطأ في الاتصال</div>';
        });
}

// عرض حالة الإعلانات اليومية
function displayDailyAdsStatus(status) {
    const container = document.getElementById('dailyAdsStatus');
    let html = '';

    const miningTypes = {
        'COIN': { emoji: '🪙', name: 'COIN' },
        'BANAN': { emoji: '🍌', name: 'BANAN' },
        'TRX': { emoji: '🔷', name: 'TRX' },
        'SHIB': { emoji: '🐕', name: 'SHIB' },
        'BEAMX': { emoji: '⚡', name: 'BEAMX' }
    };

    for (const [type, info] of Object.entries(miningTypes)) {
        const data = status[type] || {};
        const completed = data.completed || 0;
        const maxDaily = data.max_daily || 0;
        const remaining = data.remaining || 0;
        const percentage = data.percentage || 0;
        const isMaxed = data.is_maxed || false;
        const error = data.error || null;

        let progressBarClass = 'bg-success';
        let statusText = 'نشط';
        let statusClass = 'text-success';

        if (isMaxed) {
            progressBarClass = 'bg-danger';
            statusText = 'مكتمل';
            statusClass = 'text-danger';
        } else if (percentage > 80) {
            progressBarClass = 'bg-warning';
            statusText = 'قريب من الانتهاء';
            statusClass = 'text-warning';
        }

        html += `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-2">
                            <span class="fs-4 me-2">${info.emoji}</span>
                            <h6 class="card-title mb-0">${info.name}</h6>
                        </div>

                        ${error ? `
                            <div class="alert alert-warning py-2 mb-2 small">${error}</div>
                        ` : ''}

                        <div class="mb-2">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <small class="text-muted">الإعلانات:</small>
                                <small class="${statusClass} fw-bold">${statusText}</small>
                            </div>
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar ${progressBarClass}" 
                                     style="width: ${percentage}%"></div>
                            </div>
                        </div>

                        <div class="row text-center">
                            <div class="col-4">
                                <div class="small text-muted">مكتمل</div>
                                <div class="fw-bold text-primary">${completed}</div>
                            </div>
                            <div class="col-4">
                                <div class="small text-muted">المتبقي</div>
                                <div class="fw-bold text-info">${remaining}</div>
                            </div>
                            <div class="col-4">
                                <div class="small text-muted">الإجمالي</div>
                                <div class="fw-bold text-secondary">${maxDaily}</div>
                            </div>
                        </div>

                        <div class="mt-2 text-center">
                            <small class="text-muted">${percentage}% مكتمل</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}

// تحديث حالة التعدين كل 30 ثانية
document.addEventListener('DOMContentLoaded', function() {
    updateMiningStatus();
    loadUrlHistory();
    loadOperationLogs();
    refreshDailyAdsStatus();
    setInterval(updateMiningStatus, 30000);

// تحديث سجل العمليات كل 5 ثواني
    setInterval(updateOperationLogs, 5000);

// تحديث سجل العمليات عند تحميل الصفحة
    updateOperationLogs();
});

// تحديث دوري للحالة
setInterval(() => {
    updateMiningStatus();
    refreshOperationLogs();
    refreshDailyAdsStatus(); // تحديث حالة الإعلانات كل 10 ثواني
}, 10000); // كل 10 ثواني

// تحميل البيانات عند بدء الصفحة
document.addEventListener('DOMContentLoaded', function() {
    updateMiningStatus();
    loadUrlHistory();
    loadOperationLogs();
    refreshDailyAdsStatus(); // تحميل حالة الإعلانات عند بدء الصفحة
});