// Fetch and update dashboard data
function updateDashboard() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error from server:', data.error);
                return;
            }

            // Update statistics cards
            document.querySelector('#totalVisitors').textContent = data.total_visitors || '0';
            document.querySelector('#activeCameras').textContent = data.active_cameras || '0';
            document.querySelector('#avgTimeSpent').textContent = `${data.avg_time || '0'} min`;
            document.querySelector('#popularArtwork').textContent = data.popular_artwork || 'N/A';

            // Update recent observations table
            const tbody = document.querySelector('#recentObservations');
            if (data.recent_observations && data.recent_observations.length > 0) {
                tbody.innerHTML = data.recent_observations.map(obs => `
                    <tr>
                        <td>${obs.aruco_id || 'Unknown'}</td>
                        <td>${obs.artwork_id || 'Unknown'}</td>
                        <td>${obs.time_spent || '0 min'}</td>
                        <td>${obs.sections || 'None'}</td>
                        <td>${obs.timestamp || 'N/A'}</td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No recent observations</td></tr>';
            }

            // Update time per section chart
            if (window.timeChart) {
                const sectionTimes = [
                    data.section_times?.section_1 || 0,
                    data.section_times?.section_2 || 0,
                    data.section_times?.section_3 || 0
                ];
                window.timeChart.data.datasets[0].data = sectionTimes;
                window.timeChart.update();
            }

            // Update visitor flow chart with real data if available
            if (window.flowChart && data.recent_observations) {
                const hourCounts = new Array(7).fill(0); // 9 AM to 3 PM
                data.recent_observations.forEach(obs => {
                    const hour = new Date(obs.timestamp).getHours();
                    const index = hour - 9; // 9 AM is index 0
                    if (index >= 0 && index < 7) {
                        hourCounts[index]++;
                    }
                });
                window.flowChart.data.datasets[0].data = hourCounts;
                window.flowChart.update();
            }
        })
        .catch(error => {
            console.error('Error updating dashboard:', error);
            // Handle error state in UI
            document.querySelector('#totalVisitors').textContent = '0';
            document.querySelector('#activeCameras').textContent = '0';
            document.querySelector('#avgTimeSpent').textContent = '0 min';
            document.querySelector('#popularArtwork').textContent = 'N/A';

            const tbody = document.querySelector('#recentObservations');
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">Failed to load data</td></tr>';
        });
}

// Initialize charts when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Time per section chart
    const timeCtx = document.getElementById('timePerSectionChart').getContext('2d');
    window.timeChart = new Chart(timeCtx, {
        type: 'bar',
        data: {
            labels: ['Section 1', 'Section 2', 'Section 3'],
            datasets: [{
                label: 'Average Time Spent (minutes)',
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Minutes'
                    }
                }
            }
        }
    });

    // Visitor flow chart
    const flowCtx = document.getElementById('visitorFlowChart').getContext('2d');
    window.flowChart = new Chart(flowCtx, {
        type: 'line',
        data: {
            labels: ['9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM'],
            datasets: [{
                label: 'Number of Visitors',
                data: [0, 0, 0, 0, 0, 0, 0],
                fill: true,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Visitors'
                    }
                }
            }
        }
    });

    // Update dashboard immediately and then every 30 seconds
    updateDashboard();
    setInterval(updateDashboard, 30000);
});