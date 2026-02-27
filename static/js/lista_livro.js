/**
 * Lista de Livros - Funcionalidades Específicas
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Lista de Livros carregada');
    
    // Elementos principais
    const tabelaLivros = document.getElementById('tabelaLivros');
    const filtroCategoria = document.getElementById('filtroCategoria');
    const filtroStatus = document.getElementById('filtroStatus');
    const buscaLivros = document.getElementById('buscaLivros');
    const btnBuscar = document.querySelector('.input-group .btn');
    const modalDetalhes = document.getElementById('modalDetalhesLivro');
    const btnEditarLivro = document.getElementById('btnEditarLivro');
    let livroAtualId = null;
    
    // ===== FILTRAGEM DE LIVROS =====
    function filtrarLivros() {
        if (!tabelaLivros) return;
        
        const categoria = filtroCategoria ? filtroCategoria.value : '';
        const status = filtroStatus ? filtroStatus.value : '';
        const busca = buscaLivros ? buscaLivros.value.toLowerCase().trim() : '';
        
        const linhas = tabelaLivros.querySelectorAll('tbody tr.livro-row');
        
        linhas.forEach(linha => {
            const linhaCategoria = linha.dataset.categoria;
            const linhaStatus = linha.dataset.status;
            const linhaDisponivel = linha.dataset.disponivel;
            const linhaTitulo = linha.dataset.titulo || '';
            const linhaAutor = linha.dataset.autor || '';
            const linhaTexto = linha.textContent.toLowerCase();
            
            let mostrar = true;
            
            // Filtrar por categoria
            if (categoria && linhaCategoria !== categoria) {
                mostrar = false;
            }
            
            // Filtrar por status
            if (status) {
                if (status === 'ativo' && linhaStatus !== 'ativo') {
                    mostrar = false;
                } else if (status === 'inativo' && linhaStatus !== 'inativo') {
                    mostrar = false;
                } else if (status === 'disponivel' && linhaDisponivel !== 'disponivel') {
                    mostrar = false;
                } else if (status === 'indisponivel' && linhaDisponivel !== 'indisponivel') {
                    mostrar = false;
                }
            }
            
            // Filtrar por busca
            if (busca) {
                const correspondeTitulo = linhaTitulo.includes(busca);
                const correspondeAutor = linhaAutor.includes(busca);
                const correspondeTexto = linhaTexto.includes(busca);
                
                if (!correspondeTitulo && !correspondeAutor && !correspondeTexto) {
                    mostrar = false;
                }
            }
            
            // Aplicar visual
            if (mostrar) {
                linha.style.display = '';
                linha.classList.add('fade-in');
                linha.classList.remove('d-none');
            } else {
                linha.style.display = 'none';
                linha.classList.remove('fade-in');
            }
        });
        
        // Atualizar contador
        atualizarContadorLivros();
    }
    
    function atualizarContadorLivros() {
        const linhasVisiveis = tabelaLivros ? 
            tabelaLivros.querySelectorAll('tbody tr.livro-row:not([style*="display: none"]):not([style*="display:none"])').length : 0;
        
        const contador = document.querySelector('.card-title .badge');
        if (contador) {
            contador.textContent = `${linhasVisiveis} livro${linhasVisiveis !== 1 ? 's' : ''}`;
        }
    }
    
    // ===== CARREGAR DETALHES DO LIVRO =====
    function carregarDetalhesLivro(livroId) {
        livroAtualId = livroId;
        
        // Mostrar loading
        const conteudoModal = document.getElementById('conteudoDetalhesLivro');
        conteudoModal.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-3 text-muted">Carregando detalhes do livro...</p>
            </div>
        `;
        
        // Fazer requisição AJAX
        fetch(`/api/livro/${livroId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Livro não encontrado');
                }
                return response.json();
            })
            .then(data => {
                exibirDetalhesLivro(data);
            })
            .catch(error => {
                console.error('Erro:', error);
                conteudoModal.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Erro ao carregar detalhes do livro: ${error.message}
                    </div>
                `;
            });
    }
    
    function exibirDetalhesLivro(livro) {
        const conteudoModal = document.getElementById('conteudoDetalhesLivro');
        
        // Calcular porcentagens
        const disponivelPercent = Math.round((livro.quantidade_disponivel / livro.quantidade_total) * 100);
        const emprestadoPercent = Math.round(((livro.quantidade_total - livro.quantidade_disponivel) / livro.quantidade_total) * 100);
        
        conteudoModal.innerHTML = `
            <div class="row">
                <!-- Capa do Livro -->
                <div class="col-md-4 mb-4 mb-md-0">
                    <div class="text-center">
                        <div class="book-cover mb-3">
                            <i class="fas fa-book-open fa-5x text-primary"></i>
                        </div>
                        <div class="d-grid gap-2">
                            <span class="badge ${livro.ativo ? 'bg-success' : 'bg-danger'} fs-6">
                                <i class="fas fa-${livro.ativo ? 'check' : 'times'} me-1"></i>
                                ${livro.ativo ? 'Ativo' : 'Inativo'}
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Informações do Livro -->
                <div class="col-md-8">
                    <h4 class="mb-2">${livro.titulo}</h4>
                    <p class="text-muted mb-3">
                        <i class="fas fa-user-edit me-2"></i>${livro.autor}
                    </p>
                    
                    <!-- Informações Básicas -->
                    <div class="row mb-4">
                        <div class="col-6 mb-3">
                            <label class="small text-muted d-block">Editora</label>
                            <strong>${livro.editora || 'Não informada'}</strong>
                        </div>
                        <div class="col-6 mb-3">
                            <label class="small text-muted d-block">Ano de Publicação</label>
                            <strong>${livro.ano_publicacao || 'Não informado'}</strong>
                        </div>
                        <div class="col-6 mb-3">
                            <label class="small text-muted d-block">Categoria</label>
                            <span class="badge bg-secondary">${livro.categoria_display}</span>
                        </div>
                        <div class="col-6 mb-3">
                            <label class="small text-muted d-block">Classificação</label>
                            <strong>${livro.classificacao || 'Não classificada'}</strong>
                        </div>
                        <div class="col-6">
                            <label class="small text-muted d-block">Prateleira</label>
                            <span class="badge bg-info">
                                <i class="fas fa-layer-group me-1"></i>${livro.prateleira}
                            </span>
                        </div>
                        <div class="col-6">
                            <label class="small text-muted d-block">ISBN</label>
                            <strong>${livro.isbn || 'Não informado'}</strong>
                        </div>
                    </div>
                    
                    <!-- Estatísticas de Quantidade -->
                    <div class="card mb-4">
                        <div class="card-header bg-light">
                            <strong><i class="fas fa-chart-bar me-2"></i>Estoque do Livro</strong>
                        </div>
                        <div class="card-body">
                            <!-- Barras de Progresso -->
                            <div class="mb-3">
                                <div class="d-flex justify-content-between mb-1">
                                    <span class="small">Disponível: ${livro.quantidade_disponivel} (${disponivelPercent}%)</span>
                                    <span class="small">Emprestado: ${livro.quantidade_total - livro.quantidade_disponivel} (${emprestadoPercent}%)</span>
                                </div>
                                <div class="progress" style="height: 12px">
                                    <div class="progress-bar bg-success" style="width: ${disponivelPercent}%"></div>
                                    <div class="progress-bar bg-warning" style="width: ${emprestadoPercent}%"></div>
                                </div>
                            </div>
                            
                            <!-- Números -->
                            <div class="row text-center">
                                <div class="col-4">
                                    <div class="display-6 text-success">${livro.quantidade_disponivel}</div>
                                    <small class="text-muted">Disponíveis</small>
                                </div>
                                <div class="col-4">
                                    <div class="display-6 text-warning">${livro.quantidade_total - livro.quantidade_disponivel}</div>
                                    <small class="text-muted">Emprestados</small>
                                </div>
                                <div class="col-4">
                                    <div class="display-6 text-secondary">${livro.quantidade_total}</div>
                                    <small class="text-muted">Total</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Sinopse -->
                    ${livro.sinopse ? `
                    <div class="card">
                        <div class="card-header bg-light">
                            <strong><i class="fas fa-align-left me-2"></i>Sinopse</strong>
                        </div>
                        <div class="card-body">
                            <p class="mb-0">${livro.sinopse}</p>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        // Configurar botão de editar
        if (btnEditarLivro) {
            btnEditarLivro.onclick = function() {
                if (livroAtualId) {
                    window.location.href = `/sistema/livros/editar/${livroAtualId}/`;
                }
            };
        }
    }
    
    // ===== HISTÓRICO DO LIVRO =====
    function verHistoricoLivro(livroId) {
        // Simulação de carregamento de histórico
        Swal.fire({
            title: 'Histórico do Livro',
            text: `Carregando histórico para o livro ID: ${livroId}`,
            icon: 'info',
            showCancelButton: false,
            showConfirmButton: true,
            confirmButtonText: 'OK',
            timer: 2000,
            timerProgressBar: true
        });
        
        // Em produção, faria uma requisição AJAX
        // fetch(`/api/livro/${livroId}/historico/`)
        //     .then(response => response.json())
        //     .then(data => exibirHistorico(data));
    }
    
    // ===== EVENT LISTENERS =====
    function setupEventListeners() {
        // Filtros
        if (filtroCategoria) {
            filtroCategoria.addEventListener('change', filtrarLivros);
        }
        
        if (filtroStatus) {
            filtroStatus.addEventListener('change', filtrarLivros);
        }
        
        if (buscaLivros) {
            buscaLivros.addEventListener('input', filtrarLivros);
            buscaLivros.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    filtrarLivros();
                }
            });
        }
        
        if (btnBuscar) {
            btnBuscar.addEventListener('click', filtrarLivros);
        }
        
        // Botões de detalhes
        document.querySelectorAll('.ver-detalhes').forEach(btn => {
            btn.addEventListener('click', function() {
                const livroId = this.dataset.livroId;
                carregarDetalhesLivro(livroId);
                
                // Abrir modal
                const modal = new bootstrap.Modal(modalDetalhes);
                modal.show();
            });
        });
        
        // Botões de histórico
        document.querySelectorAll('.ver-historico').forEach(btn => {
            btn.addEventListener('click', function() {
                const livroId = this.dataset.livroId;
                verHistoricoLivro(livroId);
            });
        });
        
        // Limpar filtros com duplo clique
        if (filtroCategoria) {
            filtroCategoria.addEventListener('dblclick', function() {
                this.value = '';
                filtrarLivros();
            });
        }
        
        if (filtroStatus) {
            filtroStatus.addEventListener('dblclick', function() {
                this.value = '';
                filtrarLivros();
            });
        }
        
        if (buscaLivros) {
            buscaLivros.addEventListener('dblclick', function() {
                this.value = '';
                filtrarLivros();
            });
        }
    }
    
    // ===== ANIMAÇÕES =====
    function initAnimations() {
        // Animar números dos cards
        const statNumbers = document.querySelectorAll('.stat-number');
        
        statNumbers.forEach(el => {
            const text = el.textContent.trim();
            const number = parseInt(text);
            
            if (!isNaN(number) && number > 0) {
                animateCounter(el, number);
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
    
    // ===== EXPORTAÇÃO PARA CSV =====
    function exportarParaCSV() {
        // Implementação básica de exportação
        const linhas = tabelaLivros.querySelectorAll('tbody tr:not([style*="display: none"])');
        let csvContent = "Título,Autor,Categoria,Prateleira,Disponível,Emprestado,Total,Status\n";
        
        linhas.forEach(linha => {
            const colunas = linha.querySelectorAll('td');
            const dados = [];
            
            // Título
            dados.push(`"${colunas[0].querySelector('strong')?.textContent.trim() || ''}"`);
            
            // Autor
            dados.push(`"${colunas[1].textContent.trim()}"`);
            
            // Categoria
            dados.push(`"${colunas[2].textContent.trim()}"`);
            
            // Prateleira
            dados.push(`"${colunas[3].textContent.trim()}"`);
            
            // Status
            dados.push(`"${colunas[5].textContent.trim()}"`);
            
            csvContent += dados.join(',') + '\n';
        });
        
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `livros_${new Date().toISOString().slice(0,10)}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // ===== INICIALIZAÇÃO =====
    function init() {
        console.log('Inicializando Lista de Livros...');
        
        initAnimations();
        setupEventListeners();
        filtrarLivros(); // Aplicar filtros iniciais se houver
        
        // Adicionar botão de exportação se não existir
        const actionBar = document.querySelector('.action-bar .d-flex:first-child');
        if (actionBar && !document.getElementById('btnExportar')) {
            const btnExportar = document.createElement('button');
            btnExportar.id = 'btnExportar';
            btnExportar.className = 'btn btn-outline-secondary ms-2';
            btnExportar.innerHTML = '<i class="fas fa-file-export me-2"></i>Exportar';
            btnExportar.title = 'Exportar lista para CSV';
            btnExportar.addEventListener('click', exportarParaCSV);
            actionBar.appendChild(btnExportar);
        }
        
        console.log('Lista de Livros inicializada com sucesso!');
    }
    
    // Inicializar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Exportar funções para uso externo
    window.listaLivros = {
        filtrarLivros: filtrarLivros,
        carregarDetalhesLivro: carregarDetalhesLivro,
        exportarParaCSV: exportarParaCSV
    };
});