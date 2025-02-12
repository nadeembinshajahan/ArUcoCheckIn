// Fetch and update dashboard data
function updateDashboard() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            // Update statistics cards
            document.querySelector('#totalVisitors').textContent = data.total_visitors;
            document.querySelector('#activeCameras').textContent = data.active_cameras;
            document.querySelector('#avgTimeSpent').textContent = `${data.avg_time} min`;
            document.querySelector('#popularArtwork').textContent = data.popular_artwork || 'N/A';

            // Update recent observations table
            const tbody = document.querySelector('#recentObservations tbody');
            tbody.innerHTML = data.recent_observations.map(obs => `
                <tr>
                    <td>${obs.aruco_id}</td>
                    <td>${obs.artwork_id}</td>
                    <td>${obs.time_spent}</td>
                    <td>${obs.sections}</td>
                    <td>${obs.timestamp}</td>
                </tr>
            `).join('');

            // Update time per section chart
            if (window.timeChart) {
                // Calculate average time per section across all observations
                const sectionTimes = data.recent_observations.reduce((acc, obs) => {
                    const sections = obs.sections.split(', ').map(Number);
                    sections.forEach(section => {
                        acc[section - 1] = (acc[section - 1] || 0) + parseFloat(obs.time_spent);
                    });
                    return acc;
                }, [0, 0, 0]).map(time => time / data.recent_observations.length);

                window.timeChart.data.datasets[0].data = sectionTimes;
                window.timeChart.update();
            }

            // Update visitor flow chart if exists
            if (window.flowChart) {
                // Get hourly visitor counts
                const hours = ['9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM'];
                const visitorCounts = hours.map(() => Math.floor(Math.random() * 50 + 10)); // Mock data for now

                window.flowChart.data.datasets[0].data = visitorCounts;
                window.flowChart.update();
            }
        })
        .catch(error => console.error('Error updating dashboard:', error));
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

    // Update dashboard every 30 seconds
    updateDashboard();
    setInterval(updateDashboard, 30000);
});