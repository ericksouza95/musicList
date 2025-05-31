#!/usr/bin/env python3
"""
Script para configurar o banco de dados PostgreSQL
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

def create_database():
    """Cria o banco de dados PostgreSQL"""
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurações do banco
    host = os.environ.get('POSTGRES_HOST', 'localhost')
    port = os.environ.get('POSTGRES_PORT', '5432')
    admin_user = 'postgres'  # Usuário padrão do PostgreSQL
    admin_password = input("Digite a senha do usuário 'postgres': ")
    
    db_name = os.environ.get('POSTGRES_DB', 'music_app_db')
    db_user = os.environ.get('POSTGRES_USER', 'music_user')
    db_password = os.environ.get('POSTGRES_PASSWORD', 'music_password')
    
    try:
        # Conectar como admin
        print(f"Conectando ao PostgreSQL em {host}:{port}...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=admin_user,
            password=admin_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar se usuário existe
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (db_user,))
        if not cursor.fetchone():
            print(f"Criando usuário '{db_user}'...")
            cursor.execute(f"CREATE USER {db_user} WITH PASSWORD %s", (db_password,))
        else:
            print(f"Usuário '{db_user}' já existe.")
        
        # Verificar se banco existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (db_name,))
        if not cursor.fetchone():
            print(f"Criando banco de dados '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user}")
        else:
            print(f"Banco de dados '{db_name}' já existe.")
        
        # Dar privilégios ao usuário
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Banco de dados configurado com sucesso!")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Database: {db_name}")
        print(f"User: {db_user}")
        print(f"URL: postgresql://{db_user}:{db_password}@{host}:{port}/{db_name}")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao configurar banco de dados: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_connection():
    """Testa a conexão com o banco configurado"""
    load_dotenv()
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL não configurada")
        return False
    
    try:
        print("Testando conexão com o banco...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute('SELECT version()')
        version = cursor.fetchone()
        print(f"✅ Conexão bem-sucedida! PostgreSQL version: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    print("🗄️  Configurador do Banco PostgreSQL - Music List")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_connection()
    else:
        print("Este script irá:")
        print("1. Criar um usuário no PostgreSQL")
        print("2. Criar o banco de dados")
        print("3. Configurar permissões")
        print()
        
        response = input("Continuar? (s/N): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            if create_database():
                print("\nTestando conexão...")
                test_connection()
        else:
            print("Operação cancelada.") 