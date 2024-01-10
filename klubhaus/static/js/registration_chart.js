const dataset = JSON.parse(document.getElementById('registration-data').textContent);
const ctx = document.getElementById('registration-chart');

new Chart(ctx, {
    type: 'bar',
    data: {
        labels: dataset.labels,
        datasets: [{
            label: 'Downloads',
            data: dataset.data,
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true,
                grace: '5%',
                ticks: {
                    stepSize: 1
                }
            },
            x: {
                grid: {
                    drawOnChartArea: false
                }
            }
        }
    }
});
