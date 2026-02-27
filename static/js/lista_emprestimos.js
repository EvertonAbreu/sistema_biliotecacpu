/**
 * Lista de Empréstimos Ativos - Funcionalidades Específicas
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Lista de Empréstimos carregada');
    
    // Elementos principais
    const table = document.getElementById('emprestimosTable');
    const searchInput = document.getElementById('searchInput');
    const filterButtons = document.querySelectorAll('.btn-filter');
    const statNumbers = document.querySelectorAll('.stat-number');
    const countHoje = document.getElementById('count-hoje');
    const modalDetalhes = document.getElementById('modalDetalhesEmprestimo');
    const btnDetalhes = document.querySelectorAll('.btn-detalhes');
    
    let emprestimosHoje = 0;
    
    // ===== INICIALIZAÇÃO =====
    function init() {
        animateStatistics();
        countEmprestimosVencendoHoje();
        setupEventListeners();
        setupDataTable();
        
        console.log('Lista de Empréstimos inicializada com sucesso!');
    }
    
    // ===== ANIMAÇÃO DAS ESTATÍSTICAS =====
    function animateStatistics() {
        statNumbers.forEach(element => {
            const text = element.textContent.trim();
            const number = parseInt(text);
            
            if (!isNaN(number) && number > 0) {
                animateCounter(element, number);
            }
        });
    }
    
    function animateCounter(element, finalValue) {
        let startValue = 0;
        const duration = 1000;
        const increment = finalValue / (duration / 16);
        
        const timer = setInterval(() => {
            startValue += increment;
            if (startValue >= finalValue) {
                element.textContent = finalValue.toLocaleString('pt-BR');
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(startValue).toLocaleString('pt-BR');
            }
        }, 16);
    }
    
    // ===== CONTAR EMPRÉSTIMOS VENCENDO HOJE =====
    function countEmprestimosVencendoHoje() {
        if (!table) return;
        
        const hoje = new Date().toISOString().split('T')[0];
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const dataDevolucao = row.dataset.devolucao;
            if (dataDevolucao === hoje) {
                emprestimosHoje++;
                
                // Adicionar animação de piscar para empréstimos que vencem hoje
                const statusBadge = row.querySelector('.badge-status.alerta');
                if (statusBadge) {
                    statusBadge.classList.add('blink');
                }
            }
        });
        
        if (countHoje) {
            animateCounter(countHoje, emprestimosHoje);
        }
    }
    
    // ===== FILTRAGEM DE EMPRÉSTIMOS =====
    function filtrarEmprestimos(filter) {
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        const hoje = new Date().toISOString().split('T')[0];
        const amanha = new Date();
        amanha.setDate(amanha.getDate() + 1);
        const amanhaStr = amanha.toISOString().split('T')[0];
        
        rows.forEach(row => {
            const status = row.dataset.status;
            const dataDevolucao = row.dataset.devolucao;
            let mostrar = true;
            
            switch (filter) {
                case 'all':
                    mostrar = true;
                    break;
                case 'prazo':
                    mostrar = status === 'prazo';
                    break;
                case 'atrasado':
                    mostrar = status === 'atrasado';
                    break;
                case 'hoje':
                    mostrar = dataDevolucao === hoje;
                    break;
                case 'amanha':
                    mostrar = dataDevolucao === amanhaStr;
                    break;
            }
            
            // Aplicar filtro
            if (mostrar) {
                row.style.display = '';
                row.classList.add('fade-in');
            } else {
                row.style.display = 'none';
                row.classList.remove('fade-in');
            }
        });
        
        // Atualizar contador
        atualizarContadorEmprestimos();
    }
    
    function atualizarContadorEmprestimos() {
        if (!table) return;
        
        const rowsVisible = table.querySelectorAll('tbody tr:not([style*="display: none"])').length;
        const contador = document.querySelector('.card-title .badge');
        
        if (contador) {
            contador.textContent = `${rowsVisible} empréstimo${rowsVisible !== 1 ? 's' : ''}`;
        }
    }
    
    // ===== BUSCA EM TEMPO REAL =====
    function setupSearch() {
        if (!searchInput || !table) return;
        
        searchInput.addEventListener('input', function() {
            const termo = this.value.toLowerCase().trim();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const searchData = row.dataset.search || '';
                const texto = row.textContent.toLowerCase();
                
                if (searchData.includes(termo) || texto.includes(termo)) {
                    row.style.display = '';
                    row.classList.add('fade-in');
                } else {
                    row.style.display = 'none';
                    row.classList.remove('fade-in');
                }
            });
            
            atualizarContadorEmprestimos();
        });
    }
    
    // ===== DETALHES DO EMPRÉSTIMO =====
    function carregarDetalhesEmprestimo(emprestimoId) {
        // Mostrar loading no modal
        const conteudoModal = document.getElementById('conteudoDetalhesEmprestimo');
        conteudoModal.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-3 text-muted">Carregando detalhes do empréstimo...</p>
            </div>
        `;
        
        // Fazer requisição AJAX
        fetch(`/api/emprestimo/${emprestimoId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Empréstimo não encontrado');
                }
                return response.json();
            })
            .then(data => {
                exibirDetalhesEmprestimo(data);
            })
            .catch(error => {
                console.error('Erro:', error);
                conteudoModal.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Erro ao carregar detalhes: ${error.message}
                    </div>
                `;
            });
    }
    
    function exibirDetalhesEmprestimo(emprestimo) {
        const conteudoModal = document.getElementById('conteudoDetalhesEmprestimo');
        
        // Calcular status
        let statusClass = 'prazo';
        let statusText = 'No Prazo';
        let statusIcon = 'check-circle';
        
        if (emprestimo.status_exibicao === 'Atrasado') {
            statusClass = 'atrasado';
            statusText = 'Atrasado';
            statusIcon = 'exclamation-triangle';
        } else if (emprestimo.dias_restantes === 0) {
            statusClass = 'alerta';
            statusText = 'Vence Hoje';
            statusIcon = 'exclamation-circle';
        } else if (emprestimo.dias_restantes <= 3) {
            statusClass = 'alerta';
            statusText = 'Vencendo';
            statusIcon = 'exclamation-circle';
        }
        
        conteudoModal.innerHTML = `
            <div class="row">
                <!-- Informações do Empréstimo -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header bg-light">
                            <strong><i class="fas fa-info-circle me-2"></i>Informações do Empréstimo</strong>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="small text-muted d-block">Código</label>
                                <strong>#${emprestimo.id}</strong>
                            </div>
                            <div class="mb-3">
                                <label class="small text-muted d-block">Data do Empréstimo</label>
                                <strong>${emprestimo.data_emprestimo_formatada}</strong>
                            </div>
                            <div class="mb-3">
                                <label class="small text-muted d-block">Previsão de Devolução</label>
                                <strong>${emprestimo.data_devolucao_formatada}</strong>
                            </div>
                            <div>
                                <label class="small text-muted d-block">Status</label>
                                <span class="badge-status ${statusClass}">
                                    <i class="fas fa-${statusIcon} me-1"></i>${statusText}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Informações do Livro -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header bg-light">
                            <strong><i class="fas fa-book me-2"></i>Livro Emprestado</strong>
                        </div>
                        <div class="card-body">
                            <div class="d-flex align-items-start mb-3">
                                <div class="book-icon me-3">
                                    <i class="fas fa-book text-primary"></i>
                                </div>
                                <div>
                                    <h6 class="mb-1">${emprestimo.livro.titulo}</h6>
                                    <p class="text-muted mb-1">${emprestimo.livro.autor}</p>
                                    <small class="text-muted">${emprestimo.livro.editora} • ${emprestimo.livro.ano_publicacao}</small>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-6">
                                    <label class="small text-muted d-block">Categoria</label>
                                    <span class="badge bg-secondary">${emprestimo.livro.categoria_display}</span>
                                </div>
                                <div class="col-6">
                                    <label class="small text-muted d-block">Prateleira</label>
                                    <span class="badge bg-info">${emprestimo.livro.prateleira}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Informações do Usuário -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header bg-light">
                            <strong><i class="fas fa-user me-2"></i>Usuário</strong>
                        </div>
                        <div class="card-body">
                            <div class="d-flex align-items-start mb-3">
                                <div class="user-avatar me-3">
                                    <i class="fas fa-user text-secondary"></i>
                                </div>
                                <div>
                                    <h6 class="mb-1">${emprestimo.usuario.nome_completo}</h6>
                                    <p class="text-muted mb-1">${emprestimo.usuario.email}</p>
                                    <small class="text-muted">${emprestimo.usuario.categoria}</small>
                                </div>
                            </div>
                            ${emprestimo.usuario.whatsapp ? `
                            <div>
                                <label class="small text-muted d-block">WhatsApp</label>
                                <strong>${emprestimo.usuario.whatsapp}</strong>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
                
                <!-- Detalhes de Tempo -->
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header bg-light">
                            <strong><i class="fas fa-clock me-2"></i>Tempo Restante</strong>
                        </div>
                        <div class="card-body">
                            ${emprestimo.dias_atraso > 0 ? `
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                <strong>Em atraso há ${emprestimo.dias_atraso} dia${emprestimo.dias_atraso !== 1 ? 's' : ''}</strong>
                            </div>
                            ` : ''}
                            
                            <div class="text-center py-3">
                                ${emprestimo.dias_restantes >= 0 ? `
                                <div class="display-4 ${emprestimo.dias_restantes <= 3 ? 'text-warning' : 'text-success'}">
                                    ${emprestimo.dias_restantes}
                                </div>
                                <p class="text-muted mb-0">dias restantes</p>
                                ` : `
                                <div class="display-4 text-secondary">-</div>
                                <p class="text-muted mb-0">sem data definida</p>
                                `}
                            </div>
                            
                            ${emprestimo.data_devolucao_prevista ? `
                            <div class="progress mt-3" style="height: 10px">
                                <div class="progress-bar ${emprestimo.dias_atraso > 0 ? 'bg-danger' : emprestimo.dias_restantes <= 3 ? 'bg-warning' : 'bg-success'}" 
                                     style="width: ${Math.min(100, (emprestimo.dias_passados / emprestimo.total_dias) * 100)}%">
                                </div>
                            </div>
                            <div class="d-flex justify-content-between small mt-2">
                                <span>Empréstimo</span>
                                <span>Devolução</span>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // ===== NOTIFICAÇÃO VIA WHATSAPP =====
    function enviarNotificacao(emprestimoId) {
        showLoading();
        
        fetch('/api/whatsapp/notificar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ emprestimo_id: emprestimoId })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.status === 'success') {
                showAlert('Notificação enviada com sucesso!', 'success');
            } else {
                showAlert('Erro: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            hideLoading();
            showAlert('Erro ao enviar notificação', 'danger');
            console.error('Error:', error);
        });
    }
    
    // ===== EXPORTAR PARA EXCEL =====
    function exportToExcel() {
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr:not([style*="display: none"])');
        let csvContent = "ID,Livro,Autor,Usuário,Email,Data Empréstimo,Previsão Devolução,Status,Dias\n";
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            const dados = [];
            
            // ID
            dados.push(`"${cells[0].textContent.trim().replace('#', '')}"`);
            
            // Livro e Autor
            const livroInfo = cells[1].textContent.trim().split('\n');
            dados.push(`"${livroInfo[0]}"`);
            dados.push(`"${livroInfo[1] ? livroInfo[1].trim() : ''}"`);
            
            // Usuário e Email
            const usuarioInfo = cells[2].textContent.trim().split('\n');
            dados.push(`"${usuarioInfo[0]}"`);
            dados.push(`"${usuarioInfo[1] ? usuarioInfo[1].trim() : ''}"`);
            
            // Datas
            dados.push(`"${cells[3].textContent.trim()}"`);
            dados.push(`"${cells[4].textContent.trim()}"`);
            
            // Status
            dados.push(`"${cells[5].textContent.trim()}"`);
            
            // Dias
            dados.push(`"${cells[6].textContent.trim()}"`);
            
            csvContent += dados.join(',') + '\n';
        });
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `emprestimos_ativos_${new Date().toISOString().slice(0,10)}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showAlert('Exportação concluída!', 'success');
    }
    
    // ===== CONFIRMAÇÃO DE DEVOLUÇÃO =====
    function confirmDevolucao(form) {
        return confirm('Tem certeza que deseja registrar a devolução deste livro?');
    }
    
    // ===== ATUALIZAR TABELA =====
    function refreshTable() {
        showLoading();
        
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }
    
    // ===== DATATABLE CONFIGURAÇÃO =====
    function setupDataTable() {
        if ($.fn.DataTable && $('#emprestimosTable').length) {
            $('#emprestimosTable').DataTable({
                pageLength: 10,
                lengthMenu: [5, 10, 25, 50, 100],
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json'
                },
                order: [[3, 'desc']],
                responsive: true,
                columnDefs: [
                    { responsivePriority: 1, targets: 1 },
                    { responsivePriority: 2, targets: 2 },
                    { responsivePriority: 3, targets: -1 },
                    { orderable: false, targets: -1 }
                ]
            });
        }
    }
    
    // ===== EVENT LISTENERS =====
    function setupEventListeners() {
        // Botões de filtro
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remover classe active de todos os botões
                filterButtons.forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Adicionar classe active ao botão clicado
                this.classList.add('active');
                
                const filter = this.dataset.filter;
                filtrarEmprestimos(filter);
            });
        });
        
        // Busca
        setupSearch();
        
        // Botões de detalhes
        btnDetalhes.forEach(btn => {
            btn.addEventListener('click', function() {
                const emprestimoId = this.dataset.emprestimoId;
                carregarDetalhesEmprestimo(emprestimoId);
                
                // Abrir modal
                const modal = new bootstrap.Modal(modalDetalhes);
                modal.show();
            });
        });
        
        // Limpar busca com duplo clique
        if (searchInput) {
            searchInput.addEventListener('dblclick', function() {
                this.value = '';
                filtrarEmprestimos('all');
                filterButtons.forEach(btn => {
                    btn.classList.remove('active');
                });
                document.querySelector('.btn-filter[data-filter="all"]').classList.add('active');
            });
        }
    }
    
    // ===== UTILITÁRIOS =====
    function showLoading() {
        let overlay = document.getElementById('loadingOverlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = '<div class="spinner"></div>';
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    }
    
    function hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    function showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} floating-alert`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${message}
        `;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // ===== INICIALIZAÇÃO =====
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Exportar funções para uso externo
    window.listaEmprestimos = {
        filtrarEmprestimos: filtrarEmprestimos,
        carregarDetalhesEmprestimo: carregarDetalhesEmprestimo,
        exportToExcel: exportToExcel,
        refreshTable: refreshTable
    };
});