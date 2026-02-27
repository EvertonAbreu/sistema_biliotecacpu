/**
 * Admin Base - Sidebar e Funcionalidades Gerais
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos principais
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const headerToggle = document.getElementById('headerToggle');
    const mobileToggle = document.getElementById('mobileToggle');
    const toggleIcon = document.getElementById('toggleIcon');
    const logoText = document.getElementById('logoText');
    
    // Criar overlay para mobile
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);
    
    // Verificar preferência salva
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    
    // Inicializar sidebar
    function initSidebar() {
        // Aplicar estado salvo
        if (sidebarCollapsed) {
            collapseSidebar();
        }
        
        // Restaurar tema
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        
        // Adicionar tooltips aos itens do menu
        updateSidebarTooltips();
    }
    
    // Colapsar sidebar
    function collapseSidebar() {
        sidebar.classList.add('collapsed');
        toggleIcon.classList.remove('bi-chevron-left');
        toggleIcon.classList.add('bi-chevron-right');
        
        // Salvar preferência
        localStorage.setItem('sidebarCollapsed', true);
    }
    
    // Expandir sidebar
    function expandSidebar() {
        sidebar.classList.remove('collapsed');
        toggleIcon.classList.remove('bi-chevron-right');
        toggleIcon.classList.add('bi-chevron-left');
        
        // Salvar preferência
        localStorage.setItem('sidebarCollapsed', false);
    }
    
    // Alternar sidebar
    function toggleSidebar() {
        if (sidebar.classList.contains('collapsed')) {
            expandSidebar();
        } else {
            collapseSidebar();
        }
        updateSidebarTooltips();
    }
    
    // Atualizar tooltips do sidebar
    function updateSidebarTooltips() {
        const menuItems = document.querySelectorAll('.menu-item');
        const userButtons = document.querySelectorAll('.user-actions .btn');
        const isCollapsed = sidebar.classList.contains('collapsed');
        
        // Para itens do menu
        menuItems.forEach(item => {
            const span = item.querySelector('span');
            if (span && isCollapsed) {
                item.setAttribute('data-title', span.textContent.trim());
            } else {
                item.removeAttribute('data-title');
            }
        });
        
        // Para botões do usuário
        userButtons.forEach(btn => {
            const span = btn.querySelector('span');
            if (span && isCollapsed) {
                btn.setAttribute('title', span.textContent.trim());
                btn.setAttribute('data-bs-toggle', 'tooltip');
                btn.setAttribute('data-bs-placement', 'right');
            } else {
                btn.removeAttribute('title');
                btn.removeAttribute('data-bs-toggle');
                btn.removeAttribute('data-bs-placement');
            }
        });
        
        // Inicializar tooltips do Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            // Destruir tooltip existente
            const existingTooltip = bootstrap.Tooltip.getInstance(tooltipTriggerEl);
            if (existingTooltip) {
                existingTooltip.dispose();
            }
            // Criar novo tooltip
            new bootstrap.Tooltip(tooltipTriggerEl, {
                delay: { show: 300, hide: 100 }
            });
        });
    }
    
    // Fechar sidebar no mobile
    function closeMobileSidebar() {
        sidebar.classList.remove('show');
        overlay.style.display = 'none';
        document.body.style.overflow = '';
    }
    
    // Abrir sidebar no mobile
    function openMobileSidebar() {
        sidebar.classList.add('show');
        overlay.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
    
    // Verificar se é mobile
    function isMobile() {
        return window.innerWidth <= 768;
    }
    
    // Configurar eventos do scroll do sidebar
    function setupSidebarScroll() {
        const sidebarScroll = document.querySelector('.sidebar-scroll');
        if (!sidebarScroll) return;
        
        // Suavizar scroll com mouse wheel
        sidebarScroll.addEventListener('wheel', function(e) {
            if (e.deltaY > 0 && this.scrollHeight - this.clientHeight <= this.scrollTop + 10) {
                return;
            }
            
            this.scrollTop += e.deltaY;
            e.preventDefault();
        }, { passive: false });
    }
    
    // Configurar eventos
    function setupEventListeners() {
        // Toggle Desktop (header)
        if (headerToggle) {
            headerToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                toggleSidebar();
            });
        }
        
        // Toggle Mobile
        if (mobileToggle) {
            mobileToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                if (isMobile()) {
                    if (sidebar.classList.contains('show')) {
                        closeMobileSidebar();
                    } else {
                        openMobileSidebar();
                    }
                }
            });
        }
        
        // Fechar sidebar ao clicar no overlay
        overlay.addEventListener('click', closeMobileSidebar);
        
        // Fechar sidebar ao clicar fora no mobile
        document.addEventListener('click', function(event) {
            if (isMobile() && 
                !sidebar.contains(event.target) && 
                !mobileToggle.contains(event.target) && 
                sidebar.classList.contains('show')) {
                closeMobileSidebar();
            }
        });
        
        // Fechar dropdowns ao clicar fora
        document.addEventListener('click', function(e) {
            if (!e.target.matches('.dropdown-toggle')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
        
        // Tecla ESC fecha sidebar no mobile
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isMobile() && sidebar.classList.contains('show')) {
                closeMobileSidebar();
            }
        });
        
        // Redimensionamento da janela
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (!isMobile() && sidebar.classList.contains('show')) {
                    closeMobileSidebar();
                }
                
                // Atualizar tooltips
                updateSidebarTooltips();
            }, 250);
        });
        
        // Prevenir múltiplos cliques rápidos
        const preventMultipleClicks = (function() {
            let lastClickTime = 0;
            const delay = 300;
            
            return function(callback) {
                const now = Date.now();
                if (now - lastClickTime > delay) {
                    lastClickTime = now;
                    callback();
                }
            };
        })();
        
        // Aplicar aos botões do menu
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', function(e) {
                if (isMobile()) {
                    preventMultipleClicks(() => {
                        setTimeout(() => closeMobileSidebar(), 100);
                    });
                }
            });
        });
    }
    
    // Configurar tooltips do usuário
    function setupUserTooltips() {
        const userName = document.querySelector('.user-name');
        const userRole = document.querySelector('.user-role');
        
        if (userName) {
            userName.setAttribute('title', userName.textContent);
            userName.setAttribute('data-bs-toggle', 'tooltip');
        }
        
        if (userRole) {
            userRole.setAttribute('title', userRole.textContent);
            userRole.setAttribute('data-bs-toggle', 'tooltip');
        }
    }
    
    // Inicializar tudo
    function init() {
        console.log('Admin Base inicializando...');
        
        initSidebar();
        setupEventListeners();
        setupSidebarScroll();
        setupUserTooltips();
        
        console.log('Admin Base inicializado com sucesso!');
    }
    
    // Alternar tema (opcional)
    window.toggleTheme = function() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    };
    
    // Inicializar quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Exportar funções para uso externo
    window.adminBase = {
        toggleSidebar: toggleSidebar,
        closeMobileSidebar: closeMobileSidebar,
        openMobileSidebar: openMobileSidebar,
        toggleTheme: window.toggleTheme
    };
});

// Suporte para navegadores antigos
if (!Element.prototype.matches) {
    Element.prototype.matches = 
        Element.prototype.msMatchesSelector || 
        Element.prototype.webkitMatchesSelector;
}