import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from django.contrib.auth.models import User

# Verificar se o usuário já existe
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@biblioteca.local',
        password='AdminBiblioteca@2024'
    )
    print("Superusuário criado com sucesso!")
    print("Usuário: admin")
    print("Senha: AdminBiblioteca@2024")
else:
    print("Usuário 'admin' já existe!")
