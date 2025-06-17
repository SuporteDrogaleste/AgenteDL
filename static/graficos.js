// graficos.js

window.gerarGraficoCPU = function () {
    const canvas = document.getElementById('graficoCPU');
    if (!canvas) return alert("Canvas graficoCPU não encontrado.");
    const ctx = canvas.getContext('2d');

    const labels = JSON.parse(canvas.dataset.labels);
    const dados = JSON.parse(canvas.dataset.cpu);

    if (window.graficoCPU) window.graficoCPU.destroy();

    window.graficoCPU = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.slice().reverse(),
            datasets: [{
                label: 'Uso de CPU (%)',
                data: dados.slice().reverse(),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true, max: 100 } }
        }
    });
}

window.gerarGraficoRAM = function () {
    const canvas = document.getElementById('graficoRAM');
    if (!canvas) return alert("Canvas graficoRAM não encontrado.");
    const ctx = canvas.getContext('2d');

    const labels = JSON.parse(canvas.dataset.labels);
    const dados = JSON.parse(canvas.dataset.ram);

    if (window.graficoRAM) window.graficoRAM.destroy();

    window.graficoRAM = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.slice().reverse(),
            datasets: [{
                label: 'Uso de RAM (%)',
                data: dados.slice().reverse(),
                backgroundColor: 'rgba(255, 159, 64, 0.6)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true, max: 100 } }
        }
    });
}
