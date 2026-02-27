from django.urls import path
from . import views

urlpatterns = [
    # Público
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('acervo/', views.acervo, name='acervo'),
    path('informacoes/', views.informacoes, name='informacoes'),
    path('historia_cidade/', views.historia_cidade, name='historia_cidade'),
    path('eventos/', views.eventos_view, name='eventos'),
    path('acervo/prateleiras/', views.acervo_por_prateleira, name='acervo_prateleiras'),
    
    # Usuário
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('acervo-pdf/', views.acervo_pdf, name='acervo_pdf'),
    path('acervo-pdf/ler/<int:livro_id>/', views.ler_livro_pdf, name='ler_livro_pdf'),
    path('ler-pdf-simples/<int:livro_id>/', views.ler_pdf_simples, name='ler_pdf_simples'),
    path('teste-pdf/<int:livro_id>/', views.teste_pdf, name='teste_pdf'),
    path('visualizar/<int:livro_id>/', views.visualizar_pdf_seguro, name='visualizar_pdf_seguro'),
    path('pdf/<int:livro_id>/', views.servir_pdf_seguro, name='servir_pdf_seguro'),
    path('visualizar-imagens/<int:livro_id>/', views.visualizar_pdf_como_imagens, name='visualizar_imagens'),
    path('livro/<int:livro_id>/', views.detalhe_livro, name='detalhe_livro'),
    path('cadastro/', views.cadastro_usuario, name='cadastro_usuario'),

    # URLs para Solicitações de Empréstimo (Usuário)
    path('solicitar-emprestimo/<int:livro_id>/', views.solicitar_emprestimo, name='solicitar_emprestimo'),
    
    # Admin - URLs com prefixo 'sistema/'
    path('sistema/dashboard/', views.dashboard_admin, name='dashboard'),
    path('sistema/livros/cadastrar/', views.cadastro_livro, name='cadastro_livro'),
    path('sistema/livros/', views.lista_livros, name='lista_livros'),
    path('sistema/livros/editar/<int:livro_id>/', views.editar_livro, name='editar_livro'),
    path('sistema/usuarios/cadastrar/', views.cadastro_usuario_admin, name='cadastro_usuario_admin'),
    path('sistema/usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('sistema/emprestimos/novo/', views.realizar_emprestimo, name='realizar_emprestimo'),
    path('sistema/emprestimos/', views.lista_emprestimos, name='lista_emprestimos'),
    path('sistema/emprestimos/historico/', views.historico_emprestimos, name='historico_emprestimos'),
    
    # CORREÇÃO: Use 'devolver_livro' em vez de 'devolver_emprestimo'
    path('sistema/emprestimos/devolver/<int:emprestimo_id>/', views.devolver_livro, name='devolver_livro'),
    
    path('sistema/relatorios/', views.relatorios, name='relatorios'),
    path('sistema/configuracoes/', views.configurar_biblioteca, name='configurar_biblioteca'),
    
    # URLs para Livros PDF (Admin)
    path('sistema/livros-pdf/cadastrar/', views.cadastro_livro_pdf, name='cadastro_livro_pdf'),
    path('sistema/livros-pdf/', views.lista_livros_pdf, name='lista_livros_pdf'),
    path('sistema/livros-pdf/editar/<int:livro_id>/', views.editar_livro_pdf, name='editar_livro_pdf'),
    path('acervo-pdf/visualizar/<int:livro_id>/', views.visualizar_pdf, name='visualizar_pdf'),   
    
    path('media/pdf_livros/<path:path>', views.servir_pdf, name='servir_pdf'),
    
    # URLs para Eventos (Admin)
    path('sistema/eventos/cadastrar/', views.cadastro_evento, name='cadastro_evento'),
    path('sistema/eventos/', views.lista_eventos_admin, name='lista_eventos_admin'),
    path('sistema/eventos/editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    path('sistema/eventos/excluir/<int:evento_id>/', views.excluir_evento, name='excluir_evento'),
    
    # URLs para empréstimos (renovação)
    path('sistema/emprestimos/renovar/<int:emprestimo_id>/', views.renovar_emprestimo, name='renovar_emprestimo'),

    # APIs
    path('api/livro/<int:livro_id>/', views.api_livro_info, name='api_livro_info'),
    path('api/usuario/<int:usuario_id>/', views.api_usuario_info, name='api_usuario_info'),
    path('api/livros/buscar/', views.api_buscar_livros, name='api_buscar_livros'),
    path('api/usuarios/buscar/', views.api_buscar_usuarios, name='api_buscar_usuarios'),
    path('api/whatsapp/notificar/', views.api_whatsapp_notificacao, name='api_whatsapp_notificacao'),
    path('api/emprestimo/<int:emprestimo_id>/', views.api_emprestimo_detalhes, name='api_emprestimo_detalhes'),

    # URLs para Prateleiras (Admin)
    path('sistema/prateleiras/', views.lista_prateleiras, name='lista_prateleiras'),
    path('sistema/prateleiras/cadastrar/', views.cadastro_prateleira, name='cadastro_prateleira'),
    path('sistema/prateleiras/editar/<int:prateleira_id>/', views.editar_prateleira, name='editar_prateleira'),
    path('sistema/prateleiras/excluir/<int:prateleira_id>/', views.excluir_prateleira, name='excluir_prateleira'),
    path('sistema/prateleiras/detalhes/<int:prateleira_id>/', views.detalhes_prateleira, name='detalhes_prateleira'),

    # URLs para Editoras (Admin)
    path('sistema/editoras/', views.lista_editoras, name='lista_editoras'),
    path('sistema/editoras/cadastrar/', views.cadastro_editora, name='cadastro_editora'),
    path('sistema/editoras/editar/<int:editora_id>/', views.editar_editora, name='editar_editora'),
    path('sistema/editoras/excluir/<int:editora_id>/', views.excluir_editora, name='excluir_editora'),
    path('sistema/editoras/detalhes/<int:editora_id>/', views.detalhes_editora, name='detalhes_editora'),

    # URLs para Solicitações de Empréstimo (Admin)
    path('sistema/solicitacoes/', views.lista_solicitacoes, name='lista_solicitacoes'),
    path('sistema/solicitacoes/processar/<int:solicitacao_id>/', views.processar_solicitacao, name='processar_solicitacao'),
]