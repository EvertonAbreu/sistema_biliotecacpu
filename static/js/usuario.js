/**
 * JavaScript base para todas as páginas do sistema
 * Biblioteca Pública Municipal
 */

document.addEventListener('DOMContentLoaded', function() {
    // ===== INICIALIZAÇÃO GERAL =====
    function initGeneral() {
        // Tooltips do Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Popovers do Bootstrap
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
        
        // Auto-dismiss alerts
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }
    
    // ===== NAVBAR MOBILE =====
    function initMobileNav() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggler && navbarCollapse) {
            // Fechar menu ao clicar em um link
            const navLinks = document.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    if (navbarCollapse.classList.contains('show')) {
                        navbarToggler.click();
                    }
                });
            });
            
            // Fechar menu ao redimensionar janela
            window.addEventListener('resize', () => {
                if (window.innerWidth > 768 && navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        }
    }
    
    // ===== SCROLL TO TOP =====
    function initScrollToTop() {
        const scrollToTopBtn = document.createElement('button');
        scrollToTopBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
        scrollToTopBtn.className = 'btn-scroll-top';
        document.body.appendChild(scrollToTopBtn);
        
        // Estilos para o botão
        const style = document.createElement('style');
        style.textContent = `
            .btn-scroll-top {
                position: fixed;
                bottom: 30px;
                right: 30px;
                width: 50px;
                height: 50px;
                background: var(--secondary-color);
                color: white;
                border: none;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
                cursor: pointer;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
                z-index: 999;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            }
            
            .btn-scroll-top.show {
                opacity: 1;
                visibility: visible;
            }
            
            .btn-scroll-top:hover {
                background: #2980b9;
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }
        `;
        document.head.appendChild(style);
        
        // Mostrar/ocultar botão
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                scrollToTopBtn.classList.add('show');
            } else {
                scrollToTopBtn.classList.remove('show');
            }
        });
        
        // Rolar para o topo
        scrollToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // ===== FORM VALIDATION =====
    function initFormValidation() {
        const forms = document.querySelectorAll('form[novalidate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!this.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Adicionar classes de validação do Bootstrap
                    this.classList.add('was-validated');
                    
                    // Rolar para o primeiro campo inválido
                    const firstInvalid = this.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                        firstInvalid.focus();
                    }
                }
            });
        });
    }
    
    // ===== LOADING BUTTONS =====
    function initLoadingButtons() {
        document.querySelectorAll('.btn-loading').forEach(btn => {
            btn.addEventListener('click', function() {
                const originalText = this.innerHTML;
                const originalWidth = this.offsetWidth;
                
                // Manter a largura do botão
                this.style.minWidth = originalWidth + 'px';
                
                // Mostrar spinner
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processando...';
                this.disabled = true;
                
                // Restaurar após 5 segundos (fallback)
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                    this.style.minWidth = '';
                }, 5000);
            });
        });
    }
    
    // ===== COPY TO CLIPBOARD =====
    function initCopyToClipboard() {
        document.querySelectorAll('[data-copy]').forEach(btn => {
            btn.addEventListener('click', function() {
                const textToCopy = this.getAttribute('data-copy');
                
                navigator.clipboard.writeText(textToCopy).then(() => {
                    // Feedback visual
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check me-2"></i>Copiado!';
                    this.classList.add('btn-success');
                    
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.classList.remove('btn-success');
                    }, 2000);
                }).catch(err => {
                    console.error('Erro ao copiar: ', err);
                    alert('Não foi possível copiar o texto');
                });
            });
        });
    }
    
    // ===== THEME SWITCHER (opcional) =====
    function initThemeSwitcher() {
        const themeToggle = document.querySelector('#themeToggle');
        
        if (themeToggle) {
            // Verificar tema salvo
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.body.setAttribute('data-theme', savedTheme);
            
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.body.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                
                document.body.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // Atualizar ícone
                const icon = themeToggle.querySelector('i');
                icon.className = newTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            });
        }
    }
    
    // ===== OFFLINE DETECTION =====
    function initOfflineDetection() {
        window.addEventListener('online', () => {
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show';
            alert.innerHTML = `
                <i class="fas fa-wifi me-2"></i>
                Conexão restaurada. Você está online novamente.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.querySelector('.messages-container')?.appendChild(alert);
        });
        
        window.addEventListener('offline', () => {
            const alert = document.createElement('div');
            alert.className = 'alert alert-warning alert-dismissible fade show';
            alert.innerHTML = `
                <i class="fas fa-wifi-slash me-2"></i>
                Você está offline. Algumas funcionalidades podem não estar disponíveis.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.querySelector('.messages-container')?.appendChild(alert);
        });
    }
    
    // ===== DEBOUNCE FUNCTION =====
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
    
    // ===== INITIALIZE ALL =====
    function init() {
        initGeneral();
        initMobileNav();
        initScrollToTop();
        initFormValidation();
        initLoadingButtons();
        initCopyToClipboard();
        initThemeSwitcher();
        initOfflineDetection();
        
        // Adicionar classe para transições CSS após carregamento
        setTimeout(() => {
            document.body.classList.add('loaded');
        }, 100);
        
        // Log de inicialização
        console.log('Biblioteca Pública - Sistema inicializado');
    }
    
    // Executar inicialização
    init();
    
    // ===== GLOBAL FUNCTIONS =====
    window.biblioteca = window.biblioteca || {};
    
    // Função para mostrar toast
    window.biblioteca.showToast = function(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container') || createToastContainer();
        const toastId = 'toast-' + Date.now();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-bg-${type} border-0`;
        toast.id = toastId;
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas 
                        ${type === 'success' ? 'fa-check-circle' :
                          type === 'danger' ? 'fa-exclamation-circle' :
                          type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'} me-2">
                    </i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    };
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    }
    
    // Função para confirmar ação
    window.biblioteca.confirmAction = function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    };
    
    // Função para formatar data
    window.biblioteca.formatDate = function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    };
});

// ===== WINDOW LOAD EVENT =====
window.addEventListener('load', function() {
    // Remover preloader
    const preloader = document.querySelector('.preloader');
    if (preloader) {
        setTimeout(() => {
            preloader.style.opacity = '0';
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 500);
        }, 500);
    }
    
    // Adicionar transição suave para imagens
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        if (img.complete) {
            img.classList.add('loaded');
        } else {
            img.addEventListener('load', function() {
                this.classList.add('loaded');
            });
        }
    });
    
    // Log de performance
    const loadTime = window.performance.timing.domContentLoadedEventEnd - 
                    window.performance.timing.navigationStart;
    console.log(`Página carregada em ${loadTime}ms`);
});

// ===== ERROR HANDLING =====
window.addEventListener('error', function(e) {
    console.error('Erro na página:', e.error);
    
    // Mostrar erro amigável para o usuário
    if (!document.querySelector('.global-error')) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'global-error alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            Ocorreu um erro inesperado. Por favor, recarregue a página.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.prepend(errorDiv);
    }
});

// ===== PWA SUPPORT (opcional) =====
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').then(registration => {
            console.log('ServiceWorker registrado com sucesso:', registration.scope);
        }).catch(err => {
            console.log('Falha ao registrar ServiceWorker:', err);
        });
    });
}