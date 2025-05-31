#!/usr/bin/env python3
"""
Script para iniciar o sistema completo de música
Inicia tanto o backend (Flask) quanto o frontend (Vue.js)
"""
import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

class MusicAppLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_dir = Path(__file__).parent / "backend"
        self.frontend_dir = Path(__file__).parent / "frontend"
        self.running = True
        
    def print_banner(self):
        """Exibe banner de início"""
        print("🎵" + "=" * 60 + "🎵")
        print("           MUSIC LIST SYSTEM LAUNCHER")
        print("🎵" + "=" * 60 + "🎵")
        print()
        
    def check_dependencies(self):
        """Verifica se as dependências estão instaladas"""
        print("🔍 Verificando dependências...")
        
        # Verificar backend
        backend_venv = self.backend_dir / ".venv"
        if not backend_venv.exists():
            print("❌ Ambiente virtual do backend não encontrado!")
            print("Execute: python setup_project.py")
            return False
            
        requirements_file = self.backend_dir / "requirements.txt"
        if not requirements_file.exists():
            print("❌ Arquivo requirements.txt não encontrado!")
            return False
            
        # Verificar frontend
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            print("📦 Dependências do frontend não encontradas. Instalando...")
            if not self.install_frontend_dependencies():
                return False
            
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            print("❌ Arquivo package.json não encontrado!")
            return False
            
        print("✅ Dependências verificadas!")
        return True
        
    def install_frontend_dependencies(self):
        """Instala dependências do frontend automaticamente"""
        print("📦 Instalando dependências do Node.js...")
        try:
            # Verificar se npm está disponível
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ NPM não encontrado! Instale Node.js: https://nodejs.org/")
                return False
                
            # Instalar dependências
            result = subprocess.run(['npm', 'install'], 
                                  cwd=self.frontend_dir,
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependências do frontend instaladas!")
                return True
            else:
                print(f"❌ Erro ao instalar dependências: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ NPM não encontrado! Instale Node.js: https://nodejs.org/")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False
        
    def start_backend(self):
        """Inicia o servidor Flask"""
        print("🚀 Iniciando backend (Flask)...")
        
        # Comando para ativar venv e executar Flask
        if os.name == 'nt':  # Windows
            python_path = self.backend_dir / ".venv" / "Scripts" / "python.exe"
            cmd = f'cd /d "{self.backend_dir}" && "{python_path}" run.py'
        else:  # Linux/Mac
            python_path = self.backend_dir / ".venv" / "bin" / "python"
            cmd = f'cd "{self.backend_dir}" && "{python_path}" run.py'
        
        try:
            if os.name == 'nt':
                self.backend_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                self.backend_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    preexec_fn=os.setsid
                )
            
            print("✅ Backend iniciado! (http://localhost:5000)")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar backend: {e}")
            return False
            
    def start_frontend(self):
        """Inicia o servidor Vue.js"""
        print("🚀 Iniciando frontend (Vue.js)...")
        
        cmd = f'cd /d "{self.frontend_dir}" && npm run serve' if os.name == 'nt' else f'cd "{self.frontend_dir}" && npm run serve'
        
        try:
            if os.name == 'nt':
                self.frontend_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                self.frontend_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    preexec_fn=os.setsid
                )
            
            print("✅ Frontend iniciado! (http://localhost:3000)")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar frontend: {e}")
            return False
            
    def wait_for_services(self):
        """Aguarda os serviços estarem prontos"""
        print("⏳ Aguardando serviços inicializarem...")
        
        # Aguardar tempo fixo para inicialização
        for i in range(10):
            print(f"   Aguardando... {i+1}/10")
            time.sleep(1)
            
        print("✅ Serviços devem estar prontos!")
        return True
            
    def open_browser(self):
        """Abre o navegador automaticamente"""
        import webbrowser
        
        print("🌐 Abrindo navegador...")
        try:
            webbrowser.open("http://localhost:3000")
            print("✅ Navegador aberto!")
        except Exception as e:
            print(f"⚠️  Não foi possível abrir o navegador: {e}")
            
    def monitor_processes(self):
        """Monitora os processos em execução"""
        while self.running:
            time.sleep(5)
            
            # Verificar se os processos ainda estão rodando
            if self.backend_process and self.backend_process.poll() is not None:
                print("⚠️  Backend parou de funcionar!")
                
            if self.frontend_process and self.frontend_process.poll() is not None:
                print("⚠️  Frontend parou de funcionar!")
                
    def signal_handler(self, signum, frame):
        """Manipula sinais de interrupção"""
        print("\n🛑 Parando aplicação...")
        self.stop()
        
    def stop(self):
        """Para todos os processos"""
        self.running = False
        
        if self.backend_process:
            print("🛑 Parando backend...")
            try:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.backend_process.pid)], 
                                 capture_output=True)
                else:
                    os.killpg(os.getpgid(self.backend_process.pid), signal.SIGTERM)
                print("✅ Backend parado!")
            except Exception as e:
                print(f"⚠️  Erro ao parar backend: {e}")
                
        if self.frontend_process:
            print("🛑 Parando frontend...")
            try:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.frontend_process.pid)], 
                                 capture_output=True)
                else:
                    os.killpg(os.getpgid(self.frontend_process.pid), signal.SIGTERM)
                print("✅ Frontend parado!")
            except Exception as e:
                print(f"⚠️  Erro ao parar frontend: {e}")
                
        print("👋 Aplicação encerrada!")
        
    def run(self):
        """Executa o launcher completo"""
        self.print_banner()
        
        # Configurar manipulador de sinais
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Verificar dependências
        if not self.check_dependencies():
            print("\n❌ Não foi possível iniciar. Execute 'python setup_project.py' primeiro.")
            return False
            
        try:
            # Iniciar backend
            if not self.start_backend():
                return False
                
            # Aguardar backend estar pronto
            print("⏳ Aguardando backend carregar...")
            time.sleep(5)
                
            # Iniciar frontend
            if not self.start_frontend():
                self.stop()
                return False
                
            # Aguardar serviços
            print("⏳ Aguardando frontend carregar...")
            time.sleep(10)
                
            # Abrir navegador
            self.open_browser()
            
            # Iniciar monitoramento em thread separada
            monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            monitor_thread.start()
            
            print("\n🎉 Sistema inicializado com sucesso!")
            print("📱 Frontend: http://localhost:3000")
            print("🔧 Backend:  http://localhost:5000")
            print("📊 API Docs: http://localhost:5000/api")
            print("\n💡 Pressione Ctrl+C para parar...")
            
            # Manter o script rodando
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário...")
            self.stop()
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            self.stop()
            return False
            
        return True


def main():
    """Função principal"""
    launcher = MusicAppLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 