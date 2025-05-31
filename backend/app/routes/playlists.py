from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.music import Music
from app.models.playlist import Playlist

playlists_bp = Blueprint('playlists', __name__)


@playlists_bp.route('/', methods=['GET'])
@jwt_required()
def get_playlists():
    """Lista playlists com filtros e paginação"""
    try:
        current_user_id = get_jwt_identity()
        
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '')
        owner_id = request.args.get('owner_id', type=int)
        is_public = request.args.get('is_public', type=bool)
        
        # Query base - playlists públicas ou do usuário atual
        query = Playlist.query.filter(
            (Playlist.is_public == True) | (Playlist.owner_id == current_user_id)
        )
        
        # Filtros
        if search:
            query = query.filter(
                (Playlist.name.ilike(f'%{search}%')) |
                (Playlist.description.ilike(f'%{search}%'))
            )
        
        if owner_id:
            query = query.filter(Playlist.owner_id == owner_id)
        
        if is_public is not None:
            query = query.filter(Playlist.is_public == is_public)
        
        # Paginação
        playlists = query.order_by(Playlist.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'playlists': [playlist.to_dict() for playlist in playlists.items],
            'total': playlists.total,
            'pages': playlists.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': playlists.has_next,
            'has_prev': playlists.has_prev
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/', methods=['POST'])
@jwt_required()
def create_playlist():
    """Cria uma nova playlist"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validações
        if not data.get('name'):
            return jsonify({'error': 'Nome da playlist é obrigatório'}), 400
        
        # Criar playlist
        playlist = Playlist(
            name=data['name'],
            description=data.get('description'),
            cover_image_url=data.get('cover_image_url'),
            is_public=data.get('is_public', True),
            is_collaborative=data.get('is_collaborative', False),
            owner_id=current_user_id
        )
        
        db.session.add(playlist)
        db.session.commit()
        
        return jsonify({
            'message': 'Playlist criada com sucesso',
            'playlist': playlist.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/<int:playlist_id>', methods=['GET'])
@jwt_required()
def get_playlist(playlist_id):
    """Obtém uma playlist específica"""
    try:
        current_user_id = get_jwt_identity()
        
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist não encontrada'}), 404
        
        # Verificar permissões
        if not playlist.is_public and playlist.owner_id != current_user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        include_tracks = request.args.get('include_tracks', 'false').lower() == 'true'
        
        return jsonify({
            'playlist': playlist.to_dict(include_tracks=include_tracks)
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/<int:playlist_id>', methods=['PUT'])
@jwt_required()
def update_playlist(playlist_id):
    """Atualiza uma playlist"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist não encontrada'}), 404
        
        # Verificar permissões (dono ou colaborativo)
        if (playlist.owner_id != current_user_id and 
            not playlist.is_collaborative and 
            not current_user.is_admin):
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        # Campos que podem ser atualizados (apenas pelo dono ou admin)
        if playlist.owner_id == current_user_id or current_user.is_admin:
            if 'name' in data:
                playlist.name = data['name']
            
            if 'description' in data:
                playlist.description = data['description']
            
            if 'cover_image_url' in data:
                playlist.cover_image_url = data['cover_image_url']
            
            if 'is_public' in data:
                playlist.is_public = bool(data['is_public'])
            
            if 'is_collaborative' in data:
                playlist.is_collaborative = bool(data['is_collaborative'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Playlist atualizada com sucesso',
            'playlist': playlist.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/<int:playlist_id>', methods=['DELETE'])
@jwt_required()
def delete_playlist(playlist_id):
    """Deleta uma playlist"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist não encontrada'}), 404
        
        # Verificar permissões (dono ou admin)
        if playlist.owner_id != current_user_id and not current_user.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        db.session.delete(playlist)
        db.session.commit()
        
        return jsonify({'message': 'Playlist deletada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/<int:playlist_id>/tracks', methods=['GET'])
@jwt_required()
def get_playlist_tracks(playlist_id):
    """Obtém as músicas de uma playlist"""
    try:
        current_user_id = get_jwt_identity()
        
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist não encontrada'}), 404
        
        # Verificar permissões
        if not playlist.is_public and playlist.owner_id != current_user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        # Simular paginação das músicas
        tracks = [music.to_dict() for music in playlist.music_tracks]
        start = (page - 1) * per_page
        end = start + per_page
        paginated_tracks = tracks[start:end]
        
        return jsonify({
            'tracks': paginated_tracks,
            'total': len(tracks),
            'current_page': page,
            'per_page': per_page,
            'playlist': playlist.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/<int:playlist_id>/tracks', methods=['POST'])
@jwt_required()
def add_track_to_playlist(playlist_id):
    """Adiciona uma música à playlist"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist não encontrada'}), 404
        
        # Verificar permissões (dono ou colaborativo)
        if (playlist.owner_id != current_user_id and 
            not playlist.is_collaborative):
            return jsonify({'error': 'Acesso negado'}), 403
        
        music_id = data.get('music_id')
        if not music_id:
            return jsonify({'error': 'music_id é obrigatório'}), 400
        
        music = Music.query.get(music_id)
        if not music:
            return jsonify({'error': 'Música não encontrada'}), 404
        
        # Verificar se a música é acessível ao usuário
        if not music.is_public and music.uploaded_by_id != current_user_id:
            return jsonify({'error': 'Música não acessível'}), 403
        
        # Adicionar música à playlist
        position = data.get('position')
        success = playlist.add_music(music, position)
        
        if not success:
            return jsonify({'error': 'Música já está na playlist'}), 409
        
        return jsonify({
            'message': 'Música adicionada à playlist',
            'playlist': playlist.to_dict(),
            'music': music.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/<int:playlist_id>/tracks/<int:music_id>', methods=['DELETE'])
@jwt_required()
def remove_track_from_playlist(playlist_id, music_id):
    """Remove uma música da playlist"""
    try:
        current_user_id = get_jwt_identity()
        
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist não encontrada'}), 404
        
        # Verificar permissões (dono ou colaborativo)
        if (playlist.owner_id != current_user_id and 
            not playlist.is_collaborative):
            return jsonify({'error': 'Acesso negado'}), 403
        
        music = Music.query.get(music_id)
        if not music:
            return jsonify({'error': 'Música não encontrada'}), 404
        
        # Remover música da playlist
        success = playlist.remove_music(music)
        
        if not success:
            return jsonify({'error': 'Música não está na playlist'}), 404
        
        return jsonify({
            'message': 'Música removida da playlist',
            'playlist': playlist.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/<int:playlist_id>/tracks/reorder', methods=['POST'])
@jwt_required()
def reorder_playlist_tracks(playlist_id):
    """Reordena as músicas da playlist"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist não encontrada'}), 404
        
        # Verificar permissões (dono ou colaborativo)
        if (playlist.owner_id != current_user_id and 
            not playlist.is_collaborative):
            return jsonify({'error': 'Acesso negado'}), 403
        
        music_id = data.get('music_id')
        new_position = data.get('new_position')
        
        if not music_id or new_position is None:
            return jsonify({'error': 'music_id e new_position são obrigatórios'}), 400
        
        # Reordenar música
        playlist.reorder_music(music_id, new_position)
        
        return jsonify({
            'message': 'Música reordenada com sucesso',
            'playlist': playlist.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/<int:playlist_id>/play', methods=['POST'])
@jwt_required()
def increment_playlist_play_count(playlist_id):
    """Incrementa contador de reproduções da playlist"""
    try:
        current_user_id = get_jwt_identity()
        
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist não encontrada'}), 404
        
        # Verificar permissões
        if not playlist.is_public and playlist.owner_id != current_user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        playlist.increment_play_count()
        
        return jsonify({
            'message': 'Reprodução de playlist registrada',
            'play_count': playlist.play_count
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/<int:playlist_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_playlist(playlist_id):
    """Duplica uma playlist"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        original_playlist = Playlist.query.get(playlist_id)
        if not original_playlist:
            return jsonify({'error': 'Playlist não encontrada'}), 404
        
        # Verificar permissões para acessar a playlist original
        if not original_playlist.is_public and original_playlist.owner_id != current_user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Criar nova playlist
        new_name = data.get('name', f"{original_playlist.name} - Cópia")
        new_playlist = Playlist(
            name=new_name,
            description=data.get('description', original_playlist.description),
            cover_image_url=data.get('cover_image_url', original_playlist.cover_image_url),
            is_public=data.get('is_public', True),
            is_collaborative=data.get('is_collaborative', False),
            owner_id=current_user_id
        )
        
        db.session.add(new_playlist)
        db.session.flush()  # Para obter o ID
        
        # Copiar músicas
        for music in original_playlist.music_tracks:
            # Verificar se usuário tem acesso à música
            if music.is_public or music.uploaded_by_id == current_user_id:
                new_playlist.add_music(music)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Playlist duplicada com sucesso',
            'playlist': new_playlist.to_dict(include_tracks=True),
            'original_playlist': original_playlist.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@playlists_bp.route('/<int:playlist_id>/refresh-duration', methods=['POST'])
@jwt_required()
def refresh_playlist_duration(playlist_id):
    """Recalcula a duração total da playlist"""
    try:
        current_user_id = get_jwt_identity()
        
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'error': 'Playlist não encontrada'}), 404
        
        # Verificar permissões (dono)
        if playlist.owner_id != current_user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Recalcular duração
        total_duration = playlist.calculate_total_duration()
        
        return jsonify({
            'message': 'Duração da playlist recalculada',
            'total_duration': total_duration,
            'total_duration_formatted': playlist.total_duration_formatted
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500 