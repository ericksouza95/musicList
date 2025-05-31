from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.task import Task
from app.models.task_list import TaskList

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """Listar todas as tarefas do usuário"""
    try:
        current_user_id = get_jwt_identity()
        
        # Parâmetros de query
        task_list_id = request.args.get('task_list_id', type=int)
        completed = request.args.get('completed')
        priority = request.args.get('priority')
        search = request.args.get('search', '').strip()
        overdue_only = request.args.get('overdue_only', 'false').lower() == 'true'
        
        # Query base
        query = Task.query.filter_by(user_id=current_user_id)
        
        # Filtros
        if task_list_id:
            query = query.filter_by(task_list_id=task_list_id)
        
        if completed is not None:
            is_completed = completed.lower() == 'true'
            query = query.filter_by(completed=is_completed)
        
        if priority:
            query = query.filter_by(priority=priority)
        
        if search:
            query = query.filter(
                Task.title.ilike(f'%{search}%') |
                Task.description.ilike(f'%{search}%')
            )
        
        # Executar query
        tasks = query.all()
        
        # Filtrar vencidas (não pode ser feito direto no SQL facilmente)
        if overdue_only:
            tasks = [task for task in tasks if task.is_overdue()]
        
        # Ordenar
        tasks.sort(key=lambda t: (
            t.completed,  # Não concluídas primeiro
            -{'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}.get(t.priority, 0),  # Por prioridade
            t.due_date or datetime.max  # Por data de vencimento
        ))
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks],
            'total': len(tasks)
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """Criar nova tarefa"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validações
        if not data.get('title'):
            return jsonify({'error': 'Título é obrigatório'}), 400
        
        if len(data['title']) > 200:
            return jsonify({'error': 'Título deve ter no máximo 200 caracteres'}), 400
        
        task_list_id = data.get('task_list_id')
        if not task_list_id:
            return jsonify({'error': 'Lista de tarefas é obrigatória'}), 400
        
        # Verificar se a lista pertence ao usuário
        task_list = TaskList.query.filter_by(
            id=task_list_id,
            user_id=current_user_id
        ).first()
        
        if not task_list:
            return jsonify({'error': 'Lista de tarefas não encontrada'}), 404
        
        # Validar prioridade
        valid_priorities = [p['value'] for p in Task.get_priorities()]
        priority = data.get('priority', 'medium')
        if priority not in valid_priorities:
            return jsonify({'error': 'Prioridade inválida'}), 400
        
        # Validar data de vencimento
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Formato de data inválido'}), 400
        
        # Criar nova tarefa
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=priority,
            due_date=due_date,
            task_list_id=task_list_id,
            user_id=current_user_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Tarefa criada com sucesso',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Obter tarefa específica"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user_id
        ).first()
        
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        return jsonify({'task': task.to_dict()})
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Atualizar tarefa"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user_id
        ).first()
        
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        # Validações
        if 'title' in data:
            if not data['title']:
                return jsonify({'error': 'Título é obrigatório'}), 400
            
            if len(data['title']) > 200:
                return jsonify({'error': 'Título deve ter no máximo 200 caracteres'}), 400
            
            task.title = data['title']
        
        if 'description' in data:
            task.description = data['description']
        
        if 'priority' in data:
            valid_priorities = [p['value'] for p in Task.get_priorities()]
            if data['priority'] not in valid_priorities:
                return jsonify({'error': 'Prioridade inválida'}), 400
            task.priority = data['priority']
        
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Formato de data inválido'}), 400
            else:
                task.due_date = None
        
        if 'task_list_id' in data:
            # Verificar se a nova lista pertence ao usuário
            new_list = TaskList.query.filter_by(
                id=data['task_list_id'],
                user_id=current_user_id
            ).first()
            
            if not new_list:
                return jsonify({'error': 'Lista de tarefas não encontrada'}), 404
            
            task.task_list_id = data['task_list_id']
        
        if 'completed' in data:
            if data['completed'] != task.completed:
                task.toggle_completion()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Tarefa atualizada com sucesso',
            'task': task.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Deletar tarefa"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user_id
        ).first()
        
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Tarefa deletada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@tasks_bp.route('/<int:task_id>/toggle', methods=['PATCH'])
@jwt_required()
def toggle_task_completion(task_id):
    """Marcar/desmarcar tarefa como concluída"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user_id
        ).first()
        
        if not task:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        task.toggle_completion()
        db.session.commit()
        
        status = 'concluída' if task.completed else 'reaberta'
        
        return jsonify({
            'message': f'Tarefa {status} com sucesso',
            'task': task.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@tasks_bp.route('/priorities', methods=['GET'])
def get_priorities():
    """Obter lista de prioridades disponíveis"""
    return jsonify({'priorities': Task.get_priorities()})


@tasks_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Obter estatísticas para dashboard"""
    try:
        current_user_id = get_jwt_identity()
        
        # Tarefas do usuário
        all_tasks = Task.query.filter_by(user_id=current_user_id).all()
        
        # Estatísticas gerais
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.completed])
        pending_tasks = total_tasks - completed_tasks
        overdue_tasks = len([t for t in all_tasks if t.is_overdue()])
        
        # Tarefas por prioridade
        priority_stats = {}
        for priority_info in Task.get_priorities():
            priority = priority_info['value']
            priority_tasks = [t for t in all_tasks if t.priority == priority and not t.completed]
            priority_stats[priority] = len(priority_tasks)
        
        # Tarefas recentes (últimos 7 dias)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_tasks = [t for t in all_tasks if t.created_at >= week_ago]
        
        # Próximas tarefas (próximos 7 dias)
        next_week = datetime.utcnow() + timedelta(days=7)
        upcoming_tasks = [
            t for t in all_tasks 
            if t.due_date and not t.completed and t.due_date <= next_week
        ]
        upcoming_tasks.sort(key=lambda t: t.due_date)
        
        return jsonify({
            'stats': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'overdue_tasks': overdue_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
                'priority_breakdown': priority_stats,
                'recent_tasks_count': len(recent_tasks),
                'upcoming_tasks_count': len(upcoming_tasks)
            },
            'upcoming_tasks': [task.to_dict() for task in upcoming_tasks[:5]]  # Próximas 5
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@tasks_bp.route('/bulk', methods=['POST'])
@jwt_required()
def bulk_operations():
    """Operações em lote nas tarefas"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        task_ids = data.get('task_ids', [])
        operation = data.get('operation')
        
        if not task_ids or not operation:
            return jsonify({'error': 'IDs das tarefas e operação são obrigatórios'}), 400
        
        # Buscar tarefas do usuário
        tasks = Task.query.filter(
            Task.id.in_(task_ids),
            Task.user_id == current_user_id
        ).all()
        
        if len(tasks) != len(task_ids):
            return jsonify({'error': 'Algumas tarefas não foram encontradas'}), 404
        
        # Executar operação
        if operation == 'complete':
            for task in tasks:
                if not task.completed:
                    task.toggle_completion()
        
        elif operation == 'incomplete':
            for task in tasks:
                if task.completed:
                    task.toggle_completion()
        
        elif operation == 'delete':
            for task in tasks:
                db.session.delete(task)
        
        elif operation == 'move':
            new_list_id = data.get('target_list_id')
            if not new_list_id:
                return jsonify({'error': 'Lista de destino é obrigatória'}), 400
            
            # Verificar se a lista pertence ao usuário
            target_list = TaskList.query.filter_by(
                id=new_list_id,
                user_id=current_user_id
            ).first()
            
            if not target_list:
                return jsonify({'error': 'Lista de destino não encontrada'}), 404
            
            for task in tasks:
                task.task_list_id = new_list_id
        
        else:
            return jsonify({'error': 'Operação inválida'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': f'Operação {operation} executada em {len(tasks)} tarefa(s)',
            'affected_count': len(tasks)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500 