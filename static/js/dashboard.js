// Mock data for charts
const timePerSectionData = {
    labels: ['Section 1', 'Section 2', 'Section 3'],
    datasets: [{
        label: 'Average Time Spent (minutes)',
        data: [2.5, 5.2, 3.8],
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
};

const visitorFlowData = {
    labels: ['9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM'],
    datasets: [{
        label: 'Number of Visitors',
        data: [10, 25, 45, 30, 55, 40, 35],
        fill: true,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
    }]
};

// Initialize charts
document.addEventListener('DOMContentLoaded', function() {
    // Time per section chart
    const timeCtx = document.getElementById('timePerSectionChart').getContext('2d');
    new Chart(timeCtx, {
        type: 'bar',
        data: timePerSectionData,
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
    new Chart(flowCtx, {
        type: 'line',
        data: visitorFlowData,
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
});
