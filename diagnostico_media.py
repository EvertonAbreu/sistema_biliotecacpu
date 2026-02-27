import os
import sys
import django

# Configurar Django
sys.path.append('/Users/evertonabreu/Documents/biblioteca_publica')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from core.models import LivroPDF
from django.conf import settings

print("=== DIAGNÓSTICO DO SISTEMA DE MEDIA ===\n")

# 1. Verificar configurações
print("1. CONFIGURAÇÕES:")
print(f"   BASE_DIR: {settings.BASE_DIR}")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")
print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"   DEBUG: {settings.DEBUG}")

# 2. Verificar se a pasta media existe
print("\n2. PASTA MEDIA:")
media_path = settings.MEDIA_ROOT
if os.path.exists(media_path):
    print(f"   ✅ Pasta media existe: {media_path}")
    
    # Listar conteúdo
    for root, dirs, files in os.walk(media_path):
        level = root.replace(media_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f'{subindent}{file}')
else:
    print(f"   ❌ Pasta media NÃO existe: {media_path}")

# 3. Verificar livros PDF no banco
print("\n3. LIVROS PDF NO BANCO:")
livros = LivroPDF.objects.all()
print(f"   Total de livros: {livros.count()}")

for livro in livros:
    print(f"\n   Livro: {livro.titulo} (ID: {livro.id})")
    print(f"   Arquivo PDF: {livro.arquivo_pdf}")
    
    if livro.arquivo_pdf:
        # Caminho absoluto
        abs_path = livro.arquivo_pdf.path
        print(f"   Caminho absoluto: {abs_path}")
        
        # Verificar se existe
        if os.path.exists(abs_path):
            print(f"   ✅ Arquivo existe no servidor")
            print(f"   Tamanho: {os.path.getsize(abs_path)} bytes")
            
            # URL que deveria funcionar
            expected_url = f"http://127.0.0.1:8000{settings.MEDIA_URL}{livro.arquivo_pdf.name}"
            print(f"   URL esperada: {expected_url}")
        else:
            print(f"   ❌ Arquivo NÃO existe no servidor")
            
            # Verificar caminho relativo
            rel_path = livro.arquivo_pdf.name
            print(f"   Caminho relativo: {rel_path}")
            
            # Tentar encontrar o arquivo
            possible_paths = [
                os.path.join(settings.BASE_DIR, rel_path),
                os.path.join(settings.MEDIA_ROOT, rel_path),
                livro.arquivo_pdf.path,
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"   ✅ Encontrado em: {path}")
                    break

# 4. Testar URLs
print("\n4. TESTE DE URLS:")
if livros.exists():
    if livro.arquivo_pdf:
        test_url = f"http://127.0.0.1:8000{livro.arquivo_pdf.url}"
        print(f"   URL para teste: {test_url}")
        print(f"   Tente acessar esta URL diretamente no navegador")

print("\n=== FIM DO DIAGNÓSTICO ===")