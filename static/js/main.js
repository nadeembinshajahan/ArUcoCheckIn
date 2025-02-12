let currentArucoId = null;

function updateStatus(message, type = 'info') {
    const statusDiv = document.getElementById('status');
    statusDiv.className = `alert alert-${type}`;
    statusDiv.textContent = message;
}

function updateCheckInButton(enabled) {
    const button = document.getElementById('checkinBtn');
    button.disabled = !enabled;
}

function updateHistory() {
    fetch('/get_history')
        .then(response => response.json())
        .then(history => {
            const historyDiv = document.getElementById('history');
            historyDiv.innerHTML = history.map(entry => `
                <div class="history-item">
                    <span class="badge bg-secondary">${entry.aruco_id}</span>
                    <small class="text-muted">${entry.timestamp}</small>
                </div>
            `).join('');
        });
}

function checkAruco() {
    fetch('/check_aruco')
        .then(response => response.json())
        .then(data => {
            if (data.detected && data.aruco_id) {
                updateStatus(`ArUco code ${data.aruco_id} detected! Ready for check-in.`, 'success');
                updateCheckInButton(true);
                currentArucoId = data.aruco_id;
            } else {
                updateStatus('Position ArUco code in the center box...', 'info');
                updateCheckInButton(false);
                currentArucoId = null;
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
                    updateCheckInButton(false);
                }, 2000);
            }
        });
});

// Start periodic checks
setInterval(checkAruco, 1000);
updateHistory();