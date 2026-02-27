from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

# ========== USUÁRIO ==========
class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Nome')
    last_name = forms.CharField(required=True, label='Sobrenome')
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

# ========== PERFIL USUÁRIO ==========
class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['categoria', 'telefone', 'whatsapp', 'rua', 'bairro', 'numero', 
                 'cidade', 'nome_mae', 'nome_pai']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da rua'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do bairro'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da cidade'}),
            'nome_mae': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo da mãe'}),
            'nome_pai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo do pai'}),
        }

class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['telefone', 'whatsapp', 'rua', 'bairro', 'numero', 
                 'cidade', 'nome_mae', 'nome_pai']
        widgets = {
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_mae': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_pai': forms.TextInput(attrs={'class': 'form-control'}),
        }

# ========== PRATELEIRA ==========
class PrateleiraForm(forms.ModelForm):
    class Meta:
        model = Prateleira
        fields = ['nome', 'descricao', 'categoria_associada', 'localizacao_fisica', 'capacidade_maxima', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria_associada': forms.Select(attrs={'class': 'form-control'}),
            'localizacao_fisica': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidade_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ========== EDITORA ==========
class EditoraForm(forms.ModelForm):
    class Meta:
        model = Editora
        fields = ['nome', 'site', 'telefone', 'email', 'endereco', 'observacoes', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da editora'}),
            'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.editora.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 0000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contato@editora.com'}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Endereço completo'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações adicionais'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ========== LIVRO ==========
class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = '__all__'
        exclude = ['data_cadastro']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título do livro'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do autor'}),
            'editora': forms.Select(attrs={'class': 'form-control'}),
            'ano_publicacao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2020'}),
            'quantidade_paginas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de páginas'}),
            'prateleira': forms.Select(attrs={'class': 'form-control'}),
            'classificacao': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade total de exemplares'}),
            'quantidade_disponivel': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade disponível'}),
            'sinopse': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Sinopse do livro'}),
            'capa': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'capa': 'Capa do Livro (opcional)',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar apenas prateleiras ativas
        self.fields['prateleira'].queryset = Prateleira.objects.filter(ativo=True)
        self.fields['prateleira'].empty_label = "Selecione uma prateleira"
        
        # Filtrar apenas editoras ativas
        self.fields['editora'].queryset = Editora.objects.filter(ativo=True)
        self.fields['editora'].empty_label = "Selecione uma editora"
        
        # Adicionar ajuda visual para quantidade disponível
        self.fields['quantidade_disponivel'].help_text = "Deve ser igual ou menor que a quantidade total"

# ========== EMPRÉSTIMO ==========
class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = ['livro', 'usuario', 'data_devolucao_prevista', 'observacoes']
        widgets = {
            'livro': forms.Select(attrs={'class': 'form-control'}),
            'usuario': forms.Select(attrs={'class': 'form-control'}),
            'data_devolucao_prevista': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# ========== BIBLIOTECA INFO ==========
class BibliotecaInfoForm(forms.ModelForm):
    class Meta:
        model = BibliotecaInfo
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'historia': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'historia_municipio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'endereco': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'bibliotecaria_responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'administracao_municipal': forms.TextInput(attrs={'class': 'form-control'}),
            'horario_funcionamento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# ========== LIVRO PDF ==========
class LivroPDFForm(forms.ModelForm):
    class Meta:
        model = LivroPDF
        fields = [
            'titulo', 'autor', 'descricao', 'categoria',
            'arquivo_pdf', 'capa', 'paginas',
            'ano_publicacao', 'editora', 'isbn', 'ativo'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título do livro'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do autor'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descrição do livro'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'paginas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de páginas'}),
            'ano_publicacao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ano de publicação'}),
            'editora': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Editora'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN (opcional)'}),
            'arquivo_pdf': forms.FileInput(attrs={'class': 'form-control'}),
            'capa': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'arquivo_pdf': 'Arquivo PDF (obrigatório)',
            'capa': 'Imagem da Capa (recomendado)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titulo'].required = True
        self.fields['autor'].required = True
        self.fields['arquivo_pdf'].required = True

# ========== EVENTO ==========
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'descricao', 'data_evento', 'foto', 'ativo']
        widgets = {
            'data_evento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'titulo': 'Título do Evento',
            'descricao': 'Descrição',
            'data_evento': 'Data do Evento',
            'foto': 'Foto do Evento',
            'ativo': 'Evento Ativo',
        }

class CadastroPublicoForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['telefone', 'whatsapp', 'rua', 'bairro', 'numero', 
                 'cidade', 'nome_mae', 'nome_pai']  # REMOVIDO o campo categoria
        widgets = {
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'rua': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da rua'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do bairro'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da cidade'}),
            'nome_mae': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo da mãe'}),
            'nome_pai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo do pai'}),
        }