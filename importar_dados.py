# importar_dados.py
import sqlite3
import os

print("Iniciando importação de dados...")

# Conectar ao banco antigo
conn_old = sqlite3.connect('db.sqlite3.old')
cursor_old = conn_old.cursor()

# Conectar ao banco novo
conn_new = sqlite3.connect('db.sqlite3')
cursor_new = conn_new.cursor()

# Lista de tabelas para importar (exceto as de migração)
tabelas = [
    'core_perfilusuario',
    'core_livro',
    'core_emprestimo',
    'core_bibliotecainfo',
    'core_evento',
    'core_livropdf',
    'auth_user',
    'auth_group',
    'auth_user_groups',
    'auth_user_user_permissions',
]

for tabela in tabelas:
    try:
        # Verificar se a tabela existe no banco antigo
        cursor_old.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabela}'")
        if cursor_old.fetchone():
            # Pegar dados da tabela antiga
            cursor_old.execute(f"SELECT * FROM {tabela}")
            dados = cursor_old.fetchall()
            
            # Pegar nomes das colunas
            cursor_old.execute(f"PRAGMA table_info({tabela})")
            colunas = [col[1] for col in cursor_old.fetchall()]
            
            if dados:
                # Inserir dados na tabela nova
                placeholders = ','.join(['?' for _ in colunas])
                colunas_str = ','.join(colunas)
                
                for row in dados:
                    try:
                        cursor_new.execute(f"INSERT OR IGNORE INTO {tabela} ({colunas_str}) VALUES ({placeholders})", row)
                    except Exception as e:
                        print(f"Erro ao inserir em {tabela}: {e}")
                
                conn_new.commit()
                print(f"✓ {len(dados)} registros importados de {tabela}")
    except Exception as e:
        print(f"Erro ao processar tabela {tabela}: {e}")

conn_old.close()
conn_new.close()
print("\nImportação concluída!")