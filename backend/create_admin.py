#!/usr/bin/env python3
"""
Script para criar um usuário administrador padrão
"""
import os
import sys
from datetime import datetime

# Configurar variáveis de ambiente
os.environ['FLASK_APP'] = 'run.py'
os.environ['FLASK_ENV'] = 'development'

# Adicionar diretório pai ao path para importar módulos do app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_default_users():
    """Cria usuários padrão diretamente no banco"""
    try:
        from app import create_app, db
        from app.models.user import User
        
        # Criar app em contexto isolado
        app = create_app()
        
        with app.app_context():
            # Verificar conexão com banco
            try:
                # Criar tabelas se não existirem
                db.create_all()
                print("✅ Banco de dados verificado/criado")
            except Exception as e:
                print(f"❌ Erro ao acessar banco: {e}")
                return False
            
            success = True
            
            # Criar usuário admin
            try:
                admin = User.query.filter_by(username='admin').first()
                
                if not admin:
                    admin = User(
                        username='admin',
                        email='admin@musiclist.com',
                        first_name='Administrador',
                        last_name='Sistema',
                        is_admin=True,
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    admin.set_password('admin123')
                    
                    db.session.add(admin)
                    db.session.commit()
                    
                    print("🎉 Usuário ADMIN criado!")
                    print("   Username: admin")
                    print("   Senha: admin123")
                else:
                    print("✅ Usuário admin já existe")
                    
            except Exception as e:
                print(f"❌ Erro ao criar admin: {e}")
                success = False
                db.session.rollback()
            
            # Criar usuário teste
            try:
                test_user = User.query.filter_by(username='teste').first()
                
                if not test_user:
                    test_user = User(
                        username='teste',
                        email='teste@musiclist.com',
                        first_name='Usuário',
                        last_name='Teste',
                        is_admin=False,
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    test_user.set_password('teste123')
                    
                    db.session.add(test_user)
                    db.session.commit()
                    
                    print("🎉 Usuário TESTE criado!")
                    print("   Username: teste")
                    print("   Senha: teste123")
                else:
                    print("✅ Usuário teste já existe")
                    
            except Exception as e:
                print(f"❌ Erro ao criar teste: {e}")
                success = False
                db.session.rollback()
            
            # Listar usuários
            try:
                users = User.query.all()
                print(f"\n👥 Total de usuários: {len(users)}")
                
                for user in users:
                    admin_label = "👑 ADMIN" if user.is_admin else "👤 USER"
                    print(f"   {admin_label}: {user.username} ({user.email})")
                    
            except Exception as e:
                print(f"❌ Erro ao listar usuários: {e}")
            
            return success
            
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("💡 Certifique-se de que está no diretório backend e o ambiente virtual está ativo")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def main():
    """Função principal"""
    print("🎵" + "=" * 50 + "🎵")
    print("     MUSIC LIST - CRIAR USUÁRIOS PADRÃO")
    print("🎵" + "=" * 50 + "🎵")
    print()
    
    success = create_default_users()
    
    if success:
        print("\n🎉 SUCESSO! Usuários criados/verificados")
        print("🌐 Agora você pode fazer login no sistema:")
        print("   • http://localhost:3000")
        print()
        print("📋 CREDENCIAIS DISPONÍVEIS:")
        print("   👑 ADMIN: admin / admin123")
        print("   👤 USER:  teste / teste123")
    else:
        print("\n❌ Alguns erros ocorreram. Verifique as mensagens acima.")
    
    print("\n" + "🎵" + "=" * 50 + "🎵")

if __name__ == '__main__':
    main() 