from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import PerfilUsuario, Livro, Emprestimo, BibliotecaInfo, Prateleira, Editora, LivroPDF

# ========== PERFIL USUÁRIO ==========
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'

class UserAdminCustom(UserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_categoria')
    
    def get_categoria(self, obj):
        try:
            return obj.perfilusuario.categoria
        except:
            return 'N/A'
    get_categoria.short_description = 'Categoria'

# Desregistrar o User padrão e registrar com nosso customizado
admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)

# ========== PRATELEIRA ==========
@admin.register(Prateleira)
class PrateleiraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria_associada', 'localizacao_fisica', 'total_livros', 'ativo')
    list_filter = ('categoria_associada', 'ativo')
    search_fields = ('nome', 'descricao', 'localizacao_fisica')
    list_editable = ('ativo',)
    fieldsets = (
        ('Informações da Prateleira', {
            'fields': ('nome', 'descricao', 'categoria_associada')
        }),
        ('Localização', {
            'fields': ('localizacao_fisica', 'capacidade_maxima')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )
    readonly_fields = ('data_criacao', 'data_atualizacao')

# ========== EDITORA ==========
@admin.register(Editora)
class EditoraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'total_livros', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'email', 'telefone')
    list_editable = ('ativo',)
    readonly_fields = ('data_cadastro',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'site', 'telefone', 'email')
        }),
        ('Endereço', {
            'fields': ('endereco',)
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Status', {
            'fields': ('ativo', 'data_cadastro')
        }),
    )

# ========== LIVRO ==========
class LivroAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'titulo', 'autor', 'get_editora', 'ano_publicacao', 
                   'categoria', 'quantidade_total', 'quantidade_disponivel', 
                   'get_prateleira', 'ativo')
    list_filter = ('categoria', 'classificacao', 'prateleira__nome', 'editora__nome', 'ativo', 'ano_publicacao')
    search_fields = ('titulo', 'autor', 'editora__nome')
    list_editable = ('quantidade_disponivel', 'ativo')
    list_display_links = ('thumbnail', 'titulo')
    
    def get_prateleira(self, obj):
        return obj.prateleira.nome if obj.prateleira else 'Não definida'
    get_prateleira.short_description = 'Prateleira'
    get_prateleira.admin_order_field = 'prateleira__nome'
    
    def get_editora(self, obj):
        return obj.editora.nome if obj.editora else 'Não definida'
    get_editora.short_description = 'Editora'
    get_editora.admin_order_field = 'editora__nome'
    
    def thumbnail(self, obj):
        if obj.capa:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.capa.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: #e9ecef; border-radius: 5px; display: flex; align-items: center; justify-content: center;">'
            '<i class="fas fa-book" style="color: #6c757d;"></i>'
            '</div>'
        )
    thumbnail.short_description = 'Capa'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'autor', 'editora', 'ano_publicacao', 'sinopse')
        }),
        ('Classificação', {
            'fields': ('categoria', 'classificacao')
        }),
        ('Localização e Quantidade', {
            'fields': ('prateleira', 'quantidade_paginas', 
                      'quantidade_total', 'quantidade_disponivel')
        }),
        ('Arquivos', {
            'fields': ('capa',),
            'description': 'Upload da capa do livro (formatos: JPG, PNG)'
        }),
        ('Controle', {
            'fields': ('ativo', 'data_cadastro')
        }),
    )
    readonly_fields = ('data_cadastro',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "prateleira":
            kwargs["queryset"] = Prateleira.objects.filter(ativo=True).order_by('nome')
        elif db_field.name == "editora":
            kwargs["queryset"] = Editora.objects.filter(ativo=True).order_by('nome')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Livro, LivroAdmin)

# ========== EMPRÉSTIMO ==========
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('livro', 'usuario', 'data_emprestimo', 
                   'data_devolucao_prevista', 'status', 'atrasado_display')
    list_filter = ('status', 'data_emprestimo', 'data_devolucao_prevista')
    search_fields = ('livro__titulo', 'usuario__username', 'usuario__first_name')
    list_editable = ('status',)
    readonly_fields = ('data_emprestimo',)
    
    def atrasado_display(self, obj):
        from django.utils import timezone
        if obj.status == 'ativo' and timezone.now() > obj.data_devolucao_prevista:
            return 'Sim'
        return 'Não'
    atrasado_display.short_description = 'Atrasado'
    atrasado_display.boolean = True

admin.site.register(Emprestimo, EmprestimoAdmin)

# ========== BIBLIOTECA INFO ==========
class BibliotecaInfoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'data_atualizacao')
    readonly_fields = ('data_atualizacao',)

admin.site.register(BibliotecaInfo, BibliotecaInfoAdmin)

# ========== LIVRO PDF ==========
@admin.register(LivroPDF)
class LivroPDFAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'titulo', 'autor', 'categoria', 'visualizacoes', 'ativo')
    list_filter = ('categoria', 'ativo', 'data_cadastro')
    search_fields = ('titulo', 'autor', 'descricao')
    list_editable = ('ativo',)
    list_display_links = ('thumbnail', 'titulo')
    readonly_fields = ('visualizacoes', 'downloads', 'data_cadastro')
    
    def thumbnail(self, obj):
        if obj.capa:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.capa.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: #e9ecef; border-radius: 5px; display: flex; align-items: center; justify-content: center;">'
            '<i class="fas fa-file-pdf" style="color: #dc3545;"></i>'
            '</div>'
        )
    thumbnail.short_description = 'Capa'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'autor', 'descricao', 'categoria')
        }),
        ('Detalhes do Livro', {
            'fields': ('ano_publicacao', 'editora', 'isbn', 'paginas')
        }),
        ('Arquivos', {
            'fields': ('arquivo_pdf', 'capa')
        }),
        ('Estatísticas', {
            'fields': ('visualizacoes', 'downloads', 'data_cadastro')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )

# ========== PERSONALIZAÇÃO DO ADMIN ==========
admin.site.site_header = 'Administração da Biblioteca Pública'
admin.site.site_title = 'Sistema de Biblioteca'
admin.site.index_title = 'Painel de Controle'