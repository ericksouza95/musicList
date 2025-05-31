import os
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from mutagen import File as MutagenFile
from app import db
from app.models.user import User
from app.models.music import Music
from app.services.spotify_service import spotify_service

music_bp = Blueprint('music', __name__)

# Extensões permitidas para upload
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'aac', 'ogg'}


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_metadata(file_path):
    """Extrai metadados de um arquivo de música usando mutagen"""
    try:
        audio_file = MutagenFile(file_path)
        if audio_file is None:
            return {}
        
        metadata = {
            'title': None,
            'artist': None,
            'album': None,
            'genre': None,
            'year': None,
            'duration': None,
            'track_number': None
        }
        
        # Mapeamento de tags comuns
        tag_mappings = {
            'TIT2': 'title',  # MP3
            'TPE1': 'artist',  # MP3
            'TALB': 'album',   # MP3
            'TCON': 'genre',   # MP3
            'TDRC': 'year',    # MP3
            'TRCK': 'track_number',  # MP3
            'TITLE': 'title',  # FLAC, OGG
            'ARTIST': 'artist',  # FLAC, OGG
            'ALBUM': 'album',   # FLAC, OGG
            'GENRE': 'genre',   # FLAC, OGG
            'DATE': 'year',     # FLAC, OGG
            'TRACKNUMBER': 'track_number'  # FLAC, OGG
        }
        
        # Extrair informações básicas
        if hasattr(audio_file, 'info'):
            metadata['duration'] = int(audio_file.info.length) if audio_file.info.length else None
        
        # Extrair tags
        for tag, value in audio_file.items():
            if isinstance(value, list) and value:
                value = value[0]
            
            if tag in tag_mappings:
                field = tag_mappings[tag]
                if field == 'year' and value:
                    try:
                        metadata['year'] = int(str(value)[:4])
                    except:
                        pass
                elif field == 'track_number' and value:
                    try:
                        # Track pode vir como "1/12", pegar só o primeiro número
                        metadata['track_number'] = int(str(value).split('/')[0])
                    except:
                        pass
                else:
                    metadata[field] = str(value) if value else None
        
        return metadata
        
    except Exception as e:
        print(f"❌ Erro ao extrair metadados: {str(e)}")
        return {}


@music_bp.route('/search', methods=['GET'])
@jwt_required()
def search_music():
    """Busca músicas no Spotify"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Parâmetro de busca é obrigatório'}), 400
        
        limit = min(request.args.get('limit', 20, type=int), 50)
        offset = request.args.get('offset', 0, type=int)
        
        # Buscar no Spotify
        results = spotify_service.search_tracks(query, limit, offset)
        
        return jsonify({
            'results': results,
            'total': len(results),
            'query': query,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@music_bp.route('/import', methods=['POST'])
@jwt_required()
def import_from_spotify():
    """Importa uma música do Spotify para o banco local"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        spotify_id = data.get('spotify_id')
        if not spotify_id:
            return jsonify({'error': 'spotify_id é obrigatório'}), 400
        
        # Verificar se música já existe
        existing_music = Music.query.filter_by(spotify_id=spotify_id).first()
        if existing_music:
            return jsonify({
                'message': 'Música já existe no banco',
                'music': existing_music.to_dict()
            })
        
        # Buscar informações no Spotify
        track_data = spotify_service.get_track(spotify_id)
        if not track_data:
            return jsonify({'error': 'Música não encontrada no Spotify'}), 404
        
        # Criar entrada no banco
        music = Music(
            title=track_data['title'],
            artist=track_data['artist'],
            album=track_data['album'],
            genre=track_data['genre'],
            year=track_data['year'],
            duration=track_data['duration'],
            track_number=track_data['track_number'],
            spotify_id=track_data['spotify_id'],
            external_url=track_data['external_url'],
            preview_url=track_data['preview_url'],
            cover_image_url=track_data['cover_image_url'],
            is_local=False,
            is_public=True
        )
        
        db.session.add(music)
        db.session.commit()
        
        return jsonify({
            'message': 'Música importada com sucesso',
            'music': music.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@music_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_music():
    """Faz upload de um arquivo de música"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        # Adicionar timestamp para evitar conflitos
        import time
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extrair metadados
        metadata = extract_metadata(file_path)
        
        # Obter dados do formulário (opcionais, sobrescrevem metadados)
        form_data = request.form.to_dict()
        
        # Criar entrada no banco
        music = Music(
            title=form_data.get('title') or metadata.get('title') or name,
            artist=form_data.get('artist') or metadata.get('artist') or 'Artista Desconhecido',
            album=form_data.get('album') or metadata.get('album'),
            genre=form_data.get('genre') or metadata.get('genre'),
            year=int(form_data['year']) if form_data.get('year') else metadata.get('year'),
            duration=metadata.get('duration'),
            track_number=int(form_data['track_number']) if form_data.get('track_number') else metadata.get('track_number'),
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            file_format=ext[1:].lower() if ext else None,
            is_local=True,
            is_public=form_data.get('is_public', 'true').lower() == 'true',
            uploaded_by_id=current_user_id
        )
        
        db.session.add(music)
        db.session.commit()
        
        return jsonify({
            'message': 'Música enviada com sucesso',
            'music': music.to_dict(include_file_info=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Tentar remover arquivo se erro no banco
        try:
            if 'file_path' in locals():
                os.remove(file_path)
        except:
            pass
        return jsonify({'error': 'Erro interno do servidor'}), 500


@music_bp.route('/', methods=['GET'])
@jwt_required()
def get_music_list():
    """Lista músicas com filtros e paginação"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Parâmetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '')
        genre = request.args.get('genre', '')
        year = request.args.get('year', type=int)
        is_local = request.args.get('is_local', type=bool)
        uploader_id = request.args.get('uploader_id', type=int)
        
        # Query base - músicas públicas ou do usuário atual
        query = Music.query.filter(
            (Music.is_public == True) | (Music.uploaded_by_id == current_user_id)
        )
        
        # Filtros
        if search:
            query = query.filter(
                (Music.title.ilike(f'%{search}%')) |
                (Music.artist.ilike(f'%{search}%')) |
                (Music.album.ilike(f'%{search}%'))
            )
        
        if genre:
            query = query.filter(Music.genre.ilike(f'%{genre}%'))
        
        if year:
            query = query.filter(Music.year == year)
        
        if is_local is not None:
            query = query.filter(Music.is_local == is_local)
        
        if uploader_id:
            query = query.filter(Music.uploaded_by_id == uploader_id)
        
        # Paginação
        music_list = query.order_by(Music.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'music': [music.to_dict() for music in music_list.items],
            'total': music_list.total,
            'pages': music_list.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': music_list.has_next,
            'has_prev': music_list.has_prev
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@music_bp.route('/<int:music_id>', methods=['GET'])
@jwt_required()
def get_music(music_id):
    """Obtém uma música específica"""
    try:
        current_user_id = get_jwt_identity()
        
        music = Music.query.get(music_id)
        if not music:
            return jsonify({'error': 'Música não encontrada'}), 404
        
        # Verificar permissões
        if not music.is_public and music.uploaded_by_id != current_user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        return jsonify({'music': music.to_dict(include_file_info=True)})
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@music_bp.route('/<int:music_id>', methods=['PUT'])
@jwt_required()
def update_music(music_id):
    """Atualiza informações de uma música"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        music = Music.query.get(music_id)
        if not music:
            return jsonify({'error': 'Música não encontrada'}), 404
        
        # Verificar permissões (dono ou admin)
        if music.uploaded_by_id != current_user_id and not current_user.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        # Campos que podem ser atualizados
        if 'title' in data:
            music.title = data['title']
        
        if 'artist' in data:
            music.artist = data['artist']
        
        if 'album' in data:
            music.album = data['album']
        
        if 'genre' in data:
            music.genre = data['genre']
        
        if 'year' in data:
            music.year = int(data['year']) if data['year'] else None
        
        if 'track_number' in data:
            music.track_number = int(data['track_number']) if data['track_number'] else None
        
        if 'is_public' in data:
            music.is_public = bool(data['is_public'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Música atualizada com sucesso',
            'music': music.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@music_bp.route('/<int:music_id>', methods=['DELETE'])
@jwt_required()
def delete_music(music_id):
    """Deleta uma música"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        music = Music.query.get(music_id)
        if not music:
            return jsonify({'error': 'Música não encontrada'}), 404
        
        # Verificar permissões (dono ou admin)
        if music.uploaded_by_id != current_user_id and not current_user.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Remover arquivo local se existir
        if music.is_local and music.file_path and os.path.exists(music.file_path):
            try:
                os.remove(music.file_path)
            except Exception as e:
                print(f"⚠️  Erro ao remover arquivo: {str(e)}")
        
        db.session.delete(music)
        db.session.commit()
        
        return jsonify({'message': 'Música deletada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500


@music_bp.route('/<int:music_id>/stream', methods=['GET'])
@jwt_required()
def stream_music(music_id):
    """Faz streaming de uma música local"""
    try:
        current_user_id = get_jwt_identity()
        
        music = Music.query.get(music_id)
        if not music:
            return jsonify({'error': 'Música não encontrada'}), 404
        
        # Verificar permissões
        if not music.is_public and music.uploaded_by_id != current_user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Verificar se é música local
        if not music.is_local or not music.file_path:
            return jsonify({'error': 'Música não disponível para streaming'}), 400
        
        # Verificar se arquivo existe
        if not os.path.exists(music.file_path):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Incrementar contador de reproduções
        music.increment_play_count()
        
        # Enviar arquivo
        return send_file(
            music.file_path,
            as_attachment=False,
            mimetype=f'audio/{music.file_format}'
        )
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@music_bp.route('/<int:music_id>/play', methods=['POST'])
@jwt_required()
def increment_play_count(music_id):
    """Incrementa contador de reproduções"""
    try:
        current_user_id = get_jwt_identity()
        
        music = Music.query.get(music_id)
        if not music:
            return jsonify({'error': 'Música não encontrada'}), 404
        
        # Verificar permissões
        if not music.is_public and music.uploaded_by_id != current_user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        music.increment_play_count()
        
        return jsonify({
            'message': 'Reprodução registrada',
            'play_count': music.play_count
        })
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500 