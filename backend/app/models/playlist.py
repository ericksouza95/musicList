from datetime import datetime
from app import db
from .music import playlist_music


class Playlist(db.Model):
    """Modelo para playlists de músicas"""
    __tablename__ = 'playlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    cover_image_url = db.Column(db.String(500), nullable=True)
    
    # Visibilidade e permissões
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    is_collaborative = db.Column(db.Boolean, default=False, nullable=False)
    
    # Metadados
    total_duration = db.Column(db.Integer, default=0, nullable=False)  # em segundos
    play_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Relacionamentos
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento many-to-many com músicas
    music_tracks = db.relationship('Music', secondary=playlist_music, back_populates='playlists', 
                                 order_by='playlist_music.c.position')
    
    def add_music(self, music, position=None):
        """Adiciona uma música à playlist"""
        if music not in self.music_tracks:
            if position is None:
                position = len(self.music_tracks) + 1
            
            # Inserir na tabela de associação com posição
            stmt = playlist_music.insert().values(
                playlist_id=self.id,
                music_id=music.id,
                position=position,
                added_at=datetime.utcnow()
            )
            db.session.execute(stmt)
            
            # Atualizar duração total
            if music.duration:
                self.total_duration += music.duration
            
            db.session.commit()
            return True
        return False
    
    def remove_music(self, music):
        """Remove uma música da playlist"""
        if music in self.music_tracks:
            # Remover da tabela de associação
            stmt = playlist_music.delete().where(
                playlist_music.c.playlist_id == self.id,
                playlist_music.c.music_id == music.id
            )
            db.session.execute(stmt)
            
            # Atualizar duração total
            if music.duration:
                self.total_duration -= music.duration
                if self.total_duration < 0:
                    self.total_duration = 0
            
            db.session.commit()
            return True
        return False
    
    def reorder_music(self, music_id, new_position):
        """Reordena uma música na playlist"""
        # Implementar lógica de reordenação
        # Por simplicidade, vamos apenas atualizar a posição
        stmt = playlist_music.update().where(
            playlist_music.c.playlist_id == self.id,
            playlist_music.c.music_id == music_id
        ).values(position=new_position)
        
        db.session.execute(stmt)
        db.session.commit()
    
    def increment_play_count(self):
        """Incrementa o contador de reproduções da playlist"""
        self.play_count += 1
        db.session.commit()
    
    def calculate_total_duration(self):
        """Recalcula a duração total da playlist"""
        total = 0
        for music in self.music_tracks:
            if music.duration:
                total += music.duration
        
        self.total_duration = total
        db.session.commit()
        return total
    
    @property
    def total_duration_formatted(self):
        """Retorna a duração total formatada em HH:MM:SS"""
        if not self.total_duration:
            return "00:00"
        
        hours = self.total_duration // 3600
        minutes = (self.total_duration % 3600) // 60
        seconds = self.total_duration % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def tracks_count(self):
        """Retorna o número de músicas na playlist"""
        return len(self.music_tracks)
    
    def to_dict(self, include_tracks=False):
        """Converte a playlist para dicionário"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cover_image_url': self.cover_image_url,
            'is_public': self.is_public,
            'is_collaborative': self.is_collaborative,
            'total_duration': self.total_duration,
            'total_duration_formatted': self.total_duration_formatted,
            'play_count': self.play_count,
            'tracks_count': self.tracks_count,
            'owner_id': self.owner_id,
            'owner': self.owner.username if self.owner else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_tracks:
            data['tracks'] = [music.to_dict() for music in self.music_tracks]
            
        return data
    
    def __repr__(self):
        return f'<Playlist {self.name} by {self.owner.username if self.owner else "Unknown"}>' 