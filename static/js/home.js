/**
 * Scripts específicos para a página home
 * Biblioteca Pública Municipal
 */

document.addEventListener('DOMContentLoaded', function() {
    // ===== SCROLL ANIMATIONS =====
    function initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        // Observe all animate-on-scroll elements
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    // ===== NAVBAR SCROLL EFFECT =====
    function initNavbarScroll() {
        const navbar = document.querySelector('.navbar');
        
        if (navbar) {
            window.addEventListener('scroll', function() {
                if (window.scrollY > 100) {
                    navbar.style.padding = '10px 0';
                    navbar.style.background = 'rgba(44, 62, 80, 0.98)';
                } else {
                    navbar.style.padding = '15px 0';
                    navbar.style.background = 'rgba(44, 62, 80, 0.95)';
                }
            });
        }
    }

    // ===== STATISTICS COUNTER ANIMATION =====
    function initStatisticsCounter() {
        const statNumbers = document.querySelectorAll('.stat-number');
        
        statNumbers.forEach(stat => {
            const target = parseInt(stat.textContent);
            const increment = target / 100;
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    clearInterval(timer);
                    stat.textContent = target + '+';
                } else {
                    stat.textContent = Math.floor(current) + '+';
                }
            }, 30);
        });
    }

    // ===== BOOK CARDS HOVER EFFECT =====
    function initBookCards() {
        const bookCards = document.querySelectorAll('.book-card');
        
        bookCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.zIndex = '10';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.zIndex = '1';
            });
        });
    }

    // ===== SMOOTH SCROLL FOR ANCHOR LINKS =====
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                
                // Only handle anchor links, not empty href
                if (href === '#' || !href.startsWith('#')) return;
                
                e.preventDefault();
                const targetId = href;
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // ===== CTA BUTTON PULSE EFFECT =====
    function initCTAPulse() {
        const ctaButton = document.querySelector('.btn-cta');
        
        if (ctaButton) {
            // Add pulse animation every 3 seconds
            setInterval(() => {
                ctaButton.classList.add('pulse');
                setTimeout(() => {
                    ctaButton.classList.remove('pulse');
                }, 600);
            }, 3000);
            
            // Add CSS for pulse effect
            const style = document.createElement('style');
            style.textContent = `
                .btn-cta.pulse {
                    animation: pulse 0.6s ease-in-out;
                }
                
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // ===== LAZY LOAD IMAGES =====
    function initLazyLoad() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        }
    }

    // ===== INITIALIZE ALL FUNCTIONS =====
    function init() {
        initScrollAnimations();
        initNavbarScroll();
        initBookCards();
        initSmoothScroll();
        initCTAPulse();
        initLazyLoad();
        
        // Start counter animation after page load
        setTimeout(initStatisticsCounter, 1000);
        
        // Add loading animation for buttons
        document.querySelectorAll('.btn-hero, .btn-cta').forEach(btn => {
            btn.addEventListener('click', function(e) {
                if (this.getAttribute('href') === '#' || 
                    this.getAttribute('href') === 'javascript:void(0)') {
                    return;
                }
                
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Carregando...';
                this.style.pointerEvents = 'none';
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.style.pointerEvents = 'auto';
                }, 2000);
            });
        });
    }

    // Initialize when DOM is ready
    init();

    // ===== UTILITY FUNCTIONS =====
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

    // Debounce scroll events for performance
    window.addEventListener('scroll', debounce(function() {
        // Additional scroll-based functionality can go here
    }, 10));

    // ===== BOOK SEARCH FUNCTIONALITY =====
    function initBookSearch() {
        const searchInput = document.querySelector('#bookSearch');
        const bookCards = document.querySelectorAll('.book-card');
        
        if (searchInput && bookCards.length > 0) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase().trim();
                
                bookCards.forEach(card => {
                    const title = card.querySelector('.book-title').textContent.toLowerCase();
                    const author = card.querySelector('.book-author').textContent.toLowerCase();
                    const category = card.querySelector('.book-category').textContent.toLowerCase();
                    
                    const matches = title.includes(searchTerm) || 
                                   author.includes(searchTerm) || 
                                   category.includes(searchTerm);
                    
                    card.style.display = matches ? 'block' : 'none';
                    
                    // Add fade animation
                    if (matches) {
                        card.style.animation = 'fadeInUp 0.5s ease';
                    }
                });
            });
        }
    }

    // Initialize book search if element exists
    setTimeout(() => {
        if (document.querySelector('#bookSearch')) {
            initBookSearch();
        }
    }, 100);
});

// ===== WINDOW LOAD EVENT =====
window.addEventListener('load', function() {
    // Remove preloader if exists
    const preloader = document.querySelector('.preloader');
    if (preloader) {
        preloader.style.opacity = '0';
        setTimeout(() => {
            preloader.style.display = 'none';
        }, 500);
    }
    
    // Add loaded class to body for CSS transitions
    document.body.classList.add('loaded');
});