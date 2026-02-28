from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PerfilUsuario(models.Model):
    CATEGORIAS = [
        ('admin', 'Administrador'),
        ('funcionario', 'Funcionário'),
        ('usuario', 'Usuário'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='usuario')
    telefone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    rua = models.CharField(max_length=200)
    bairro = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    cidade = models.CharField(max_length=100)
    nome_mae = models.CharField(max_length=200)
    nome_pai = models.CharField(max_length=200, blank=True)
    visitas = models.IntegerField(default=0)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username}"

class Editora(models.Model):
    """Modelo para gerenciar as editoras"""
    nome = models.CharField(max_length=200, unique=True, verbose_name="Nome da Editora")
    site = models.URLField(max_length=200, blank=True, null=True, verbose_name="Site")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(max_length=200, blank=True, null=True, verbose_name="Email")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Editora"
        verbose_name_plural = "Editoras"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def total_livros(self):
        """Retorna o total de livros desta editora"""
        return self.livros.count()

class Prateleira(models.Model):
    """Modelo para gerenciar as prateleiras da biblioteca"""
    CATEGORIAS_ASSOCIADAS = [
        ('infantil', 'Infantil'),
        ('juvenil', 'Juvenil'),
        ('adulto', 'Adulto'),
        ('academico', 'Acadêmico'),
        ('ficcao', 'Ficção'),
        ('nao_ficcao', 'Não-Ficção'),
        ('tecnico', 'Técnico'),
        ('didatico', 'Didático'),
        ('biografia', 'Biografia'),
        ('historia', 'História'),
        ('poesia', 'Poesia'),
        ('outro', 'Outro'),
    ]
    
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome da Prateleira")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    categoria_associada = models.CharField(
        max_length=20, 
        choices=CATEGORIAS_ASSOCIADAS,
        verbose_name="Categoria Associada",
        help_text="Categoria de livros que normalmente ficam nesta prateleira"
    )
    localizacao_fisica = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Localização Física",
        help_text="Ex: Corredor A, Seção 1"
    )
    capacidade_maxima = models.IntegerField(default=50, verbose_name="Capacidade Máxima")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Prateleira"
        verbose_name_plural = "Prateleiras"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def total_livros(self):
        """Retorna o total de livros nesta prateleira"""
        return self.livros.count()
    
    def livros_disponiveis(self):
        """Retorna a quantidade de livros disponíveis nesta prateleira"""
        return self.livros.filter(quantidade_disponivel__gt=0, ativo=True).count()
    
    def livros_emprestados(self):
        """Retorna a quantidade de livros emprestados desta prateleira"""
        total = self.livros.aggregate(
            total_emprestados=models.Sum(
                models.F('quantidade_total') - models.F('quantidade_disponivel')
            )
        )['total_emprestados'] or 0
        return total

from django.db import models
import os

from django.db import models

class Livro(models.Model):
    capa = models.ImageField(
        upload_to='capas_livros/',
        verbose_name="Capa do Livro",
        blank=True,
        null=True,
        help_text="Imagem da capa do livro (formatos: JPG, PNG)"
    )
    titulo = models.CharField(max_length=300)
    autor = models.CharField(max_length=200)
    editora = models.ForeignKey(
        'Editora', 
        on_delete=models.PROTECT,
        verbose_name="Editora",
        related_name='livros',
        null=True,
        blank=True
    )
    ano_publicacao = models.IntegerField()
    quantidade_paginas = models.IntegerField()
    prateleira = models.ForeignKey(
        'Prateleira', 
        on_delete=models.PROTECT,
        verbose_name="Prateleira",
        related_name='livros'
    )
    
    classificacao = models.CharField(max_length=20, choices=[
        ('infantil', 'Infantil'),
        ('juvenil', 'Juvenil'),
        ('adulto', 'Adulto'),
        ('academico', 'Acadêmico'),
    ])
    
    categoria = models.CharField(max_length=20, choices=[
        ('ficcao', 'Ficção'),
        ('nao_ficcao', 'Não-Ficção'),
        ('tecnico', 'Técnico'),
        ('didatico', 'Didático'),
        ('biografia', 'Biografia'),
        ('historia', 'História'),
        ('poesia', 'Poesia'),
        ('outro', 'Outro'),
    ])
    
    quantidade_total = models.IntegerField(default=1)
    quantidade_disponivel = models.IntegerField(default=1)
    sinopse = models.TextField(blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    # NOVOS CAMPOS PARA PDF
    arquivo_pdf = models.FileField(upload_to="pdfs/", blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.titulo

    # SALVAR PDF NO SUPABASE
    def save(self, *args, **kwargs):
        from .supabase_storage import upload_pdf

        is_new = self.pk is None
        super().save(*args, **kwargs)  # salva para gerar ID

        # Se tiver PDF e ainda não tiver URL
        if self.arquivo_pdf and not self.pdf_url:
            filename = f"{self.id}_{self.arquivo_pdf.name}"
            self.pdf_url = upload_pdf(self.arquivo_pdf, filename)
            super().save(update_fields=["pdf_url"])
    capa = models.ImageField(
        upload_to='capas_livros/',
        verbose_name="Capa do Livro",
        blank=True,
        null=True,
        help_text="Imagem da capa do livro (formatos: JPG, PNG)"
    )
    titulo = models.CharField(max_length=300)
    autor = models.CharField(max_length=200)
    editora = models.ForeignKey(
        'Editora', 
        on_delete=models.PROTECT,
        verbose_name="Editora",
        related_name='livros',
        null=True,
        blank=True
    )
    ano_publicacao = models.IntegerField()
    quantidade_paginas = models.IntegerField()
    prateleira = models.ForeignKey(
        'Prateleira', 
        on_delete=models.PROTECT,
        verbose_name="Prateleira",
        related_name='livros'
    )
    
    classificacao = models.CharField(max_length=20, choices=[
        ('infantil', 'Infantil'),
        ('juvenil', 'Juvenil'),
        ('adulto', 'Adulto'),
        ('academico', 'Acadêmico'),
    ])
    
    categoria = models.CharField(max_length=20, choices=[
        ('ficcao', 'Ficção'),
        ('nao_ficcao', 'Não-Ficção'),
        ('tecnico', 'Técnico'),
        ('didatico', 'Didático'),
        ('biografia', 'Biografia'),
        ('historia', 'História'),
        ('poesia', 'Poesia'),
        ('outro', 'Outro'),
    ])
    
    quantidade_total = models.IntegerField(default=1)
    quantidade_disponivel = models.IntegerField(default=1)
    sinopse = models.TextField(blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    # NOVOS CAMPOS PARA PDF
    arquivo_pdf = models.FileField(upload_to="pdfs/", blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)  # Vai armazenar a URL do Supabase

    def __str__(self):
        return self.titulo

    capa = models.ImageField(
        upload_to='capas_livros/',
        verbose_name="Capa do Livro",
        blank=True,
        null=True,
        help_text="Imagem da capa do livro (formatos: JPG, PNG)"
    )
    titulo = models.CharField(max_length=300)
    autor = models.CharField(max_length=200)  # Por enquanto mantemos como CharField
    editora = models.ForeignKey(
        'Editora', 
        on_delete=models.PROTECT,
        verbose_name="Editora",
        related_name='livros',
        null=True,  # Permitir nulo temporariamente para migração
        blank=True
    )
    ano_publicacao = models.IntegerField()
    quantidade_paginas = models.IntegerField()
    prateleira = models.ForeignKey(
        'Prateleira', 
        on_delete=models.PROTECT,
        verbose_name="Prateleira",
        related_name='livros'
    )
    
    classificacao = models.CharField(max_length=20, choices=[
        ('infantil', 'Infantil'),
        ('juvenil', 'Juvenil'),
        ('adulto', 'Adulto'),
        ('academico', 'Acadêmico'),
    ])
    
    categoria = models.CharField(max_length=20, choices=[
        ('ficcao', 'Ficção'),
        ('nao_ficcao', 'Não-Ficção'),
        ('tecnico', 'Técnico'),
        ('didatico', 'Didático'),
        ('biografia', 'Biografia'),
        ('historia', 'História'),
        ('poesia', 'Poesia'),
        ('outro', 'Outro'),
    ])
    
    quantidade_total = models.IntegerField(default=1)
    quantidade_disponivel = models.IntegerField(default=1)
    sinopse = models.TextField(blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.titulo

class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_emprestimo = models.DateTimeField(default=timezone.now)
    data_devolucao_prevista = models.DateTimeField()
    data_devolucao_real = models.DateTimeField(null=True, blank=True)
    observacoes_devolucao = models.TextField(blank=True, null=True, verbose_name='Observações da Devolução')
    status = models.CharField(max_length=20, choices=[
        ('ativo', 'Ativo'),
        ('devolvido', 'Devolvido'),
        ('atrasado', 'Atrasado'),
        ('perdido', 'Perdido'),
    ], default='ativo')
    observacoes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.livro.titulo}"

class BibliotecaInfo(models.Model):
    nome = models.CharField(max_length=200)
    historia = models.TextField()
    historia_municipio = models.TextField()
    endereco = models.TextField()
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    bibliotecaria_responsavel = models.CharField(max_length=200)
    administracao_municipal = models.CharField(max_length=200)
    horario_funcionamento = models.TextField()
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nome

class Evento(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    data_evento = models.DateField(verbose_name="Data do Evento")
    foto = models.ImageField(upload_to='eventos/', verbose_name="Foto do Evento")
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-data_evento']
    
    def __str__(self):
        return self.titulo

class SolicitacaoEmprestimo(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('cancelado', 'Cancelado'),
        ('concluido', 'Concluído'),
    ]
    
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, verbose_name="Livro")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Solicitação")
    data_emprestimo = models.DateTimeField(null=True, blank=True, verbose_name="Data do Empréstimo")
    data_devolucao_prevista = models.DateTimeField(verbose_name="Data de Devolução Prevista")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    observacoes_admin = models.TextField(blank=True, verbose_name="Observações do Admin")
    notificado = models.BooleanField(default=False, verbose_name="Notificado")
    
    class Meta:
        verbose_name = "Solicitação de Empréstimo"
        verbose_name_plural = "Solicitações de Empréstimo"
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"Solicitação de {self.usuario.username} - {self.livro.titulo}"

class LivroPDF(models.Model):
    CATEGORIAS_CHOICES = [
        ('ficcao', 'Ficção'),
        ('nao_ficcao', 'Não-Ficção'),
        ('tecnico', 'Técnico'),
        ('didatico', 'Didático'),
        ('infantil', 'Infantil'),
        ('juvenil', 'Juvenil'),
        ('poesia', 'Poesia'),
        ('biografia', 'Biografia'),
        ('historia', 'História'),
        ('filosofia', 'Filosofia'),
        ('ciencia', 'Ciência'),
        ('arte', 'Arte'),
        ('outro', 'Outro'),
    ]
    
    titulo = models.CharField(max_length=300, verbose_name="Título")
    autor = models.CharField(max_length=200, verbose_name="Autor")
    descricao = models.TextField(verbose_name="Descrição")
    categoria = models.CharField(
        max_length=20, 
        choices=CATEGORIAS_CHOICES, 
        default='outro',
        verbose_name="Categoria"
    )
    arquivo_pdf = models.FileField(
        upload_to='pdf_livros/', 
        verbose_name="Arquivo PDF"
    )
    capa = models.ImageField(
        upload_to='capa_livros/',
        verbose_name="Capa do Livro",
        blank=True,
        null=True
    )
    paginas = models.IntegerField(verbose_name="Número de Páginas", default=0)
    ano_publicacao = models.IntegerField(verbose_name="Ano de Publicação", null=True, blank=True)
    editora = models.CharField(max_length=200, verbose_name="Editora", blank=True)
    isbn = models.CharField(max_length=20, verbose_name="ISBN", blank=True)
    visualizacoes = models.IntegerField(default=0, verbose_name="Visualizações")
    downloads = models.IntegerField(default=0, verbose_name="Downloads")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Livro PDF"
        verbose_name_plural = "Livros PDF"
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return self.titulo
    
    def aumentar_visualizacao(self):
        self.visualizacoes += 1
        self.save(update_fields=['visualizacoes'])
    
    def aumentar_download(self):
        self.downloads += 1
        self.save(update_fields=['downloads'])