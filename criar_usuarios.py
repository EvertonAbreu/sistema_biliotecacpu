import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PerfilUsuario

# Criar usuário comum
if not User.objects.filter(username='usuario_teste').exists():
    usuario = User.objects.create_user(
        username='usuario_teste',
        email='usuario@biblioteca.local',
        password='Usuario123',
        first_name='João',
        last_name='Silva'
    )
    
    perfil = PerfilUsuario.objects.create(
        usuario=usuario,
        categoria='usuario',
        telefone='(11) 98765-4321',
        rua='Rua das Flores',
        bairro='Centro',
        numero='123',
        cidade='São Paulo',
        estado='SP',
        nome_mae='Maria Silva',
        visitas=0
    )
    
    print("Usuário comum criado com sucesso!")
    print("Usuário: usuario_teste")
    print("Senha: Usuario123")
else:
    print("Usuário 'usuario_teste' já existe!")