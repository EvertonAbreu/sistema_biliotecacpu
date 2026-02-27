// Configurações e funções para relatórios

// Dados para os gráficos (serão preenchidos pelo Django)
const chartData = {
  meses: JSON.parse(document.getElementById('chart-data').dataset.meses || '[]'),
  valores: JSON.parse(document.getElementById('chart-data').dataset.valores || '[]'),
  categoriasLabels: JSON.parse(document.getElementById('chart-data').dataset.categoriasLabels || '[]'),
  categoriasValues: JSON.parse(document.getElementById('chart-data').dataset.categoriasValues || '[]')
};

// Cores para gráficos
const chartColors = {
  primary: 'rgba(54, 162, 235, 1)',
  primaryLight: 'rgba(54, 162, 235, 0.2)',
  secondary: 'rgba(255, 99, 132, 1)',
  secondaryLight: 'rgba(255, 99, 132, 0.2)',
  success: 'rgba(75, 192, 192, 1)',
  successLight: 'rgba(75, 192, 192, 0.2)',
  warning: 'rgba(255, 159, 64, 1)',
  warningLight: 'rgba(255, 159, 64, 0.2)',
  info: 'rgba(153, 102, 255, 1)',
  infoLight: 'rgba(153, 102, 255, 0.2)'
};

// Array de cores para gráfico de pizza
const pieChartColors = [
  '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
  '#9966FF', '#FF9F40', '#C9CBCF', '#7FFFD4',
  '#FF6B6B', '#51CF66', '#FFD43B', '#228BE6'
];

// Instâncias dos gráficos
let emprestimosChart = null;
let categoriasChart = null;

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
  initializeCharts();
  initializeEventListeners();
  initializeTooltips();
});

// Função para inicializar os gráficos
function initializeCharts() {
  // Gráfico de Empréstimos por Mês
  const ctxEmprestimos = document.getElementById('chart-emprestimos');
  if (ctxEmprestimos) {
    emprestimosChart = new Chart(ctxEmprestimos.getContext('2d'), {
      type: 'line',
      data: {
        labels: chartData.meses,
        datasets: [{
          label: 'Empréstimos',
          data: chartData.valores,
          backgroundColor: chartColors.primaryLight,
          borderColor: chartColors.primary,
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: chartColors.primary,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              font: {
                size: 14,
                family: "'Segoe UI', Roboto, 'Helvetica Neue', Arial"
              },
              color: '#495057'
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            titleFont: {
              size: 14
            },
            bodyFont: {
              size: 13
            },
            padding: 12,
            cornerRadius: 6
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              font: {
                size: 12
              }
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              font: {
                size: 12
              }
            },
            grid: {
              borderDash: [2, 2]
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        },
        animations: {
          tension: {
            duration: 1000,
            easing: 'linear'
          }
        }
      }
    });
  }

  // Gráfico de Pizza para Categorias
  const ctxCategorias = document.getElementById('chart-categorias');
  if (ctxCategorias && chartData.categoriasLabels.length > 0) {
    categoriasChart = new Chart(ctxCategorias.getContext('2d'), {
      type: 'pie',
      data: {
        labels: chartData.categoriasLabels,
        datasets: [{
          data: chartData.categoriasValues,
          backgroundColor: pieChartColors,
          borderColor: '#fff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'right',
            labels: {
              font: {
                size: 12
              },
              padding: 20
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = context.raw || 0;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = Math.round((value / total) * 100);
                return `${label}: ${value} (${percentage}%)`;
              }
            }
          }
        }
      }
    });
  }
}

// Função para inicializar event listeners
function initializeEventListeners() {
  // Filtros de período
  const periodoSelect = document.getElementById('periodo');
  if (periodoSelect) {
    periodoSelect.addEventListener('change', function() {
      applyFilters();
    });
  }

  // Botões de exportação
  document.querySelectorAll('.export-btn').forEach(button => {
    button.addEventListener('click', function(e) {
      const action = this.dataset.action;
      handleExport(action);
    });
  });

  // Botão de imprimir
  const printBtn = document.getElementById('print-btn');
  if (printBtn) {
    printBtn.addEventListener('click', function() {
      window.print();
    });
  }

  // Atualizar gráfico ao redimensionar janela
  window.addEventListener('resize', debounce(function() {
    if (emprestimosChart) emprestimosChart.resize();
    if (categoriasChart) categoriasChart.resize();
  }, 250));
}

// Função para aplicar filtros
function applyFilters() {
  const form = document.querySelector('form[method="get"]');
  if (form) {
    form.submit();
  }
}

// Função para exportar dados
function handleExport(type) {
  switch(type) {
    case 'excel':
      exportToExcel();
      break;
    case 'pdf':
      exportToPDF();
      break;
    case 'print':
      window.print();
      break;
    default:
      console.warn('Tipo de exportação não suportado:', type);
  }
}

// Exportar para Excel (simulação)
function exportToExcel() {
  showNotification('Preparando exportação para Excel...', 'info');
  
  // Em produção, aqui você faria uma requisição para o servidor
  setTimeout(() => {
    showNotification('Arquivo Excel gerado com sucesso!', 'success');
    // Simular download
    // window.location.href = '/api/relatorios/exportar/excel/';
  }, 1000);
}

// Exportar para PDF (simulação)
function exportToPDF() {
  showNotification('Gerando relatório em PDF...', 'info');
  
  setTimeout(() => {
    showNotification('PDF gerado com sucesso!', 'success');
    // Simular download
    // window.location.href = '/api/relatorios/exportar/pdf/';
  }, 1500);
}

// Função auxiliar para debounce
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Função para mostrar notificações
function showNotification(message, type = 'info') {
  // Criar elemento de notificação
  const notification = document.createElement('div');
  notification.className = `alert alert-${type} alert-dismissible fade show notification-alert`;
  notification.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  // Adicionar ao documento
  const container = document.querySelector('.notification-container') || createNotificationContainer();
  container.appendChild(notification);
  
  // Remover automaticamente após 5 segundos
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 5000);
}

// Criar container para notificações
function createNotificationContainer() {
  const container = document.createElement('div');
  container.className = 'notification-container';
  container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; width: 300px;';
  document.body.appendChild(container);
  return container;
}

// Inicializar tooltips do Bootstrap
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

// Função para atualizar dados dinamicamente (se necessário)
function updateChartData(newData) {
  if (emprestimosChart && newData.meses && newData.valores) {
    emprestimosChart.data.labels = newData.meses;
    emprestimosChart.data.datasets[0].data = newData.valores;
    emprestimosChart.update();
  }
}

// Função para baixar dados como CSV
function downloadCSV(data, filename) {
  const csvContent = "data:text/csv;charset=utf-8," + data;
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Expor funções para uso global (se necessário)
window.relatorios = {
  updateChartData,
  exportToExcel,
  exportToPDF
};