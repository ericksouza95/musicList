from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from email_validator import validate_email, EmailNotValidError
from app import db
from app.models.user import User

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Lista todos os usuários (apenas admins)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        search = request.args.get('search', '')
        
        # Query base
        query = User.query
        
        # Filtro de busca
        if search:
            query = query.filter(
                (User.username.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%')) |
                (User.first_name.ilike(f'%{search}%')) |
                (User.last_name.ilike(f'%{search}%'))
            )
        
        # Paginação
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': users.has_next,
            'has_prev': users.has_prev
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Obtém um usuário específico"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar permissões (próprio usuário ou admin)
        if current_user_id != user_id and not current_user.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict()})
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Atualiza um usuário"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar permissões (próprio usuário ou admin)
        if current_user_id != user_id and not current_user.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Campos que podem ser atualizados
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        if 'email' in data:
            # Validar email
            try:
                validated_email = validate_email(data['email'])
                email = validated_email.email
                
                # Verificar se email já existe (exceto o atual)
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and existing_user.id != user.id:
                    return jsonify({'error': 'Email já cadastrado'}), 409
                
                user.email = email
            except EmailNotValidError:
                return jsonify({'error': 'Email inválido'}), 400
        
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        # Campos que apenas admins podem alterar
        if current_user.is_admin:
            if 'is_active' in data:
                user.is_active = bool(data['is_active'])
            
            if 'is_admin' in data:
                user.is_admin = bool(data['is_admin'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário atualizado com sucesso',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Deleta um usuário"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar permissões (próprio usuário ou admin)
        if current_user_id != user_id and not current_user.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Impedir auto-exclusão de admin se for o único
        if user.is_admin and current_user_id == user_id:
            admin_count = User.query.filter_by(is_admin=True, is_active=True).count()
            if admin_count <= 1:
                return jsonify({'error': 'Não é possível excluir o último administrador'}), 400
        
        # Em vez de deletar, desativar o usuário
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Usuário desativado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@users_bp.route('/<int:user_id>/playlists', methods=['GET'])
@jwt_required()
def get_user_playlists(user_id):
    """Obtém playlists de um usuário"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Filtrar playlists públicas ou do próprio usuário
        query = user.playlists
        if current_user_id != user_id:
            query = [p for p in user.playlists if p.is_public]
        
        # Converter para dicionário
        playlists = [playlist.to_dict() for playlist in query]
        
        # Simular paginação (poderia ser implementada no banco)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_playlists = playlists[start:end]
        
        return jsonify({
            'playlists': paginated_playlists,
            'total': len(playlists),
            'current_page': page,
            'per_page': per_page,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@users_bp.route('/<int:user_id>/uploads', methods=['GET'])
@jwt_required()
def get_user_uploads(user_id):
    """Obtém músicas enviadas por um usuário"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Filtrar uploads públicos ou do próprio usuário
        query = user.music_uploads
        if current_user_id != user_id:
            query = [m for m in user.music_uploads if m.is_public]
        
        # Converter para dicionário
        uploads = [music.to_dict() for music in query]
        
        # Simular paginação
        start = (page - 1) * per_page
        end = start + per_page
        paginated_uploads = uploads[start:end]
        
        return jsonify({
            'uploads': paginated_uploads,
            'total': len(uploads),
            'current_page': page,
            'per_page': per_page,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500 