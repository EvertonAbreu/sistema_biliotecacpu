/**
 * Dashboard Admin - Biblioteca Pública
 * Scripts específicos para o dashboard administrativo
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard admin carregado');
    
    // ===== ANIMAÇÃO DE NÚMEROS =====
    function animateNumbers() {
        const numberElements = document.querySelectorAll('.stat-number, .stat-number-sm');
        
        numberElements.forEach(el => {
            const text = el.textContent.trim();
            
            // Verificar se é um número
            const number = parseInt(text);
            if (!isNaN(number) && number > 0) {
                const finalValue = number;
                let startValue = 0;
                const duration = 1500; // 1.5 segundos
                const increment = finalValue / (duration / 16); // 60fps
                
                // Limpar conteúdo
                el.textContent = '0';
                
                const timer = setInterval(() => {
                    startValue += increment;
                    if (startValue >= finalValue) {
                        el.textContent = finalValue.toLocaleString('pt-BR');
                        clearInterval(timer);
                        
                        // Adicionar efeito de conclusão
                        el.style.color = '#28a745';
                        setTimeout(() => {
                            el.style.color = '';
                        }, 500);
                    } else {
                        el.textContent = Math.floor(startValue).toLocaleString('pt-BR');
                    }
                }, 16);
            }
        });
    }
    
    // ===== BADGE DE ATRASADOS PISCANTE =====
    function initWarningBadge() {
        const warningElement = document.querySelector('.stat-subtext.text-danger');
        if (warningElement) {
            // Verificar se há atrasados
            const warningText = warningElement.textContent;
            const hasDelays = warningText.includes('atrasados');
            
            if (hasDelays) {
                // Adicionar animação de piscar
                setInterval(() => {
                    warningElement.classList.toggle('text-danger');
                    warningElement.classList.toggle('text-warning');
                    
                    // Também piscar o ícone
                    const icon = warningElement.querySelector('i');
                    if (icon) {
                        icon.classList.toggle('fa-exclamation-triangle');
                        icon.classList.toggle('fa-exclamation-circle');
                    }
                }, 1000);
                
                // Adicionar tooltip
                warningElement.setAttribute('title', 'Há empréstimos atrasados! Clique para ver detalhes.');
                warningElement.style.cursor = 'pointer';
                
                warningElement.addEventListener('click', function() {
                    const emprestimosUrl = document.querySelector('a[href*="lista_emprestimos"]');
                    if (emprestimosUrl) {
                        window.location.href = emprestimosUrl.href;
                    }
                });
            }
        }
    }
    
    // ===== AUTO-REFRESH DO DASHBOARD =====
    function initAutoRefresh() {
        let refreshCountdown = 60; // segundos
        
        function updateRefreshCounter() {
            const counterElement = document.getElementById('refresh-counter');
            if (counterElement) {
                counterElement.textContent = refreshCountdown;
            }
            
            refreshCountdown--;
            
            if (refreshCountdown <= 0) {
                if (!document.hidden) {
                    location.reload();
                }
                refreshCountdown = 60;
            }
        }
        
        // Criar elemento de contador se não existir
        if (!document.getElementById('refresh-counter')) {
            const header = document.querySelector('.dashboard-card .card-header');
            if (header) {
                const counterSpan = document.createElement('span');
                counterSpan.id = 'refresh-counter';
                counterSpan.className = 'badge bg-info ms-2';
                counterSpan.textContent = '60';
                counterSpan.setAttribute('title', 'Segundos até próximo refresh automático');
                counterSpan.style.cursor = 'help';
                
                header.querySelector('.card-title').appendChild(counterSpan);
            }
        }
        
        // Iniciar contador
        setInterval(updateRefreshCounter, 1000);
    }
    
    // ===== ANIMAÇÃO DE ENTRADA DOS CARDS =====
    function initCardAnimations() {
        const cards = document.querySelectorAll('.stat-card, .dashboard-card');
        
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
    
    // ===== TOOLTIPS =====
    function initTooltips() {
        // Tooltips do Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Tooltips personalizados para números
        const statNumbers = document.querySelectorAll('.stat-number');
        statNumbers.forEach(number => {
            number.setAttribute('title', 'Clique para ver detalhes');
            number.style.cursor = 'pointer';
            
            number.addEventListener('click', function() {
                // Determinar qual seção mostrar com base no tipo
                const parentCard = this.closest('.stat-card');
                if (parentCard) {
                    const icon = parentCard.querySelector('.stat-icon i');
                    if (icon) {
                        const iconClass = icon.className;
                        
                        if (iconClass.includes('fa-book')) {
                            window.location.href = document.querySelector('a[href*="lista_livros"]').href;
                        } else if (iconClass.includes('fa-file-pdf')) {
                            window.location.href = '/admin/core/livropdf/';
                        } else if (iconClass.includes('fa-users')) {
                            window.location.href = document.querySelector('a[href*="lista_usuarios"]').href;
                        } else if (iconClass.includes('fa-book-reader')) {
                            window.location.href = document.querySelector('a[href*="lista_emprestimos"]').href;
                        } else if (iconClass.includes('fa-calendar-alt')) {
                            window.location.href = document.querySelector('a[href*="lista_eventos"]').href;
                        }
                    }
                }
            });
        });
    }
    
    // ===== BOTÕES DE AÇÃO RÁPIDA =====
    function initQuickActions() {
        const quickActions = document.querySelectorAll('.quick-action-btn');
        
        quickActions.forEach(btn => {
            btn.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px) scale(1.05)';
                this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.2)';
            });
            
            btn.addEventListener('mouseleave', function() {
                this.style.transform = '';
                this.style.boxShadow = '';
            });
            
            // Efeito de clique
            btn.addEventListener('mousedown', function() {
                this.style.transform = 'translateY(-2px) scale(0.98)';
            });
            
            btn.addEventListener('mouseup', function() {
                this.style.transform = 'translateY(-5px) scale(1.05)';
            });
        });
    }
    
    // ===== GRÁFICOS DINÂMICOS (SIMULADOS) =====
    function initChartSimulation() {
        // Simular gráfico de empréstimos por mês
        const emprestimosData = [12, 19, 15, 25, 22, 30, 28, 32, 29, 27, 31, 35];
        const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
        
        // Adicionar mini gráfico na tabela de empréstimos
        const emprestimosRows = document.querySelectorAll('.dashboard-card tbody tr');
        emprestimosRows.forEach((row, index) => {
            if (index < 3) { // Apenas para as primeiras linhas
                const cell = row.cells[2]; // Coluna de data
                const dateText = cell.textContent.trim();
                
                // Criar mini gráfico de barras
                const barContainer = document.createElement('div');
                barContainer.className = 'mini-bar-chart';
                barContainer.style.display = 'inline-block';
                barContainer.style.marginLeft = '10px';
                barContainer.style.verticalAlign = 'middle';
                barContainer.style.height = '15px';
                barContainer.style.width = '40px';
                barContainer.style.backgroundColor = '#e9ecef';
                barContainer.style.borderRadius = '3px';
                barContainer.style.overflow = 'hidden';
                barContainer.style.position = 'relative';
                
                const bar = document.createElement('div');
                bar.style.position = 'absolute';
                bar.style.top = '0';
                bar.style.left = '0';
                bar.style.height = '100%';
                bar.style.width = Math.min(Math.random() * 100, 100) + '%';
                bar.style.backgroundColor = index === 0 ? '#4e73df' : 
                                           index === 1 ? '#1cc88a' : '#f6c23e';
                bar.style.transition = 'width 1s ease';
                
                barContainer.appendChild(bar);
                cell.appendChild(barContainer);
                
                // Animar a barra
                setTimeout(() => {
                    bar.style.transition = 'width 1s ease';
                }, index * 200);
            }
        });
    }
    
    // ===== NOTIFICAÇÕES DINÂMICAS =====
    function initNotifications() {
        // Verificar se há eventos próximos
        const proximoEventoCard = document.querySelector('.stat-card.stat-danger');
        if (proximoEventoCard) {
            const eventDateText = proximoEventoCard.querySelector('.stat-subtext')?.textContent;
            if (eventDateText && eventDateText.includes('/')) {
                const today = new Date();
                const eventDate = parseDate(eventDateText);
                
                if (eventDate) {
                    const diffTime = eventDate - today;
                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                    
                    if (diffDays <= 3 && diffDays >= 0) {
                        // Evento próximo! Adicionar efeito especial
                        proximoEventoCard.classList.add('event-soon');
                        proximoEventoCard.style.animation = 'pulse 2s infinite';
                        
                        // Adicionar badge de alerta
                        const statIcon = proximoEventoCard.querySelector('.stat-icon');
                        const alertBadge = document.createElement('span');
                        alertBadge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
                        alertBadge.style.fontSize = '0.6rem';
                        alertBadge.style.padding = '0.25em 0.5em';
                        alertBadge.textContent = '!';
                        alertBadge.title = `Evento em ${diffDays} dias`;
                        statIcon.appendChild(alertBadge);
                    }
                }
            }
        }
        
        // Função auxiliar para parsear data
        function parseDate(dateString) {
            const match = dateString.match(/(\d{2})\/(\d{2})\/(\d{4})/);
            if (match) {
                const [, day, month, year] = match;
                return new Date(year, month - 1, day);
            }
            return null;
        }
    }
    
    // ===== ATUALIZAÇÃO DE STATUS EM TEMPO REAL =====
    function initRealTimeUpdates() {
        // Simular atualizações em tempo real
        const updateInterval = 30000; // 30 segundos
        
        function simulateUpdates() {
            // Atualizar contadores aleatoriamente
            const statNumbers = document.querySelectorAll('.stat-number');
            statNumbers.forEach(number => {
                const current = parseInt(number.textContent);
                if (!isNaN(current) && Math.random() > 0.7) {
                    const change = Math.floor(Math.random() * 5) - 2; // -2 a +2
                    const newValue = Math.max(0, current + change);
                    
                    if (newValue !== current) {
                        // Efeito visual
                        number.style.color = newValue > current ? '#28a745' : '#dc3545';
                        setTimeout(() => {
                            number.style.color = '';
                        }, 1000);
                        
                        number.textContent = newValue.toLocaleString('pt-BR');
                    }
                }
            });
        }
        
        setInterval(simulateUpdates, updateInterval);
    }
    
    // ===== RESPONSIVIDADE DINÂMICA =====
    function initResponsiveBehavior() {
        function adjustLayout() {
            const width = window.innerWidth;
            const quickActionsGrid = document.querySelector('.quick-actions-grid');
            
            if (quickActionsGrid) {
                if (width < 768) {
                    quickActionsGrid.style.gridTemplateColumns = '1fr';
                } else if (width < 1200) {
                    quickActionsGrid.style.gridTemplateColumns = 'repeat(2, 1fr)';
                } else {
                    quickActionsGrid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(200px, 1fr))';
                }
            }
            
            // Ajustar tamanho da fonte em telas muito pequenas
            const statNumbers = document.querySelectorAll('.stat-number');
            if (width < 576) {
                statNumbers.forEach(num => {
                    num.style.fontSize = '1.3rem';
                });
            } else if (width < 768) {
                statNumbers.forEach(num => {
                    num.style.fontSize = '1.5rem';
                });
            } else {
                statNumbers.forEach(num => {
                    num.style.fontSize = '';
                });
            }
        }
        
        // Executar ao carregar e ao redimensionar
        adjustLayout();
        window.addEventListener('resize', adjustLayout);
    }
    
    // ===== SHORTCUTS DE TECLADO =====
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl + Alt + N = Novo Livro
            if (e.ctrlKey && e.altKey && e.key === 'n') {
                e.preventDefault();
                const novoLivroBtn = document.querySelector('a[href*="cadastro_livro"]');
                if (novoLivroBtn) window.location.href = novoLivroBtn.href;
            }
            
            // Ctrl + Alt + U = Novo Usuário
            if (e.ctrlKey && e.altKey && e.key === 'u') {
                e.preventDefault();
                const novoUsuarioBtn = document.querySelector('a[href*="cadastro_usuario_admin"]');
                if (novoUsuarioBtn) window.location.href = novoUsuarioBtn.href;
            }
            
            // Ctrl + Alt + E = Novo Empréstimo
            if (e.ctrlKey && e.altKey && e.key === 'e') {
                e.preventDefault();
                const novoEmprestimoBtn = document.querySelector('a[href*="realizar_emprestimo"]');
                if (novoEmprestimoBtn) window.location.href = novoEmprestimoBtn.href;
            }
            
            // F5 = Refresh com confirmação
            if (e.key === 'F5') {
                e.preventDefault();
                if (confirm('Recarregar o dashboard?')) {
                    location.reload();
                }
            }
        });
        
        // Mostrar dica de shortcuts
        setTimeout(() => {
            if (localStorage.getItem('showShortcutsHint') !== 'false') {
                const hint = document.createElement('div');
                hint.className = 'alert alert-info alert-dismissible fade show position-fixed';
                hint.style.bottom = '20px';
                hint.style.right = '20px';
                hint.style.zIndex = '1000';
                hint.style.maxWidth = '300px';
                hint.innerHTML = `
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    <strong>Dica:</strong> Use <kbd>Ctrl+Alt+N</kbd> para novo livro, 
                    <kbd>Ctrl+Alt+U</kbd> para novo usuário
                    <div class="form-check form-switch mt-2">
                        <input class="form-check-input" type="checkbox" id="disableHints">
                        <label class="form-check-label" for="disableHints">Não mostrar novamente</label>
                    </div>
                `;
                document.body.appendChild(hint);
                
                // Configurar checkbox
                const checkbox = hint.querySelector('#disableHints');
                checkbox.addEventListener('change', function() {
                    localStorage.setItem('showShortcutsHint', !this.checked);
                });
                
                // Auto-fechar após 10 segundos
                setTimeout(() => {
                    const bsAlert = new bootstrap.Alert(hint);
                    bsAlert.close();
                }, 10000);
            }
        }, 3000);
    }
    
    // ===== METRICS TRACKING =====
    function initMetricsTracking() {
        // Track de interação do usuário
        const interactionStart = Date.now();
        let clickCount = 0;
        let hoverCount = 0;
        
        // Contar cliques
        document.addEventListener('click', function() {
            clickCount++;
        });
        
        // Contar hovers
        document.addEventListener('mouseover', function(e) {
            if (e.target.closest('.stat-card, .quick-action-btn, .dashboard-card')) {
                hoverCount++;
            }
        });
        
        // Enviar métricas ao sair (simulado)
        window.addEventListener('beforeunload', function() {
            const sessionDuration = Date.now() - interactionStart;
            const metrics = {
                duration: Math.round(sessionDuration / 1000),
                clicks: clickCount,
                hovers: hoverCount,
                page: 'admin_dashboard'
            };
            
            console.log('Session Metrics:', metrics);
            // Em produção, enviaria para um endpoint de analytics
            // fetch('/api/metrics/', { method: 'POST', body: JSON.stringify(metrics) });
        });
    }
    
    // ===== DARK MODE SUPPORT =====
    function initDarkMode() {
        // Verificar preferência do sistema
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
        
        function updateDarkMode(isDark) {
            if (isDark) {
                document.documentElement.setAttribute('data-bs-theme', 'dark');
                
                // Ajustar cores específicas
                const statCards = document.querySelectorAll('.stat-card');
                statCards.forEach(card => {
                    card.style.backgroundColor = '#2d3748';
                    card.style.color = '#e2e8f0';
                });
                
                const dashboardCards = document.querySelectorAll('.dashboard-card');
                dashboardCards.forEach(card => {
                    card.style.backgroundColor = '#2d3748';
                });
            } else {
                document.documentElement.setAttribute('data-bs-theme', 'light');
            }
        }
        
        // Aplicar inicialmente
        updateDarkMode(prefersDark.matches);
        
        // Observar mudanças
        prefersDark.addEventListener('change', (e) => {
            updateDarkMode(e.matches);
        });
    }
    
    // ===== INICIALIZAÇÃO =====
    function init() {
        console.log('Inicializando dashboard admin...');
        
        // Executar inicializações
        animateNumbers();
        initWarningBadge();
        initAutoRefresh();
        initCardAnimations();
        initTooltips();
        initQuickActions();
        initChartSimulation();
        initNotifications();
        initRealTimeUpdates();
        initResponsiveBehavior();
        initKeyboardShortcuts();
        initMetricsTracking();
        initDarkMode();
        
        // Adicionar CSS adicional dinâmico
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.02); }
            }
            
            .event-soon {
                animation: pulse 2s ease-in-out infinite;
            }
            
            .mini-bar-chart {
                transition: all 0.3s ease;
            }
            
            .mini-bar-chart:hover {
                transform: scaleY(1.5);
            }
            
            .stat-card:hover .stat-icon {
                transform: rotate(15deg) scale(1.1);
            }
            
            .stat-icon {
                transition: transform 0.3s ease;
            }
            
            .quick-action-btn:active {
                transform: translateY(-2px) scale(0.98) !important;
            }
            
            /* Dark mode adjustments */
            [data-bs-theme="dark"] .stat-label {
                color: #cbd5e0;
            }
            
            [data-bs-theme="dark"] .stat-number {
                color: #f7fafc;
            }
            
            [data-bs-theme="dark"] .card {
                background-color: #2d3748;
                color: #e2e8f0;
            }
        `;
        document.head.appendChild(style);
        
        console.log('Dashboard admin inicializado com sucesso!');
    }
    
    // Inicializar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // ===== AJAX PARA ATUALIZAÇÕES =====
    function fetchDashboardUpdates() {
        // Simular chamada AJAX para atualizar dados
        fetch('/api/dashboard/stats/')
            .then(response => response.json())
            .then(data => {
                // Atualizar contadores
                updateStatCounter('total_livros', data.total_livros);
                updateStatCounter('total_pdf', data.total_pdf);
                updateStatCounter('total_usuarios', data.total_usuarios);
                updateStatCounter('emprestimos_ativos', data.emprestimos_ativos);
                
                // Atualizar tabelas se necessário
                if (data.has_updates) {
                    refreshTables();
                }
            })
            .catch(error => {
                console.error('Erro ao buscar atualizações:', error);
            });
    }
    
    function updateStatCounter(elementId, newValue) {
        const element = document.getElementById(elementId);
        if (element) {
            const current = parseInt(element.textContent.replace(/\D/g, ''));
            if (!isNaN(current) && current !== newValue) {
                // Animar mudança
                animateCounter(element, current, newValue);
            }
        }
    }
    
    function animateCounter(element, start, end) {
        const duration = 1000;
        const steps = 60;
        const stepValue = (end - start) / steps;
        let current = start;
        
        const interval = setInterval(() => {
            current += stepValue;
            
            if ((stepValue > 0 && current >= end) || (stepValue < 0 && current <= end)) {
                element.textContent = end.toLocaleString('pt-BR');
                clearInterval(interval);
                
                // Efeito visual
                element.style.color = end > start ? '#28a745' : '#dc3545';
                setTimeout(() => {
                    element.style.color = '';
                }, 500);
            } else {
                element.textContent = Math.round(current).toLocaleString('pt-BR');
            }
        }, duration / steps);
    }
    
    // Iniciar polling para atualizações
    setInterval(fetchDashboardUpdates, 60000); // A cada 1 minuto
});

// Exportar funções para uso externo (se necessário)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        animateNumbers: animateNumbers,
        initCardAnimations: initCardAnimations
    };
}