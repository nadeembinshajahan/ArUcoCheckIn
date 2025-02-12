let currentArucoId = null;
let currentStatus = null;

function updateStatus(message, type = 'info') {
    const statusDiv = document.getElementById('status');
    statusDiv.className = `alert alert-${type}`;
    statusDiv.textContent = message;
}

function updateActionButton(enabled, isCheckout = false) {
    const button = document.getElementById('checkinBtn');
    button.disabled = !enabled;
    button.textContent = isCheckout ? 'Check Out' : 'Check In';
    button.className = `btn ${isCheckout ? 'btn-warning' : 'btn-primary'} w-100 mb-3`;
}

function updateHistory() {
    fetch('/get_history')
        .then(response => response.json())
        .then(history => {
            const historyDiv = document.getElementById('history');
            historyDiv.innerHTML = history.map(entry => `
                <div class="history-item">
                    <div>
                        <span class="badge bg-secondary">${entry.aruco_id}</span>
                        <span class="badge ${entry.status === 'checked_in' ? 'bg-success' : 'bg-warning'}">
                            ${entry.status === 'checked_in' ? 'In' : 'Out'}
                        </span>
                    </div>
                    <small class="text-muted">
                        ${entry.status === 'checked_in' ? entry.timestamp : 
                          `${entry.timestamp} - ${entry.checkout_time}`}
                    </small>
                </div>
            `).join('');
        });
}

function checkAruco() {
    fetch('/check_aruco')
        .then(response => response.json())
        .then(data => {
            if (data.detected && data.aruco_id) {
                currentArucoId = data.aruco_id;
                currentStatus = data.status;

                if (data.status === 'can_checkin') {
                    updateStatus(`ArUco code ${data.aruco_id} detected! Ready for check-in.`, 'success');
                    updateActionButton(true, false);
                } else if (data.status === 'can_checkout') {
                    updateStatus(`ArUco code ${data.aruco_id} is checked in. You can check out.`, 'warning');
                    updateActionButton(true, true);
                } else if (data.status === 'cooldown') {
                    updateStatus(`Please wait before checking in ArUco ${data.aruco_id} again.`, 'info');
                    updateActionButton(false);
                }
            } else {
                updateStatus('Position ArUco code in the center box...', 'info');
                updateActionButton(false);
                currentArucoId = null;
                currentStatus = null;
            }
        });
}

document.getElementById('checkinBtn').addEventListener('click', () => {
    if (!currentArucoId) return;

    const endpoint = currentStatus === 'can_checkout' ? 'checkout' : 'checkin';

    fetch(`/${endpoint}/${currentArucoId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const action = endpoint === 'checkout' ? 'out' : 'in';
                updateStatus(`Check-${action} successful for ArUco ${currentArucoId}!`, 'success');
                updateHistory();
                setTimeout(() => {
                    updateStatus('Position ArUco code in the center box...', 'info');
                    updateActionButton(false);
                }, 2000);
            } else {
                updateStatus(data.error || 'Operation failed', 'danger');
            }
        });
});

// Start periodic checks
setInterval(checkAruco, 1000);
updateHistory();