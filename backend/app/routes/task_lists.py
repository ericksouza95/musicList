from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.task_list import TaskList
from app.models.task import Task

task_lists_bp = Blueprint('task_lists', __name__)


@task_lists_bp.route('/', methods=['GET'])
@jwt_required()
def get_task_lists():
    """Listar todas as listas de tarefas do usuário"""
    try:
        current_user_id = get_jwt_identity()
        
        # Parâmetros de query
        include_archived = request.args.get('include_archived', 'false').lower() == 'true'
        
        # Query base
        query = TaskList.query.filter_by(user_id=current_user_id)
        
        # Filtrar arquivadas se necessário
        if not include_archived:
            query = query.filter_by(is_archived=False)
        
        task_lists = query.order_by(TaskList.created_at.desc()).all()
        
        return jsonify({
            'task_lists': [task_list.to_dict() for task_list in task_lists],
            'total': len(task_lists)
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@task_lists_bp.route('/', methods=['POST'])
@jwt_required()
def create_task_list():
    """Criar nova lista de tarefas"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validações
        if not data.get('title'):
            return jsonify({'error': 'Título é obrigatório'}), 400
        
        if len(data['title']) > 100:
            return jsonify({'error': 'Título deve ter no máximo 100 caracteres'}), 400
        
        # Verificar se já existe uma lista com o mesmo nome
        existing = TaskList.query.filter_by(
            user_id=current_user_id,
            title=data['title']
        ).first()
        
        if existing:
            return jsonify({'error': 'Já existe uma lista com este nome'}), 409
        
        # Criar nova lista
        task_list = TaskList(
            title=data['title'],
            description=data.get('description', ''),
            color=data.get('color', '#1976d2'),
            user_id=current_user_id
        )
        
        db.session.add(task_list)
        db.session.commit()
        
        return jsonify({
            'message': 'Lista criada com sucesso',
            'task_list': task_list.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@task_lists_bp.route('/<int:list_id>', methods=['GET'])
@jwt_required()
def get_task_list(list_id):
    """Obter lista específica com suas tarefas"""
    try:
        current_user_id = get_jwt_identity()
        
        task_list = TaskList.query.filter_by(
            id=list_id,
            user_id=current_user_id
        ).first()
        
        if not task_list:
            return jsonify({'error': 'Lista não encontrada'}), 404
        
        # Parâmetros de query para filtrar tarefas
        include_completed = request.args.get('include_completed', 'true').lower() == 'true'
        
        # Obter tarefas da lista
        tasks_query = Task.query.filter_by(task_list_id=list_id)
        
        if not include_completed:
            tasks_query = tasks_query.filter_by(completed=False)
        
        tasks = tasks_query.order_by(
            Task.completed.asc(),  # Não concluídas primeiro
            Task.priority.desc(),  # Por prioridade
            Task.due_date.asc()    # Por data de vencimento
        ).all()
        
        task_list_dict = task_list.to_dict()
        task_list_dict['tasks'] = [task.to_dict() for task in tasks]
        
        return jsonify({'task_list': task_list_dict})
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@task_lists_bp.route('/<int:list_id>', methods=['PUT'])
@jwt_required()
def update_task_list(list_id):
    """Atualizar lista de tarefas"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        task_list = TaskList.query.filter_by(
            id=list_id,
            user_id=current_user_id
        ).first()
        
        if not task_list:
            return jsonify({'error': 'Lista não encontrada'}), 404
        
        # Validações
        if 'title' in data:
            if not data['title']:
                return jsonify({'error': 'Título é obrigatório'}), 400
            
            if len(data['title']) > 100:
                return jsonify({'error': 'Título deve ter no máximo 100 caracteres'}), 400
            
            # Verificar duplicata (exceto a própria lista)
            existing = TaskList.query.filter(
                TaskList.user_id == current_user_id,
                TaskList.title == data['title'],
                TaskList.id != list_id
            ).first()
            
            if existing:
                return jsonify({'error': 'Já existe uma lista com este nome'}), 409
            
            task_list.title = data['title']
        
        # Atualizar outros campos
        if 'description' in data:
            task_list.description = data['description']
        
        if 'color' in data:
            task_list.color = data['color']
        
        if 'is_archived' in data:
            task_list.is_archived = data['is_archived']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Lista atualizada com sucesso',
            'task_list': task_list.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@task_lists_bp.route('/<int:list_id>', methods=['DELETE'])
@jwt_required()
def delete_task_list(list_id):
    """Deletar lista de tarefas"""
    try:
        current_user_id = get_jwt_identity()
        
        task_list = TaskList.query.filter_by(
            id=list_id,
            user_id=current_user_id
        ).first()
        
        if not task_list:
            return jsonify({'error': 'Lista não encontrada'}), 404
        
        # Verificar se é a única lista do usuário
        user_lists_count = TaskList.query.filter_by(
            user_id=current_user_id,
            is_archived=False
        ).count()
        
        if user_lists_count <= 1:
            return jsonify({'error': 'Não é possível deletar a única lista ativa'}), 400
        
        # Deletar lista (cascade deletará as tarefas)
        db.session.delete(task_list)
        db.session.commit()
        
        return jsonify({'message': 'Lista deletada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@task_lists_bp.route('/<int:list_id>/archive', methods=['PATCH'])
@jwt_required()
def toggle_archive_task_list(list_id):
    """Arquivar/desarquivar lista de tarefas"""
    try:
        current_user_id = get_jwt_identity()
        
        task_list = TaskList.query.filter_by(
            id=list_id,
            user_id=current_user_id
        ).first()
        
        if not task_list:
            return jsonify({'error': 'Lista não encontrada'}), 404
        
        # Verificar se é a única lista ativa
        if not task_list.is_archived:
            active_lists_count = TaskList.query.filter_by(
                user_id=current_user_id,
                is_archived=False
            ).count()
            
            if active_lists_count <= 1:
                return jsonify({'error': 'Não é possível arquivar a única lista ativa'}), 400
        
        task_list.is_archived = not task_list.is_archived
        db.session.commit()
        
        action = 'arquivada' if task_list.is_archived else 'desarquivada'
        
        return jsonify({
            'message': f'Lista {action} com sucesso',
            'task_list': task_list.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@task_lists_bp.route('/<int:list_id>/stats', methods=['GET'])
@jwt_required()
def get_task_list_stats(list_id):
    """Obter estatísticas da lista de tarefas"""
    try:
        current_user_id = get_jwt_identity()
        
        task_list = TaskList.query.filter_by(
            id=list_id,
            user_id=current_user_id
        ).first()
        
        if not task_list:
            return jsonify({'error': 'Lista não encontrada'}), 404
        
        # Calcular estatísticas
        total_tasks = len(task_list.tasks)
        completed_tasks = len([t for t in task_list.tasks if t.completed])
        pending_tasks = total_tasks - completed_tasks
        overdue_tasks = len([t for t in task_list.tasks if t.is_overdue()])
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Estatísticas por prioridade
        priority_stats = {}
        for priority_info in Task.get_priorities():
            priority = priority_info['value']
            priority_tasks = [t for t in task_list.tasks if t.priority == priority]
            priority_stats[priority] = {
                'total': len(priority_tasks),
                'completed': len([t for t in priority_tasks if t.completed]),
                'pending': len([t for t in priority_tasks if not t.completed])
            }
        
        return jsonify({
            'stats': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'overdue_tasks': overdue_tasks,
                'completion_rate': round(completion_rate, 2),
                'priority_breakdown': priority_stats
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500 