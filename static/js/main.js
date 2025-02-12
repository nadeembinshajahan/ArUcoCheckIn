let currentArucoId = null;
let currentCheckinId = null;
let currentStatus = null;

function updateStatus(message, type = 'info') {
    const statusDiv = document.getElementById('status');
    statusDiv.className = `alert alert-${type}`;
    statusDiv.textContent = message;
}

function updateButtons(status, arucoId, checkinId) {
    const checkinBtn = document.getElementById('checkinBtn');
    const checkoutBtn = document.getElementById('checkoutBtn');

    checkinBtn.style.display = 'none';
    checkoutBtn.style.display = 'none';

    if (status === 'can_checkin') {
        checkinBtn.style.display = 'block';
        checkinBtn.disabled = false;
    } else if (status === 'can_checkout') {
        checkoutBtn.style.display = 'block';
        checkoutBtn.disabled = false;
    }

    currentArucoId = arucoId;
    currentCheckinId = checkinId;
    currentStatus = status;
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
                        ${entry.is_checked_out ? 
                            `<span class="badge bg-danger">Checked Out</span>` : 
                            `<span class="badge bg-success">Checked In</span>`
                        }
                    </div>
                    <div class="text-end">
                        <small class="text-muted">In: ${entry.check_in_time}</small>
                        ${entry.check_out_time ? 
                            `<br><small class="text-muted">Out: ${entry.check_out_time}</small>` : 
                            ''
                        }
                    </div>
                </div>
            `).join('');
        });
}

function checkAruco() {
    fetch('/check_aruco')
        .then(response => response.json())
        .then(data => {
            if (data.detected && data.aruco_id) {
                if (data.status === 'can_checkin') {
                    updateStatus(`ArUco code ${data.aruco_id} detected! Ready for check-in.`, 'success');
                    updateButtons('can_checkin', data.aruco_id);
                } else if (data.status === 'can_checkout') {
                    updateStatus(`ArUco code ${data.aruco_id} can now check out.`, 'warning');
                    updateButtons('can_checkout', data.aruco_id, data.checkin_id);
                } else if (data.status === 'already_checked_in') {
                    updateStatus(`ArUco code ${data.aruco_id} is already checked in.`, 'info');
                    updateButtons('already_checked_in', data.aruco_id);
                }
            } else {
                updateStatus('Position ArUco code in the center box...', 'info');
                updateButtons(null, null);
            }
        });
}

document.getElementById('checkinBtn').addEventListener('click', () => {
    if (!currentArucoId) return;

    fetch(`/checkin/${currentArucoId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatus(`Check-in successful for ArUco ${currentArucoId}!`, 'success');
                updateHistory();
                setTimeout(() => {
                    updateStatus('Position ArUco code in the center box...', 'info');
                    updateButtons(null, null);
                }, 2000);
            } else {
                updateStatus(data.message, 'danger');
            }
        });
});

document.getElementById('checkoutBtn').addEventListener('click', () => {
    if (!currentCheckinId) return;

    fetch(`/checkout/${currentCheckinId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatus(`Check-out successful!`, 'success');
                updateHistory();
                setTimeout(() => {
                    updateStatus('Position ArUco code in the center box...', 'info');
                    updateButtons(null, null);
                }, 2000);
            } else {
                updateStatus(data.message, 'danger');
            }
        });
});

// Start periodic checks
setInterval(checkAruco, 1000);
updateHistory();