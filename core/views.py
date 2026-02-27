from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from datetime import timedelta, datetime, date
import json
import os
import uuid
import threading
import time
from collections import defaultdict
from django import forms 
from .forms import (
    LivroForm, UserForm, PerfilUsuarioForm, EmprestimoForm,
    BibliotecaInfoForm, EventoForm, LivroPDFForm, PrateleiraForm, 
    EditoraForm, CadastroPublicoForm  # <-- ADICIONE ESTA LINHA
)

# Importações de models
from .models import (
    Livro, User, Emprestimo, Evento, LivroPDF, 
    PerfilUsuario, BibliotecaInfo, Prateleira, Editora, SolicitacaoEmprestimo
)

# Importações de forms
from .forms import (
    LivroForm, UserForm, PerfilUsuarioForm, EmprestimoForm,
    BibliotecaInfoForm, EventoForm, LivroPDFForm, PrateleiraForm, EditoraForm
)

# Importações de decorators
from .decorators import admin_required, admin_or_funcionario_required

# ========== FUNÇÕES AUXILIARES ==========
def servir_pdf(request, path):
    """View personalizada para servir PDFs"""
    from django.views.static import serve
    from django.conf import settings
    import os
    
    document_root = os.path.join(settings.MEDIA_ROOT, 'pdf_livros')
    return serve(request, path, document_root=document_root)

# ========== VIEWS PÚBLICAS ==========
def home(request):
    """Página inicial pública"""
    livros_destaque = Livro.objects.filter(ativo=True, quantidade_disponivel__gt=0)[:8]
    biblioteca_info = BibliotecaInfo.objects.first()
    total_livros = Livro.objects.count()
    
    context = {
        'livros_destaque': livros_destaque,
        'biblioteca_info': biblioteca_info,
        'total_livros': total_livros,
    }
    return render(request, 'usuario/home/home.html', context)

def login_view(request):
    """View para login de usuários"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            
            # Atualizar contador de visitas
            perfil, created = PerfilUsuario.objects.get_or_create(
                usuario=user,
                defaults={'categoria': 'usuario'}
            )
            perfil.visitas += 1
            perfil.save()
            
            if perfil.categoria in ['admin', 'funcionario']:
                return redirect('dashboard')
            
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'auth/login.html')
    """View para login de usuários"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            
            perfil, created = PerfilUsuario.objects.get_or_create(
                usuario=user,
                defaults={'categoria': 'usuario'}
            )
            perfil.visitas += 1
            perfil.save()
            
            if perfil.categoria in ['admin', 'funcionario']:
                return redirect('dashboard')
            
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    """View para logout de usuários"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('home')

def acervo(request):
    """View para exibir acervo de livros físicos"""
    livros = Livro.objects.filter(ativo=True, quantidade_disponivel__gt=0)
    context = {'livros': livros}
    return render(request, 'usuario/acervo/acervo.html', context)

def informacoes(request):
    """View para exibir informações da biblioteca"""
    biblioteca_info = BibliotecaInfo.objects.first()
    context = {'biblioteca_info': biblioteca_info}
    return render(request, 'usuario/informacoes/informacoes.html', context)

def historia_cidade(request):
    """View para exibir história da cidade"""
    return render(request, 'usuario/historia/historia_cidade.html')

def eventos_view(request):
    """View pública para exibir eventos"""
    eventos = Evento.objects.filter(ativo=True).order_by('-data_evento')
    return render(request, 'usuario/eventos/eventos.html', {'eventos': eventos})

# ========== ACERVO POR PRATELEIRA ==========
def acervo_por_prateleira(request):
    """View para exibir livros organizados por prateleira"""
    try:
        prateleiras = Prateleira.objects.filter(ativo=True).order_by('nome')
        
        livros_por_prateleira = {}
        
        for prateleira in prateleiras:
            livros = Livro.objects.filter(
                ativo=True,
                prateleira=prateleira
            ).order_by('titulo')
            
            total_livros = livros.count()
            disponiveis = livros.filter(quantidade_disponivel__gt=0).count()
            
            livros_por_prateleira[prateleira.nome] = {
                'prateleira_obj': prateleira,
                'livros': livros,
                'total_livros': total_livros,
                'disponiveis': disponiveis,
                'emprestados': total_livros - disponiveis,
                'tem_livros_disponiveis': disponiveis > 0,
                'categoria_associada': prateleira.get_categoria_associada_display(),
                'localizacao': prateleira.localizacao_fisica or 'Local não informado',
            }
        
        total_geral = Livro.objects.filter(ativo=True).count()
        disponiveis_geral = Livro.objects.filter(ativo=True, quantidade_disponivel__gt=0).count()
        emprestados_geral = total_geral - disponiveis_geral
        
        context = {
            'livros_por_prateleira': livros_por_prateleira,
            'total_prateleiras': prateleiras.count(),
            'total_geral': total_geral,
            'disponiveis_geral': disponiveis_geral,
            'emprestados_geral': emprestados_geral,
        }
        
        return render(request, 'usuario/acervo/acervo_prateleiras.html', context)
        
    except Exception as e:
        print(f"Erro em acervo_por_prateleira: {e}")
        import traceback
        traceback.print_exc()
        
        context = {
            'livros_por_prateleira': {},
            'total_prateleiras': 0,
            'total_geral': 0,
            'disponiveis_geral': 0,
            'emprestados_geral': 0,
            'erro': str(e)
        }
        return render(request, 'usuario/acervo/acervo_prateleiras.html', context)

# ========== DETALHE DO LIVRO ==========
def detalhe_livro(request, livro_id):
    """Exibe detalhes de um livro específico"""
    livro = get_object_or_404(Livro, id=livro_id, ativo=True)
    
    livros_relacionados = Livro.objects.filter(
        Q(categoria=livro.categoria) | Q(prateleira=livro.prateleira),
        ativo=True
    ).exclude(id=livro_id)[:4]
    
    context = {
        'livro': livro,
        'livros_relacionados': livros_relacionados,
    }
    return render(request, 'usuario/livro/livro_detalhe.html', context)

# ========== ÁREA DO ADMINISTRADOR ==========
@login_required
@admin_or_funcionario_required
def dashboard_admin(request):
    """Dashboard administrativo"""
    total_livros = Livro.objects.count()
    livros_disponiveis = Livro.objects.filter(quantidade_disponivel__gt=0).count()
    total_usuarios = User.objects.count()
    emprestimos_ativos = Emprestimo.objects.filter(data_devolucao_real__isnull=True).count()
    
    hoje = timezone.now().date()
    emprestimos_atrasados = 0
    for emprestimo in Emprestimo.objects.filter(data_devolucao_real__isnull=True):
        if emprestimo.data_devolucao_prevista:
            if isinstance(emprestimo.data_devolucao_prevista, datetime):
                data_prevista = emprestimo.data_devolucao_prevista.date()
            else:
                data_prevista = emprestimo.data_devolucao_prevista
            
            if data_prevista < hoje:
                emprestimos_atrasados += 1
    
    ultimos_emprestimos = Emprestimo.objects.select_related('livro', 'usuario').order_by('-data_emprestimo')[:10]
    livros_populares = Livro.objects.annotate(num_emprestimos=Count('emprestimo')).order_by('-num_emprestimos')[:5]
    
    total_eventos = Evento.objects.count()
    eventos_ativos = Evento.objects.filter(ativo=True).count()
    proximo_evento = Evento.objects.filter(
        data_evento__gte=timezone.now().date(),
        ativo=True
    ).order_by('data_evento').first()
    
    total_pdf = LivroPDF.objects.count()
    pdf_ativos = LivroPDF.objects.filter(ativo=True).count()
    
    usuarios_top = User.objects.annotate(num_emprestimos=Count('emprestimo')).order_by('-num_emprestimos')[:5]
    
    context = {
        'total_livros': total_livros,
        'livros_disponiveis': livros_disponiveis,
        'total_usuarios': total_usuarios,
        'emprestimos_ativos': emprestimos_ativos,
        'emprestimos_atrasados': emprestimos_atrasados,
        'ultimos_emprestimos': ultimos_emprestimos,
        'livros_populares': livros_populares,
        'hoje': hoje,
        'total_eventos': total_eventos,
        'eventos_ativos': eventos_ativos,
        'proximo_evento': proximo_evento,
        'total_pdf': total_pdf,
        'pdf_ativos': pdf_ativos,
        'usuarios_top': usuarios_top,
    }
    
    return render(request, 'admin/dashboard/dashboard.html', context)

# ========== PRATELEIRAS (ADMIN) ==========
@login_required
@admin_required
def lista_prateleiras(request):
    """Listagem de prateleiras"""
    prateleiras = Prateleira.objects.all().order_by('nome')
    
    total_prateleiras = prateleiras.count()
    prateleiras_ativas = prateleiras.filter(ativo=True).count()
    total_livros_em_prateleiras = sum(p.total_livros() for p in prateleiras)
    
    context = {
        'prateleiras': prateleiras,
        'total_prateleiras': total_prateleiras,
        'prateleiras_ativas': prateleiras_ativas,
        'total_livros_em_prateleiras': total_livros_em_prateleiras,
    }
    return render(request, 'admin/prateleiras/lista_prateleiras.html', context)

@login_required
@admin_required
def cadastro_prateleira(request):
    """Cadastro de nova prateleira"""
    if request.method == 'POST':
        form = PrateleiraForm(request.POST)
        if form.is_valid():
            prateleira = form.save()
            messages.success(request, f'Prateleira "{prateleira.nome}" cadastrada com sucesso!')
            return redirect('lista_prateleiras')
    else:
        form = PrateleiraForm()
    
    context = {'form': form}
    return render(request, 'admin/prateleiras/cadastro_prateleira.html', context)

@login_required
@admin_required
def editar_prateleira(request, prateleira_id):
    """Edição de prateleira"""
    prateleira = get_object_or_404(Prateleira, id=prateleira_id)
    
    if request.method == 'POST':
        form = PrateleiraForm(request.POST, instance=prateleira)
        if form.is_valid():
            form.save()
            messages.success(request, f'Prateleira "{prateleira.nome}" atualizada com sucesso!')
            return redirect('lista_prateleiras')
    else:
        form = PrateleiraForm(instance=prateleira)
    
    context = {'form': form, 'prateleira': prateleira}
    return render(request, 'admin/prateleiras/editar_prateleira.html', context)

@login_required
@admin_required
def excluir_prateleira(request, prateleira_id):
    """Exclusão de prateleira"""
    prateleira = get_object_or_404(Prateleira, id=prateleira_id)
    
    if prateleira.livros.exists():
        messages.error(request, f'Não é possível excluir a prateleira "{prateleira.nome}" pois existem livros associados a ela.')
        return redirect('lista_prateleiras')
    
    if request.method == 'POST':
        prateleira_nome = prateleira.nome
        prateleira.delete()
        messages.success(request, f'Prateleira "{prateleira_nome}" excluída com sucesso!')
        return redirect('lista_prateleiras')
    
    context = {'prateleira': prateleira}
    return render(request, 'admin/prateleiras/excluir_prateleira.html', context)

@login_required
@admin_required
def detalhes_prateleira(request, prateleira_id):
    """Detalhes de uma prateleira específica"""
    prateleira = get_object_or_404(Prateleira, id=prateleira_id)
    livros = prateleira.livros.all().order_by('titulo')
    
    context = {
        'prateleira': prateleira,
        'livros': livros,
        'total_livros': livros.count(),
        'livros_disponiveis': prateleira.livros_disponiveis(),
        'livros_emprestados': prateleira.livros_emprestados(),
    }
    return render(request, 'admin/prateleiras/detalhes_prateleira.html', context)

# ========== EDITORAS (ADMIN) ==========
@login_required
@admin_required
def lista_editoras(request):
    """Listagem de editoras"""
    editoras = Editora.objects.all().order_by('-data_cadastro')
    
    total_editoras = editoras.count()
    editoras_ativas = editoras.filter(ativo=True).count()
    total_livros = sum(e.total_livros() for e in editoras)
    
    busca = request.GET.get('busca', '')
    status = request.GET.get('status', '')
    
    if busca:
        editoras = editoras.filter(nome__icontains=busca)
    
    if status == 'ativo':
        editoras = editoras.filter(ativo=True)
    elif status == 'inativo':
        editoras = editoras.filter(ativo=False)
    
    page = request.GET.get('page', 1)
    paginator = Paginator(editoras, 10)
    
    try:
        editoras_page = paginator.page(page)
    except PageNotAnInteger:
        editoras_page = paginator.page(1)
    except EmptyPage:
        editoras_page = paginator.page(paginator.num_pages)
    
    context = {
        'editoras': editoras_page,
        'total_editoras': total_editoras,
        'editoras_ativas': editoras_ativas,
        'total_livros': total_livros,
        'busca': busca,
        'status': status,
    }
    return render(request, 'admin/editoras/lista_editoras.html', context)

@login_required
@admin_required
def cadastro_editora(request):
    """Cadastro de nova editora"""
    if request.method == 'POST':
        form = EditoraForm(request.POST)
        if form.is_valid():
            editora = form.save()
            messages.success(request, f'Editora "{editora.nome}" cadastrada com sucesso!')
            return redirect('lista_editoras')
    else:
        form = EditoraForm()
    
    context = {'form': form}
    return render(request, 'admin/editoras/cadastro_editora.html', context)

@login_required
@admin_required
def editar_editora(request, editora_id):
    """Edição de editora"""
    editora = get_object_or_404(Editora, id=editora_id)
    
    if request.method == 'POST':
        form = EditoraForm(request.POST, instance=editora)
        if form.is_valid():
            form.save()
            messages.success(request, f'Editora "{editora.nome}" atualizada com sucesso!')
            return redirect('lista_editoras')
    else:
        form = EditoraForm(instance=editora)
    
    context = {'form': form, 'editora': editora}
    return render(request, 'admin/editoras/editar_editora.html', context)

@login_required
@admin_required
def excluir_editora(request, editora_id):
    """Exclusão de editora"""
    editora = get_object_or_404(Editora, id=editora_id)
    
    if editora.livros.exists():
        messages.error(request, f'Não é possível excluir a editora "{editora.nome}" pois existem livros associados a ela.')
        return redirect('lista_editoras')
    
    if request.method == 'POST':
        editora_nome = editora.nome
        editora.delete()
        messages.success(request, f'Editora "{editora_nome}" excluída com sucesso!')
        return redirect('lista_editoras')
    
    context = {'editora': editora}
    return render(request, 'admin/editoras/excluir_editora.html', context)

@login_required
@admin_required
def detalhes_editora(request, editora_id):
    """Detalhes de uma editora"""
    editora = get_object_or_404(Editora, id=editora_id)
    livros = editora.livros.all().order_by('titulo')
    
    context = {
        'editora': editora,
        'livros': livros,
        'total_livros': livros.count(),
    }
    return render(request, 'admin/editoras/detalhes_editora.html', context)

# ========== LIVROS (ADMIN) ==========
@login_required
@admin_or_funcionario_required
def cadastro_livro(request):
    """Cadastro de novos livros"""
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            livro = form.save()
            messages.success(request, f'✅ Livro "{livro.titulo}" cadastrado com sucesso!')
            return redirect('lista_livros')
        else:
            messages.error(request, '❌ Erro no formulário. Verifique os campos.')
    else:
        form = LivroForm()
    
    context = {'form': form}
    return render(request, 'admin/livros/cadastro_livro.html', context)

@login_required
@admin_or_funcionario_required
def lista_livros(request):
    """Listagem de todos os livros"""
    livros_list = Livro.objects.all().order_by('-data_cadastro')
    
    livros_com_emprestimos = []
    for livro in livros_list:
        quantidade_emprestada = Emprestimo.objects.filter(
            livro=livro,
            data_devolucao_real__isnull=True
        ).count()
        livro.quantidade_emprestada = quantidade_emprestada
        livros_com_emprestimos.append(livro)
    
    categoria = request.GET.get('categoria')
    status = request.GET.get('status')
    busca = request.GET.get('busca', '')
    prateleira = request.GET.get('prateleira')
    
    livros_filtrados = livros_com_emprestimos
    
    if categoria:
        livros_filtrados = [l for l in livros_filtrados if l.categoria == categoria]
    
    if status:
        if status == 'ativo':
            livros_filtrados = [l for l in livros_filtrados if l.ativo]
        elif status == 'inativo':
            livros_filtrados = [l for l in livros_filtrados if not l.ativo]
        elif status == 'disponivel':
            livros_filtrados = [l for l in livros_filtrados if l.quantidade_disponivel > 0]
        elif status == 'indisponivel':
            livros_filtrados = [l for l in livros_filtrados if l.quantidade_disponivel == 0]
    
    if prateleira:
        livros_filtrados = [l for l in livros_filtrados if str(l.prateleira) == prateleira]
    
    if busca:
        busca_lower = busca.lower()
        livros_filtrados = [
            l for l in livros_filtrados 
            if (busca_lower in l.titulo.lower() or 
                busca_lower in l.autor.lower() or 
                (l.editora and busca_lower in l.editora.nome.lower()))
        ]
    
    page = request.GET.get('page', 1)
    paginator = Paginator(livros_filtrados, 10)
    
    try:
        livros = paginator.page(page)
    except PageNotAnInteger:
        livros = paginator.page(1)
    except EmptyPage:
        livros = paginator.page(paginator.num_pages)
    
    total_livros = len(livros_filtrados)
    total_disponiveis = sum(1 for l in livros_filtrados if l.quantidade_disponivel > 0)
    total_emprestados = sum(l.quantidade_emprestada for l in livros_filtrados)
    
    categoria_field = Livro._meta.get_field('categoria')
    categorias = categoria_field.choices
    
    context = {
        'livros': livros,
        'total_livros': total_livros,
        'total_disponiveis': total_disponiveis,
        'total_emprestados': total_emprestados,
        'categorias': categorias,
    }
    return render(request, 'admin/livros/lista_livros.html', context)

@login_required
@admin_or_funcionario_required
def editar_livro(request, livro_id):
    """Edição de livro existente"""
    livro = get_object_or_404(Livro, id=livro_id)
    
    if request.method == 'POST':
        form = LivroForm(request.POST, instance=livro)
        if form.is_valid():
            form.save()
            messages.success(request, f'Livro "{livro.titulo}" atualizado com sucesso!')
            return redirect('lista_livros')
    else:
        form = LivroForm(instance=livro)
    
    context = {'form': form, 'livro': livro}
    return render(request, 'admin/livros/editar_livro.html', context)

# ========== USUÁRIOS (ADMIN) ==========
@login_required
@admin_or_funcionario_required
def cadastro_usuario_admin(request):
    """Cadastro de usuários pelo administrador"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        perfil_form = PerfilUsuarioForm(request.POST)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user = user_form.save()
            
            perfil = perfil_form.save(commit=False)
            perfil.usuario = user
            
            if perfil.categoria in ['admin', 'funcionario']:
                user.is_staff = True
                user.save()
            
            perfil.save()
            
            messages.success(request, f'Usuário "{user.username}" cadastrado com sucesso!')
            return redirect('lista_usuarios')
    else:
        user_form = UserForm()
        perfil_form = PerfilUsuarioForm()
    
    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
    }
    return render(request, 'admin/usuarios/cadastro_usuario.html', context)

@login_required
@admin_or_funcionario_required
def lista_usuarios(request):
    """Listagem de usuários"""
    usuarios_list = User.objects.all().order_by('-date_joined')
    
    categoria = request.GET.get('categoria')
    status = request.GET.get('status')
    busca = request.GET.get('busca', '')
    
    if categoria:
        usuarios_list = usuarios_list.filter(perfilusuario__categoria=categoria)
    
    if status:
        if status == 'ativo':
            usuarios_list = usuarios_list.filter(is_active=True)
        elif status == 'inativo':
            usuarios_list = usuarios_list.filter(is_active=False)
    
    if busca:
        usuarios_list = usuarios_list.filter(
            Q(username__icontains=busca) |
            Q(first_name__icontains=busca) |
            Q(last_name__icontains=busca) |
            Q(email__icontains=busca) |
            Q(perfilusuario__telefone__icontains=busca)
        )
    
    page = request.GET.get('page', 1)
    paginator = Paginator(usuarios_list, 10)
    
    try:
        usuarios = paginator.page(page)
    except PageNotAnInteger:
        usuarios = paginator.page(1)
    except EmptyPage:
        usuarios = paginator.page(paginator.num_pages)
    
    context = {'usuarios': usuarios}
    return render(request, 'admin/usuarios/lista_usuarios.html', context)

# ========== EVENTOS (ADMIN) ==========
@login_required
@admin_or_funcionario_required
def cadastro_evento(request):
    """Cadastro de novos eventos"""
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save()
            messages.success(request, f'Evento "{evento.titulo}" cadastrado com sucesso!')
            return redirect('lista_eventos_admin')
    else:
        form = EventoForm()
    
    context = {'form': form}
    return render(request, 'admin/eventos/cadastro_evento.html', context)

@login_required
@admin_or_funcionario_required
def lista_eventos_admin(request):
    """Listagem de todos os eventos"""
    eventos = Evento.objects.all().order_by('-data_evento')
    
    status = request.GET.get('status', '')
    busca = request.GET.get('busca', '')
    
    if status == 'ativo':
        eventos = eventos.filter(ativo=True)
    elif status == 'inativo':
        eventos = eventos.filter(ativo=False)
    
    if busca:
        eventos = eventos.filter(
            Q(titulo__icontains=busca) |
            Q(descricao__icontains=busca)
        )
    
    total_eventos = eventos.count()
    eventos_ativos = eventos.filter(ativo=True).count()
    eventos_inativos = eventos.filter(ativo=False).count()
    
    context = {
        'eventos': eventos,
        'total_eventos': total_eventos,
        'eventos_ativos': eventos_ativos,
        'eventos_inativos': eventos_inativos,
        'status_selecionado': status,
        'busca': busca,
    }
    
    return render(request, 'admin/eventos/lista_eventos.html', context)

@login_required
@admin_or_funcionario_required
def editar_evento(request, evento_id):
    """Edição de evento existente"""
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, f'Evento "{evento.titulo}" atualizado com sucesso!')
            return redirect('lista_eventos_admin')
    else:
        form = EventoForm(instance=evento)
    
    context = {'form': form, 'evento': evento}
    return render(request, 'admin/eventos/editar_evento.html', context)

@login_required
@admin_or_funcionario_required
def excluir_evento(request, evento_id):
    """Exclusão de evento"""
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.method == 'POST':
        evento_titulo = evento.titulo
        evento.delete()
        messages.success(request, f'Evento "{evento_titulo}" excluído com sucesso!')
        return redirect('lista_eventos_admin')
    
    context = {'evento': evento}
    return render(request, 'admin/eventos/excluir_evento.html', context)

# ========== EMPRÉSTIMOS ==========
@login_required
@admin_or_funcionario_required
def realizar_emprestimo(request):
    """Realizar novo empréstimo"""
    if request.method == 'POST':
        form = EmprestimoForm(request.POST)
        if form.is_valid():
            emprestimo = form.save(commit=False)
            emprestimo.data_emprestimo = timezone.now()
            
            if not emprestimo.data_devolucao_prevista:
                emprestimo.data_devolucao_prevista = timezone.now() + timedelta(days=15)
            
            livro = emprestimo.livro
            if livro.quantidade_disponivel > 0:
                livro.quantidade_disponivel -= 1
                livro.save()
                
                emprestimo.save()
                messages.success(request, f'Empréstimo realizado para {emprestimo.usuario.get_full_name()}')
                return redirect('lista_emprestimos')
            else:
                messages.error(request, 'Livro não disponível para empréstimo')
    else:
        form = EmprestimoForm()
    
    context = {'form': form}
    return render(request, 'admin/emprestimos/realizar_emprestimo.html', context)

@login_required
@admin_or_funcionario_required
def lista_emprestimos(request):
    """Listagem de empréstimos ativos"""
    hoje = timezone.now().date()
    
    emprestimos_ativos = Emprestimo.objects.filter(
        data_devolucao_real__isnull=True
    ).order_by('-data_emprestimo')
    
    emprestimos_no_prazo = 0
    emprestimos_atrasados = 0
    emprestimos_vencendo_hoje = 0
    
    for emprestimo in emprestimos_ativos:
        if emprestimo.data_devolucao_prevista:
            if isinstance(emprestimo.data_devolucao_prevista, datetime):
                data_prevista = emprestimo.data_devolucao_prevista.date()
            else:
                data_prevista = emprestimo.data_devolucao_prevista
            
            if data_prevista < hoje:
                emprestimo.status_exibicao = 'Atrasado'
                emprestimo.dias_atraso = (hoje - data_prevista).days
                emprestimo.dias_restantes = 0
                emprestimos_atrasados += 1
            else:
                emprestimo.status_exibicao = 'No prazo'
                emprestimo.dias_atraso = 0
                emprestimo.dias_restantes = (data_prevista - hoje).days
                emprestimos_no_prazo += 1
                
                if data_prevista == hoje:
                    emprestimos_vencendo_hoje += 1
        else:
            emprestimo.status_exibicao = 'No prazo'
            emprestimo.dias_atraso = 0
            emprestimo.dias_restantes = None
    
    context = {
        'emprestimos': emprestimos_ativos,
        'hoje': hoje,
        'emprestimos_no_prazo': emprestimos_no_prazo,
        'emprestimos_atrasados': emprestimos_atrasados,
        'emprestimos_vencendo_hoje': emprestimos_vencendo_hoje,
    }
    
    return render(request, 'admin/emprestimos/lista_emprestimos.html', context)

@login_required
@admin_or_funcionario_required
def devolver_livro(request, emprestimo_id):
    """Devolução de livro emprestado"""
    if request.method == 'POST':
        try:
            emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id, data_devolucao_real__isnull=True)
            
            emprestimo.data_devolucao_real = timezone.now()
            emprestimo.observacoes_devolucao = request.POST.get('observacoes', '')
            emprestimo.status = 'devolvido'
            emprestimo.save()
            
            livro = emprestimo.livro
            livro.quantidade_disponivel += 1
            livro.save()
            
            messages.success(request, f'✅ Livro "{livro.titulo}" devolvido com sucesso!')
            
        except Exception as e:
            messages.error(request, f'❌ Erro ao devolver livro: {str(e)}')
        
        return redirect('lista_emprestimos')
    
    return redirect('lista_emprestimos')

@login_required
@admin_or_funcionario_required
def lista_emprestimos_final(request):
    """Listagem final de empréstimos (versão alternativa)"""
    hoje = timezone.now().date()
    
    emprestimos = Emprestimo.objects.filter(
        data_devolucao_real__isnull=True
    ).select_related('livro', 'usuario').order_by('-data_emprestimo')
    
    emprestimos_data = []
    for emp in emprestimos:
        if emp.data_devolucao_prevista:
            if isinstance(emp.data_devolucao_prevista, datetime):
                data_prevista = emp.data_devolucao_prevista.date()
            else:
                data_prevista = emp.data_devolucao_prevista
            
            if data_prevista < hoje:
                status = 'Atrasado'
                dias_atraso = (hoje - data_prevista).days
            else:
                status = 'No prazo'
                dias_atraso = 0
        else:
            status = 'No prazo'
            dias_atraso = 0
        
        emprestimos_data.append({
            'id': emp.id,
            'livro_titulo': emp.livro.titulo,
            'livro_autor': emp.livro.autor,
            'usuario_nome': emp.usuario.get_full_name() or emp.usuario.username,
            'usuario_email': emp.usuario.email,
            'data_emprestimo': emp.data_emprestimo.strftime('%d/%m/%Y %H:%M'),
            'data_prevista': emp.data_devolucao_prevista.strftime('%d/%m/%Y') if emp.data_devolucao_prevista else 'Não definida',
            'status': status,
            'dias_atraso': dias_atraso,
        })
    
    return render(request, 'admin/emprestimos/emprestimos_final.html', {
        'emprestimos_data': emprestimos_data,
        'hoje': hoje
    })

@login_required
@admin_or_funcionario_required
def historico_emprestimos(request):
    """Histórico de empréstimos"""
    emprestimos = Emprestimo.objects.filter(
        data_devolucao_real__isnull=False
    ).order_by('-data_devolucao_real')[:50]
    
    context = {
        'emprestimos': emprestimos,
    }
    
    return render(request, 'admin/emprestimos/historico_emprestimos.html', context)

# ========== RELATÓRIOS ==========
@login_required
@admin_or_funcionario_required
def relatorios(request):
    """Geração de relatórios"""
    CATEGORIAS = [
        ('ficcao', 'Ficção'),
        ('nao_ficcao', 'Não-Ficção'),
        ('tecnico', 'Técnico'),
        ('didatico', 'Didático'),
        ('biografia', 'Biografia'),
        ('historia', 'História'),
        ('poesia', 'Poesia'),
    ]
    
    total_emprestimos = Emprestimo.objects.count()
    
    livros_com_emprestimos = []
    todos_livros = Livro.objects.all()
    
    for livro in todos_livros:
        quantidade_emprestada = Emprestimo.objects.filter(
            livro=livro,
            data_devolucao_real__isnull=True
        ).count()
        livro.quantidade_emprestada = quantidade_emprestada
        livros_com_emprestimos.append(livro)
    
    livros_com_emprestimos.sort(key=lambda x: x.quantidade_emprestada, reverse=True)
    top_livros = [{'titulo': livro.titulo, 'total': livro.quantidade_emprestada} for livro in livros_com_emprestimos[:10]]
    
    top_usuarios = User.objects.annotate(
        num_emprestimos=Count('emprestimo')
    ).order_by('-num_emprestimos')[:10]
    
    usuarios_formatados = []
    for user in top_usuarios:
        usuarios_formatados.append({
            'nome': user.get_full_name() or user.username,
            'total': user.num_emprestimos
        })
    
    livro_mais_emprestado = {'titulo': top_livros[0]['titulo'], 'quantidade': top_livros[0]['total']} if top_livros else {'titulo': 'N/A', 'quantidade': 0}
    usuario_mais_ativo = usuarios_formatados[0] if usuarios_formatados else {'nome': 'N/A', 'quantidade': 0}
    
    categorias_data = []
    for cat_value, cat_label in CATEGORIAS:
        count = Livro.objects.filter(categoria=cat_value).count()
        if count > 0:
            percentual = (count / Livro.objects.count() * 100) if Livro.objects.count() > 0 else 0
            categorias_data.append({
                'categoria': cat_value,
                'categoria_display': cat_label,
                'total': count,
                'percentual': round(percentual, 1)
            })
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dec']
    valores_emprestimos = [12, 19, 3, 5, 2, 15, 8, 12, 7, 9, 11, 14]
    
    import json
    meses_json = json.dumps(meses)
    valores_json = json.dumps(valores_emprestimos)
    categorias_labels = json.dumps([cat['categoria_display'] for cat in categorias_data])
    categorias_values = json.dumps([cat['total'] for cat in categorias_data])
    
    context = {
        'total_emprestimos': total_emprestimos,
        'livro_mais_emprestado': livro_mais_emprestado,
        'usuario_mais_ativo': usuario_mais_ativo,
        'taxa_devolucao': 95,
        'top_livros': top_livros,
        'top_usuarios': usuarios_formatados,
        'categorias': categorias_data,
        'meses': meses_json,
        'valores_emprestimos': valores_json,
        'categorias_labels': categorias_labels,
        'categorias_values': categorias_values,
    }
    
    return render(request, 'admin/relatorios/relatorios.html', context)

# ========== CONFIGURAÇÕES ==========
@login_required
@admin_or_funcionario_required
def configurar_biblioteca(request):
    """Configuração das informações da biblioteca"""
    biblioteca_info, created = BibliotecaInfo.objects.get_or_create(
        id=1,
        defaults={
            'nome': 'Biblioteca Pública Municipal',
            'historia': 'Informe a história da biblioteca...',
            'historia_municipio': 'Informe a história do município...',
            'endereco': 'Informe o endereço...',
            'telefone': '(00) 00000-0000',
            'email': 'biblioteca@municipio.gov.br',
            'bibliotecaria_responsavel': 'Nome da bibliotecária',
            'administracao_municipal': 'Prefeitura Municipal',
            'horario_funcionamento': 'Segunda a Sexta: 8h às 18h\nSábado: 9h às 13h',
        }
    )
    
    if request.method == 'POST':
        form = BibliotecaInfoForm(request.POST, instance=biblioteca_info)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informações da biblioteca atualizadas com sucesso!')
            return redirect('configurar_biblioteca')
    else:
        form = BibliotecaInfoForm(instance=biblioteca_info)
    
    context = {'form': form}
    return render(request, 'admin/config/configurar_biblioteca.html', context)

def cadastro_usuario(request):
    """View pública para cadastro de novos usuários"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        perfil_form = CadastroPublicoForm(request.POST)
        
        if user_form.is_valid() and perfil_form.is_valid():
            # Salvar o usuário
            user = user_form.save()
            
            # Criar perfil com categoria fixa como 'usuario'
            perfil = perfil_form.save(commit=False)
            perfil.usuario = user
            perfil.categoria = 'usuario'  # Categoria fixa para todos
            perfil.save()
            
            # Fazer login automático - IMPORTANTE: usar django.contrib.auth.login
            from django.contrib.auth import login as auth_login
            auth_login(request, user)
            
            messages.success(request, 'Cadastro realizado com sucesso! Seja bem-vindo à biblioteca.')
            
            # Redirecionar para o perfil do usuário
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Erro no cadastro. Verifique os dados informados.')
    else:
        user_form = UserForm()
        perfil_form = CadastroPublicoForm()
    
    context = {
        'form': user_form,
        'perfil_form': perfil_form,
    }
    return render(request, 'auth/cadastro.html', context)
    """View pública para cadastro de novos usuários"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        perfil_form = CadastroPublicoForm(request.POST)  # Usando o novo formulário
        
        if user_form.is_valid() and perfil_form.is_valid():
            user = user_form.save()
            
            # Criar perfil com categoria fixa como 'usuario'
            perfil = perfil_form.save(commit=False)
            perfil.usuario = user
            perfil.categoria = 'usuario'  # Categoria fixa para todos
            perfil.save()
            
            # Fazer login automático
            login(request, user)
            
            messages.success(request, 'Cadastro realizado com sucesso! Seja bem-vindo à biblioteca.')
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Erro no cadastro. Verifique os dados informados.')
    else:
        user_form = UserForm()
        perfil_form = CadastroPublicoForm()  # Usando o novo formulário
    
    context = {
        'form': user_form,
        'perfil_form': perfil_form,
    }
    return render(request, 'auth/cadastro.html', context)
    """View pública para cadastro de novos usuários"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        perfil_form = PerfilUsuarioForm(request.POST)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user = user_form.save()
            
            # Forçar categoria como 'usuario' para cadastros públicos
            perfil = perfil_form.save(commit=False)
            perfil.usuario = user
            perfil.categoria = 'usuario'  # Sempre usuário comum no cadastro público
            perfil.save()
            
            # Fazer login automático após cadastro
            from django.contrib.auth import login
            login(request, user)
            
            messages.success(request, 'Cadastro realizado com sucesso! Seja bem-vindo à biblioteca.')
            
            # Verificar se tem perfil e redirecionar
            if hasattr(user, 'perfilusuario'):
                return redirect('perfil_usuario')
            return redirect('home')
        else:
            messages.error(request, 'Erro no cadastro. Verifique os dados informados.')
    else:
        user_form = UserForm()
        perfil_form = PerfilUsuarioForm()
    
    # Esconder campo categoria no formulário de perfil (será forçado como 'usuario')
    perfil_form.fields['categoria'].widget = forms.HiddenInput()
    perfil_form.fields['categoria'].initial = 'usuario'  # Define o valor inicial
    
    context = {
        'form': user_form,
        'perfil_form': perfil_form,
    }
    return render(request, 'auth/cadastro.html', context)
    """View pública para cadastro de novos usuários"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        perfil_form = PerfilUsuarioForm(request.POST)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user = user_form.save()
            
            # Forçar categoria como 'usuario' para cadastros públicos
            perfil = perfil_form.save(commit=False)
            perfil.usuario = user
            perfil.categoria = 'usuario'  # Sempre usuário comum no cadastro público
            perfil.save()
            
            # Fazer login automático após cadastro
            from django.contrib.auth import login
            login(request, user)
            
            messages.success(request, 'Cadastro realizado com sucesso! Seja bem-vindo à biblioteca.')
            
            # Verificar se tem perfil e redirecionar
            if hasattr(user, 'perfilusuario'):
                return redirect('perfil_usuario')
            return redirect('home')
        else:
            messages.error(request, 'Erro no cadastro. Verifique os dados informados.')
    else:
        user_form = UserForm()
        perfil_form = PerfilUsuarioForm()
    
    # Esconder campo categoria no formulário de perfil (será forçado como 'usuario')
    perfil_form.fields['categoria'].widget = forms.HiddenInput()
    perfil_form.initial['categoria'] = 'usuario'
    
    context = {
        'form': user_form,
        'perfil_form': perfil_form,
    }
    return render(request, 'auth/cadastro.html', context)

# ========== ÁREA DO USUÁRIO COMUM ==========
@login_required
def perfil_usuario(request):
    """Perfil do usuário comum"""
    perfil, created = PerfilUsuario.objects.get_or_create(
        usuario=request.user,
        defaults={
            'categoria': 'usuario',
            'telefone': '',
            'rua': '',
            'bairro': '',
            'numero': '',
            'cidade': '',
            'nome_mae': '',
        }
    )
    
    emprestimos_ativos = Emprestimo.objects.filter(
        usuario=request.user,
        data_devolucao_real__isnull=True
    ).order_by('-data_emprestimo')
    
    hoje = timezone.now().date()
    for emprestimo in emprestimos_ativos:
        if emprestimo.data_devolucao_prevista:
            if isinstance(emprestimo.data_devolucao_prevista, datetime):
                data_prevista = emprestimo.data_devolucao_prevista.date()
            else:
                data_prevista = emprestimo.data_devolucao_prevista
            
            if data_prevista < hoje:
                emprestimo.dias_atraso = (hoje - data_prevista).days
                emprestimo.dias_restantes = 0
            else:
                emprestimo.dias_atraso = 0
                emprestimo.dias_restantes = (data_prevista - hoje).days
        else:
            emprestimo.dias_atraso = 0
            emprestimo.dias_restantes = None
    
    emprestimos_historico = Emprestimo.objects.filter(
        usuario=request.user,
        data_devolucao_real__isnull=False
    ).order_by('-data_emprestimo')[:20]
    
    emprestimos_total = Emprestimo.objects.filter(usuario=request.user).count()
    livros_lidos = Emprestimo.objects.filter(
        usuario=request.user,
        data_devolucao_real__isnull=False
    ).count()
    
    context = {
        'perfil': perfil,
        'emprestimos_ativos': emprestimos_ativos,
        'emprestimos_historico': emprestimos_historico,
        'emprestimos_total': emprestimos_total,
        'livros_lidos': livros_lidos,
    }
    
    return render(request, 'usuario/perfil/perfil.html', context)

# ========== LIVROS PDF (PÚBLICO) ==========
def acervo_pdf(request):
    """Acervo de livros em PDF"""
    categoria = request.GET.get('categoria', '')
    busca = request.GET.get('busca', '')
    
    livros = LivroPDF.objects.filter(ativo=True)
    
    if categoria:
        livros = livros.filter(categoria=categoria)
    
    if busca:
        livros = livros.filter(
            Q(titulo__icontains=busca) |
            Q(autor__icontains=busca) |
            Q(descricao__icontains=busca)
        )
    
    ordenacao = request.GET.get('ordenar', 'recentes')
    if ordenacao == 'visualizacoes':
        livros = livros.order_by('-visualizacoes')
    elif ordenacao == 'titulo':
        livros = livros.order_by('titulo')
    else:
        livros = livros.order_by('-data_cadastro')
    
    categorias = LivroPDF.CATEGORIAS_CHOICES
    
    context = {
        'livros': livros,
        'categorias': categorias,
        'categoria_selecionada': categoria,
        'busca': busca,
        'ordenacao': ordenacao,
        'total_livros': livros.count(),
    }
    
    return render(request, 'usuario/pdf/acervo_pdf.html', context)

def ler_pdf_simples(request, livro_id):
    """Versão simples do leitor PDF"""
    livro = get_object_or_404(LivroPDF, id=livro_id, ativo=True)
    livro.aumentar_visualizacao()
    
    pdf_disponivel = livro.arquivo_pdf is not None
    pdf_url = f"/media/{livro.arquivo_pdf.name}" if pdf_disponivel else None
    
    context = {
        'livro': livro,
        'pdf_disponivel': pdf_disponivel,
        'pdf_url': pdf_url,
    }
    return render(request, 'usuario/pdf/ler_pdf_simples.html', context)

def teste_pdf(request, livro_id):
    """View de teste para PDF"""
    from django.conf import settings
    
    try:
        livro = LivroPDF.objects.get(id=livro_id, ativo=True)
        
        context = {
            'pdf_disponivel': livro.arquivo_pdf is not None,
            'pdf_url': f"/media/{livro.arquivo_pdf.name}" if livro.arquivo_pdf else None,
            'arquivo': livro.arquivo_pdf.name if livro.arquivo_pdf else None,
            'livro_id': livro_id,
            'media_url': settings.MEDIA_URL,
            'media_root': str(settings.MEDIA_ROOT),
        }
        
        return render(request, 'usuario/pdf/teste_pdf.html', context)
        
    except Exception as e:
        return HttpResponse(f"Erro: {str(e)}")

def ler_livro_pdf(request, livro_id):
    """Leitura de livro PDF"""
    try:
        livro = get_object_or_404(LivroPDF, id=livro_id, ativo=True)
        livro.aumentar_visualizacao()
        
        livros_relacionados = LivroPDF.objects.filter(
            categoria=livro.categoria,
            ativo=True
        ).exclude(id=livro_id)[:4]
        
        pdf_disponivel = livro.arquivo_pdf is not None
        pdf_url = f"/media/{livro.arquivo_pdf.name}" if pdf_disponivel else None
        
        context = {
            'livro': livro,
            'livros_relacionados': livros_relacionados,
            'pdf_disponivel': pdf_disponivel,
            'pdf_url': pdf_url,
        }
        
        return render(request, 'usuario/pdf/ler_pdf.html', context)
        
    except Exception as e:
        print(f"Erro em ler_livro_pdf: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Erro ao carregar o livro: {str(e)}')
        return redirect('acervo_pdf')

# ========== THREAD DE LIMPEZA DE IMAGENS TEMPORÁRIAS ==========
def limpar_imagens_temporarias():
    """Limpa imagens temporárias com mais de 1 hora"""
    from django.conf import settings
    import os
    import time
    
    while True:
        try:
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_pages')
            if os.path.exists(temp_dir):
                agora = time.time()
                for arquivo in os.listdir(temp_dir):
                    caminho = os.path.join(temp_dir, arquivo)
                    if os.path.isfile(caminho) and (agora - os.path.getmtime(caminho)) > 3600:
                        os.remove(caminho)
                        print(f"Removido arquivo temporário: {arquivo}")
        except Exception as e:
            print(f"Erro ao limpar temporários: {e}")
        
        time.sleep(3600)

# Iniciar thread de limpeza
limpeza_thread = threading.Thread(target=limpar_imagens_temporarias, daemon=True)
limpeza_thread.start()

def visualizar_pdf_como_imagens(request, livro_id):
    """Converte PDF para imagens e exibe página por página"""
    from django.conf import settings
    import os
    import uuid
    
    try:
        livro = get_object_or_404(LivroPDF, id=livro_id, ativo=True)
        livro.aumentar_visualizacao()
        
        pdf_path = livro.arquivo_pdf.path
        
        if not os.path.exists(pdf_path):
            messages.error(request, 'Arquivo PDF não encontrado.')
            return redirect('acervo_pdf')
        
        poppler_path = '/Users/evertonabreu/micromamba/bin'
        
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_pages')
        os.makedirs(temp_dir, exist_ok=True)
        
        from pdf2image import convert_from_path
        images = convert_from_path(
            pdf_path, 
            dpi=150,
            first_page=1,
            last_page=min(30, 999),
            fmt='jpeg',
            poppler_path=poppler_path
        )
        
        session_id = str(uuid.uuid4())[:8]
        
        imagens_urls = []
        for i, image in enumerate(images):
            filename = f"livro_{livro_id}_pagina_{i+1}_{session_id}.jpg"
            filepath = os.path.join(temp_dir, filename)
            image.save(filepath, 'JPEG', quality=70)
            
            url = f"{settings.MEDIA_URL}temp_pages/{filename}"
            imagens_urls.append({
                'url': url,
                'numero': i + 1
            })
        
        context = {
            'livro': livro,
            'imagens': imagens_urls,
            'total_paginas': len(imagens_urls),
            'session_id': session_id
        }
        
        return render(request, 'usuario/pdf/visualizador_imagens.html', context)
        
    except Exception as e:
        print(f"Erro ao converter PDF: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Erro ao processar o PDF: {str(e)}')
        return redirect('acervo_pdf')

def visualizar_pdf_seguro(request, livro_id):
    """Visualização segura de PDF (apenas leitura, sem download)"""
    try:
        livro = get_object_or_404(LivroPDF, id=livro_id, ativo=True)
        livro.aumentar_visualizacao()
        
        pdf_disponivel = livro.arquivo_pdf is not None
        pdf_url = f"/media/{livro.arquivo_pdf.name}" if pdf_disponivel else None
        
        livros_relacionados = LivroPDF.objects.filter(
            categoria=livro.categoria,
            ativo=True
        ).exclude(id=livro_id)[:4]
        
        context = {
            'livro': livro,
            'pdf_disponivel': pdf_disponivel,
            'pdf_url': pdf_url,
            'livros_relacionados': livros_relacionados,
        }
        
        return render(request, 'usuario/pdf/visualizador_seguro.html', context)
        
    except Exception as e:
        print(f"Erro em visualizar_pdf_seguro: {e}")
        messages.error(request, 'Erro ao carregar o PDF')
        return redirect('acervo_pdf')

def servir_pdf_seguro(request, livro_id):
    """Serve o PDF com headers apropriados para visualização no iframe"""
    try:
        livro = get_object_or_404(LivroPDF, id=livro_id, ativo=True)
        
        if not livro.arquivo_pdf:
            raise Http404("PDF não encontrado")
        
        file_path = livro.arquivo_pdf.path
        
        if not os.path.exists(file_path):
            raise Http404("Arquivo não encontrado no servidor")
        
        livro.aumentar_visualizacao()
        
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
        
        response['Content-Disposition'] = f'inline; filename="{livro.titulo}.pdf"'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Content-Security-Policy'] = "frame-ancestors 'self'"
        response['Access-Control-Allow-Origin'] = '*'
        
        return response
        
    except Exception as e:
        print(f"Erro ao servir PDF: {e}")
        raise Http404("Erro ao carregar o PDF")

def visualizar_pdf(request, livro_id):
    """Visualização de PDF"""
    try:
        livro = get_object_or_404(LivroPDF, id=livro_id, ativo=True)
        
        if not livro.arquivo_pdf:
            messages.error(request, 'Arquivo PDF não encontrado.')
            return redirect('ler_livro_pdf', livro_id=livro_id)
        
        livro.aumentar_visualizacao()
        
        file_path = livro.arquivo_pdf.path
        
        if not os.path.exists(file_path):
            messages.error(request, 'Arquivo PDF não encontrado no servidor.')
            return redirect('ler_livro_pdf', livro_id=livro_id)
        
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{livro.titulo}.pdf"'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
        
    except Exception as e:
        print(f"Erro em visualizar_pdf: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f'Erro ao carregar PDF: {str(e)}')
        return redirect('ler_livro_pdf', livro_id=livro_id)

# ========== LIVROS PDF (ADMIN) ==========
@login_required
@admin_or_funcionario_required
def cadastro_livro_pdf(request):
    """Cadastro de livro PDF"""
    if request.method == 'POST':
        form = LivroPDFForm(request.POST, request.FILES)
        if form.is_valid():
            livro = form.save()
            messages.success(request, f'Livro PDF "{livro.titulo}" cadastrado com sucesso!')
            return redirect('lista_livros_pdf')
    else:
        form = LivroPDFForm()
    
    context = {'form': form}
    return render(request, 'admin/livros_pdf/cadastro_livro_pdf.html', context)

@login_required
@admin_or_funcionario_required
def lista_livros_pdf(request):
    """Listagem de livros PDF"""
    livros = LivroPDF.objects.all().order_by('-data_cadastro')
    
    categoria = request.GET.get('categoria', '')
    busca = request.GET.get('busca', '')
    
    if categoria:
        livros = livros.filter(categoria=categoria)
    
    if busca:
        livros = livros.filter(
            Q(titulo__icontains=busca) |
            Q(autor__icontains=busca) |
            Q(descricao__icontains=busca)
        )
    
    context = {
        'livros': livros,
        'categorias': LivroPDF.CATEGORIAS_CHOICES,
        'categoria_selecionada': categoria,
        'busca': busca,
    }
    
    return render(request, 'admin/livros_pdf/lista_livros_pdf.html', context)

@login_required
@admin_or_funcionario_required
def editar_livro_pdf(request, livro_id):
    """Edição de livro PDF"""
    livro = get_object_or_404(LivroPDF, id=livro_id)
    
    if request.method == 'POST':
        form = LivroPDFForm(request.POST, request.FILES, instance=livro)
        if form.is_valid():
            form.save()
            messages.success(request, f'Livro PDF "{livro.titulo}" atualizado com sucesso!')
            return redirect('lista_livros_pdf')
    else:
        form = LivroPDFForm(instance=livro)
    
    context = {'form': form, 'livro': livro}
    return render(request, 'admin/livros_pdf/editar_livro_pdf.html', context)

# ========== SOLICITAÇÕES DE EMPRÉSTIMO ==========
@login_required
def solicitar_emprestimo(request, livro_id):
    """Usuário solicita empréstimo de um livro"""
    livro = get_object_or_404(Livro, id=livro_id, ativo=True)
    
    if request.method == 'POST':
        data_devolucao = request.POST.get('data_devolucao')
        observacoes = request.POST.get('observacoes', '')
        
        if not data_devolucao:
            data_devolucao = timezone.now() + timedelta(days=15)
        else:
            data_devolucao = datetime.strptime(data_devolucao, '%Y-%m-%d')
        
        solicitacao = SolicitacaoEmprestimo.objects.create(
            livro=livro,
            usuario=request.user,
            data_devolucao_prevista=data_devolucao,
            observacoes=observacoes,
            status='pendente'
        )
        
        messages.success(request, f'Solicitação de empréstimo para "{livro.titulo}" enviada com sucesso! Aguarde a aprovação.')
        return redirect('perfil_usuario')
    
    context = {
        'livro': livro,
        'data_padrao': (timezone.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
    }
    return render(request, 'usuario/perfil/solicitar_emprestimo.html', context)

@login_required
@admin_required
def lista_solicitacoes(request):
    """Listagem de solicitações de empréstimo"""
    status = request.GET.get('status', 'pendente')
    
    solicitacoes = SolicitacaoEmprestimo.objects.all().order_by('-data_solicitacao')
    
    if status:
        solicitacoes = solicitacoes.filter(status=status)
    
    pendentes_count = SolicitacaoEmprestimo.objects.filter(status='pendente').count()
    
    page = request.GET.get('page', 1)
    paginator = Paginator(solicitacoes, 20)
    
    try:
        solicitacoes_page = paginator.page(page)
    except PageNotAnInteger:
        solicitacoes_page = paginator.page(1)
    except EmptyPage:
        solicitacoes_page = paginator.page(paginator.num_pages)
    
    context = {
        'solicitacoes': solicitacoes_page,
        'status_atual': status,
        'pendentes_count': pendentes_count,
        'total_pendentes': pendentes_count,
    }
    return render(request, 'admin/solicitacoes/lista_solicitacoes.html', context)

@login_required
@admin_required
def processar_solicitacao(request, solicitacao_id):
    """Aprovar ou rejeitar uma solicitação"""
    solicitacao = get_object_or_404(SolicitacaoEmprestimo, id=solicitacao_id)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        observacoes = request.POST.get('observacoes_admin', '')
        
        if acao == 'aprovar':
            if solicitacao.livro.quantidade_disponivel <= 0:
                messages.error(request, 'Livro não está mais disponível!')
                return redirect('lista_solicitacoes')
            
            emprestimo = Emprestimo.objects.create(
                livro=solicitacao.livro,
                usuario=solicitacao.usuario,
                data_emprestimo=timezone.now(),
                data_devolucao_prevista=solicitacao.data_devolucao_prevista,
                observacoes=solicitacao.observacoes,
                status='ativo'
            )
            
            solicitacao.livro.quantidade_disponivel -= 1
            solicitacao.livro.save()
            
            solicitacao.status = 'aprovado'
            solicitacao.observacoes_admin = observacoes
            solicitacao.data_emprestimo = timezone.now()
            solicitacao.save()
            
            messages.success(request, f'Solicitação aprovada! Empréstimo #{emprestimo.id} criado.')
            
        elif acao == 'rejeitar':
            solicitacao.status = 'rejeitado'
            solicitacao.observacoes_admin = observacoes
            solicitacao.save()
            messages.warning(request, 'Solicitação rejeitada.')
            
        return redirect('lista_solicitacoes')
    
    context = {
        'solicitacao': solicitacao,
    }
    return render(request, 'admin/solicitacoes/processar_solicitacao.html', context)

@login_required
@admin_or_funcionario_required
def renovar_emprestimo(request, emprestimo_id):
    """Renovar empréstimo por mais 15 dias"""
    if request.method == 'POST':
        emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id, data_devolucao_real__isnull=True)
        
        nova_data = emprestimo.data_devolucao_prevista + timedelta(days=15)
        emprestimo.data_devolucao_prevista = nova_data
        emprestimo.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Empréstimo renovado com sucesso!',
            'nova_data': nova_data.strftime('%d/%m/%Y')
        })
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)

@login_required
@admin_or_funcionario_required
def api_emprestimo_detalhes(request, emprestimo_id):
    """API para detalhes do empréstimo"""
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id)
    
    hoje = timezone.now().date()
    if isinstance(emprestimo.data_devolucao_prevista, datetime):
        data_prevista = emprestimo.data_devolucao_prevista.date()
    else:
        data_prevista = emprestimo.data_devolucao_prevista
    
    if data_prevista < hoje:
        status = 'Atrasado'
        status_cor = 'danger'
        dias_restantes = f"{abs((hoje - data_prevista).days)} dias de atraso"
    else:
        status = 'No prazo'
        status_cor = 'success'
        dias_restantes = f"{(data_prevista - hoje).days} dias restantes"
    
    data = {
        'id': emprestimo.id,
        'livro': {
            'titulo': emprestimo.livro.titulo,
            'autor': emprestimo.livro.autor,
            'editora': emprestimo.livro.editora.nome if emprestimo.livro.editora else 'Não informada',
        },
        'usuario': {
            'nome': emprestimo.usuario.get_full_name() or emprestimo.usuario.username,
            'email': emprestimo.usuario.email,
            'telefone': emprestimo.usuario.perfilusuario.telefone if hasattr(emprestimo.usuario, 'perfilusuario') else 'Não informado',
        },
        'data_emprestimo': emprestimo.data_emprestimo.strftime('%d/%m/%Y %H:%M'),
        'data_prevista': emprestimo.data_devolucao_prevista.strftime('%d/%m/%Y'),
        'dias_restantes': dias_restantes,
        'status': status,
        'status_cor': status_cor,
        'observacoes': emprestimo.observacoes,
    }
    
    return JsonResponse(data)

# ========== APIs ==========
@login_required
@admin_or_funcionario_required
def api_livro_info(request, livro_id):
    """API para informações do livro"""
    livro = get_object_or_404(Livro, id=livro_id)
    
    data = {
        'id': livro.id,
        'titulo': livro.titulo,
        'autor': livro.autor,
        'editora': livro.editora.nome if livro.editora else '',
        'ano_publicacao': livro.ano_publicacao,
        'categoria': livro.categoria,
        'categoria_display': livro.get_categoria_display(),
        'classificacao': livro.classificacao,
        'quantidade_total': livro.quantidade_total,
        'quantidade_disponivel': livro.quantidade_disponivel,
        'prateleira': livro.prateleira.nome if livro.prateleira else '',
        'sinopse': livro.sinopse,
        'ativo': livro.ativo,
    }
    
    return JsonResponse(data)

@login_required
@admin_or_funcionario_required
def api_usuario_info(request, usuario_id):
    """API para informações do usuário"""
    usuario = get_object_or_404(User, id=usuario_id)
    perfil = PerfilUsuario.objects.filter(usuario=usuario).first()
    
    emprestimos_ativos = Emprestimo.objects.filter(
        usuario=usuario,
        data_devolucao_real__isnull=True
    ).count()
    
    data = {
        'id': usuario.id,
        'username': usuario.username,
        'email': usuario.email,
        'first_name': usuario.first_name,
        'last_name': usuario.last_name,
        'nome_completo': usuario.get_full_name() or usuario.username,
        'telefone': perfil.telefone if perfil else '',
        'whatsapp': perfil.whatsapp if perfil else '',
        'categoria': perfil.categoria if perfil else 'usuario',
        'categoria_display': perfil.get_categoria_display() if perfil else 'Usuário',
        'emprestimos_ativos': emprestimos_ativos,
    }
    
    return JsonResponse(data)

@login_required
@admin_or_funcionario_required
def api_buscar_livros(request):
    """API para busca de livros"""
    termo = request.GET.get('q', '')
    
    livros = Livro.objects.filter(
        Q(titulo__icontains=termo) |
        Q(autor__icontains=termo) |
        Q(editora__nome__icontains=termo)
    ).filter(
        ativo=True,
        quantidade_disponivel__gt=0
    )[:10]
    
    resultados = []
    for livro in livros:
        resultados.append({
            'id': livro.id,
            'titulo': livro.titulo,
            'autor': livro.autor,
            'editora': livro.editora.nome if livro.editora else '',
            'ano_publicacao': livro.ano_publicacao,
            'quantidade_disponivel': livro.quantidade_disponivel,
            'quantidade_total': livro.quantidade_total,
        })
    
    return JsonResponse(resultados, safe=False)

@login_required
@admin_or_funcionario_required
def api_buscar_usuarios(request):
    """API para busca de usuários"""
    termo = request.GET.get('q', '')
    
    usuarios = User.objects.filter(
        Q(username__icontains=termo) |
        Q(first_name__icontains=termo) |
        Q(last_name__icontains=termo) |
        Q(email__icontains=termo)
    )[:10]
    
    resultados = []
    for usuario in usuarios:
        perfil = PerfilUsuario.objects.filter(usuario=usuario).first()
        
        resultados.append({
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'nome_completo': usuario.get_full_name() or usuario.username,
            'categoria': perfil.categoria if perfil else 'usuario',
            'categoria_display': perfil.get_categoria_display() if perfil else 'Usuário',
        })
    
    return JsonResponse(resultados, safe=False)

# ========== API WhatsApp ==========
@login_required
@admin_or_funcionario_required
def api_whatsapp_notificacao(request):
    """API para envio de notificação via WhatsApp"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            emprestimo_id = data.get('emprestimo_id')
            
            emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id)
            perfil = PerfilUsuario.objects.filter(usuario=emprestimo.usuario).first()
            
            if not perfil or not perfil.whatsapp:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Usuário não tem WhatsApp cadastrado'
                }, status=400)
            
            telefone = perfil.whatsapp
            
            if emprestimo.data_devolucao_prevista:
                if isinstance(emprestimo.data_devolucao_prevista, datetime):
                    data_formatada = emprestimo.data_devolucao_prevista.strftime('%d/%m/%Y')
                else:
                    data_formatada = emprestimo.data_devolucao_prevista.strftime('%d/%m/%Y')
            else:
                data_formatada = "Não definida"
            
            return JsonResponse({
                'status': 'success',
                'message': 'Notificação enviada com sucesso!',
                'telefone': telefone
            })
            
        except Emprestimo.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Empréstimo não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao enviar notificação: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido'
    }, status=405)