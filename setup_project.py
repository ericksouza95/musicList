#!/usr/bin/env python3
"""
Script para configuração inicial do projeto Music List
Instala todas as dependências automaticamente
"""
import os
import sys
import subprocess
from pathlib import Path

class ProjectSetup:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.backend_dir = self.project_dir / "backend"
        self.frontend_dir = self.project_dir / "frontend"
        
    def print_banner(self):
        """Exibe banner de início"""
        print("🔧" + "=" * 60 + "🔧")
        print("        MUSIC LIST SYSTEM - SETUP INICIAL")
        print("🔧" + "=" * 60 + "🔧")
        print()
        
    def check_python(self):
        """Verifica se Python está instalado"""
        print("🐍 Verificando Python...")
        try:
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 8):
                print("❌ Python 3.8+ é necessário!")
                return False
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} encontrado!")
            return True
        except Exception as e:
            print(f"❌ Erro ao verificar Python: {e}")
            return False
            
    def check_node(self):
        """Verifica se Node.js está instalado"""
        print("📦 Verificando Node.js...")
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js {result.stdout.strip()} encontrado!")
                return True
            else:
                print("❌ Node.js não encontrado!")
                return False
        except FileNotFoundError:
            print("❌ Node.js não está instalado!")
            print("Baixe em: https://nodejs.org/")
            return False
            
    def setup_backend(self):
        """Configura o backend"""
        print("🔧 Configurando backend...")
        
        # Verificar se diretório backend existe
        if not self.backend_dir.exists():
            print("❌ Diretório backend não encontrado!")
            return False
            
        # Criar ambiente virtual
        venv_dir = self.backend_dir / ".venv"
        if not venv_dir.exists():
            print("📦 Criando ambiente virtual...")
            result = subprocess.run([
                sys.executable, '-m', 'venv', str(venv_dir)
            ], cwd=self.backend_dir)
            
            if result.returncode != 0:
                print("❌ Erro ao criar ambiente virtual!")
                return False
                
        # Ativar ambiente virtual e instalar dependências
        print("📥 Instalando dependências do backend...")
        
        if os.name == 'nt':  # Windows
            activate_script = venv_dir / "Scripts" / "activate.bat"
            pip_path = venv_dir / "Scripts" / "pip.exe"
        else:  # Linux/Mac
            activate_script = venv_dir / "bin" / "activate"
            pip_path = venv_dir / "bin" / "pip"
            
        # Instalar dependências
        result = subprocess.run([
            str(pip_path), 'install', '-r', 'requirements.txt'
        ], cwd=self.backend_dir)
        
        if result.returncode != 0:
            print("❌ Erro ao instalar dependências do backend!")
            return False
            
        print("✅ Backend configurado!")
        return True
        
    def setup_frontend(self):
        """Configura o frontend"""
        print("🎨 Configurando frontend...")
        
        # Verificar se diretório frontend existe
        if not self.frontend_dir.exists():
            print("❌ Diretório frontend não encontrado!")
            return False
            
        # Instalar dependências
        print("📥 Instalando dependências do frontend...")
        result = subprocess.run(['npm', 'install'], cwd=self.frontend_dir)
        
        if result.returncode != 0:
            print("❌ Erro ao instalar dependências do frontend!")
            return False
            
        print("✅ Frontend configurado!")
        return True
        
    def setup_database(self):
        """Configura o banco de dados"""
        print("🗄️  Configurando banco de dados...")
        
        # Copiar arquivo de configuração
        env_example = self.backend_dir / "env.example"
        env_file = self.backend_dir / ".env"
        
        if not env_file.exists() and env_example.exists():
            print("📝 Criando arquivo .env...")
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Arquivo .env criado!")
        
        # Executar migrações
        print("🔄 Executando migrações do banco...")
        
        if os.name == 'nt':  # Windows
            python_path = self.backend_dir / ".venv" / "Scripts" / "python.exe"
        else:  # Linux/Mac
            python_path = self.backend_dir / ".venv" / "bin" / "python"
            
        # Inicializar migrações se necessário
        migrations_dir = self.backend_dir / "migrations"
        if not migrations_dir.exists():
            result = subprocess.run([
                str(python_path), '-m', 'flask', 'db', 'init'
            ], cwd=self.backend_dir, env={**os.environ, 'FLASK_APP': 'run.py'})
            
        # Criar e aplicar migração
        subprocess.run([
            str(python_path), '-m', 'flask', 'db', 'migrate', 
            '-m', 'Initial migration'
        ], cwd=self.backend_dir, env={**os.environ, 'FLASK_APP': 'run.py'})
        
        result = subprocess.run([
            str(python_path), '-m', 'flask', 'db', 'upgrade'
        ], cwd=self.backend_dir, env={**os.environ, 'FLASK_APP': 'run.py'})
        
        if result.returncode == 0:
            print("✅ Banco de dados configurado!")
            return True
        else:
            print("⚠️  Aviso: Erro na configuração do banco de dados")
            print("Você pode configurar manualmente mais tarde")
            return True
            
    def run_setup(self):
        """Executa a configuração completa"""
        self.print_banner()
        
        print("🚀 Iniciando configuração do projeto...\n")
        
        # Verificar pré-requisitos
        if not self.check_python():
            return False
            
        if not self.check_node():
            return False
            
        print()
        
        # Configurar componentes
        if not self.setup_backend():
            return False
            
        if not self.setup_frontend():
            return False
            
        if not self.setup_database():
            return False
            
        print("\n🎉 Configuração concluída com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Execute: python start_app.py")
        print("2. Acesse: http://localhost:3000")
        print("3. Configure suas credenciais do Spotify no .env")
        print("\n💡 Dica: Use 'python start_app.py' para iniciar o sistema completo")
        
        return True


def main():
    """Função principal"""
    setup = ProjectSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🤔 Deseja iniciar o sistema agora? (s/N): ", end="")
        try:
            response = input().lower()
            if response in ['s', 'sim', 'y', 'yes']:
                print("\n🚀 Iniciando sistema...")
                os.system('python start_app.py')
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 