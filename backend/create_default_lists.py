#!/usr/bin/env python3
"""
Script para criar listas de tarefas padrão para usuários existentes
"""

import sys
import os

# Adicionar o diretório parent ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.task_list import TaskList
from app.models.task import Task

def create_default_lists():
    """Cria listas padrão para todos os usuários existentes"""
    app = create_app()
    
    with app.app_context():
        try:
            # Buscar todos os usuários
            users = User.query.all()
            print(f"Encontrados {len(users)} usuários")
            
            for user in users:
                # Verificar se o usuário já tem listas
                existing_lists = TaskList.query.filter_by(user_id=user.id).count()
                
                if existing_lists == 0:
                    print(f"Criando lista padrão para {user.username}...")
                    
                    # Criar lista padrão
                    default_list = TaskList(
                        title='Minhas Tarefas',
                        description='Lista padrão de tarefas',
                        color='#1976d2',
                        user_id=user.id
                    )
                    db.session.add(default_list)
                    db.session.flush()  # Para obter o ID
                    
                    # Criar algumas tarefas de exemplo
                    example_tasks = [
                        {
                            'title': 'Bem-vindo ao sistema TO-DO!',
                            'description': 'Esta é sua primeira tarefa. Explore as funcionalidades do sistema.',
                            'priority': 'medium'
                        },
                        {
                            'title': 'Configurar perfil',
                            'description': 'Atualize suas informações pessoais no seu perfil.',
                            'priority': 'low'
                        },
                        {
                            'title': 'Criar nova lista',
                            'description': 'Experimente criar uma nova lista de tarefas personalizada.',
                            'priority': 'low'
                        }
                    ]
                    
                    for task_data in example_tasks:
                        task = Task(
                            title=task_data['title'],
                            description=task_data['description'],
                            priority=task_data['priority'],
                            task_list_id=default_list.id,
                            user_id=user.id
                        )
                        db.session.add(task)
                    
                    print(f"✅ Lista criada para {user.username}")
                    
                else:
                    print(f"⏭️  {user.username} já possui {existing_lists} lista(s)")
            
            # Salvar todas as alterações
            db.session.commit()
            print("\n🎉 Processo concluído com sucesso!")
            
            # Mostrar estatísticas finais
            total_lists = TaskList.query.count()
            total_tasks = Task.query.count()
            print(f"\n📊 Estatísticas:")
            print(f"   • Total de usuários: {len(users)}")
            print(f"   • Total de listas: {total_lists}")
            print(f"   • Total de tarefas: {total_tasks}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    create_default_lists() 