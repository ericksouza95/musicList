from datetime import datetime
from app import db


# Tabela de associação para many-to-many entre Playlist e Music
playlist_music = db.Table('playlist_music',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlists.id'), primary_key=True),
    db.Column('music_id', db.Integer, db.ForeignKey('music.id'), primary_key=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow, nullable=False),
    db.Column('position', db.Integer, nullable=True)  # Para ordenação na playlist
)


class Music(db.Model):
    """Modelo para músicas do sistema"""
    __tablename__ = 'music'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    artist = db.Column(db.String(200), nullable=False, index=True)
    album = db.Column(db.String(200), nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # duração em segundos
    track_number = db.Column(db.Integer, nullable=True)
    
    # Informações do arquivo
    file_path = db.Column(db.String(500), nullable=True)  # para músicas locais
    file_size = db.Column(db.Integer, nullable=True)  # tamanho em bytes
    file_format = db.Column(db.String(10), nullable=True)  # mp3, wav, flac, etc.
    
    # Informações externas (APIs)
    spotify_id = db.Column(db.String(100), nullable=True, unique=True)
    external_url = db.Column(db.String(500), nullable=True)
    preview_url = db.Column(db.String(500), nullable=True)
    cover_image_url = db.Column(db.String(500), nullable=True)
    
    # Metadados
    is_local = db.Column(db.Boolean, default=False, nullable=False)  # se foi feito upload
    is_public = db.Column(db.Boolean, default=True, nullable=False)  # visível para outros usuários
    play_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Relacionamentos
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento many-to-many com playlists
    playlists = db.relationship('Playlist', secondary=playlist_music, back_populates='music_tracks')
    
    def increment_play_count(self):
        """Incrementa o contador de reproduções"""
        self.play_count += 1
        db.session.commit()
    
    @property
    def duration_formatted(self):
        """Retorna a duração formatada em MM:SS"""
        if not self.duration:
            return "00:00"
        
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def file_size_formatted(self):
        """Retorna o tamanho do arquivo formatado"""
        if not self.file_size:
            return "0 KB"
        
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    def to_dict(self, include_file_info=False):
        """Converte a música para dicionário"""
        data = {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'genre': self.genre,
            'year': self.year,
            'duration': self.duration,
            'duration_formatted': self.duration_formatted,
            'track_number': self.track_number,
            'spotify_id': self.spotify_id,
            'external_url': self.external_url,
            'preview_url': self.preview_url,
            'cover_image_url': self.cover_image_url,
            'is_local': self.is_local,
            'is_public': self.is_public,
            'play_count': self.play_count,
            'uploaded_by_id': self.uploaded_by_id,
            'uploader': self.uploader.username if self.uploader else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'playlists_count': len(self.playlists)
        }
        
        if include_file_info:
            data.update({
                'file_path': self.file_path,
                'file_size': self.file_size,
                'file_size_formatted': self.file_size_formatted,
                'file_format': self.file_format
            })
            
        return data
    
    def __repr__(self):
        return f'<Music {self.title} by {self.artist}>' 