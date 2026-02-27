// Service worker vazio para evitar erros 404
self.addEventListener('install', function(event) {
    console.log('Service Worker instalado');
});

self.addEventListener('fetch', function(event) {
    // Não fazer nada, apenas ignorar
});