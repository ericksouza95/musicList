from datetime import datetime
from app import db


class TaskList(db.Model):
    """Modelo para listas de tarefas"""
    __tablename__ = 'task_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#1976d2')  # Cor em hex
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('task_lists', lazy=True, cascade='all, delete-orphan'))
    tasks = db.relationship('Task', backref='task_list', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TaskList {self.title}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'color': self.color,
            'user_id': self.user_id,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'task_count': len(self.tasks),
            'completed_count': len([t for t in self.tasks if t.completed]),
            'pending_count': len([t for t in self.tasks if not t.completed])
        }
    
    @staticmethod
    def create_default_list(user_id):
        """Cria uma lista padrão para novo usuário"""
        default_list = TaskList(
            title='Minhas Tarefas',
            description='Lista padrão de tarefas',
            color='#1976d2',
            user_id=user_id
        )
        db.session.add(default_list)
        db.session.commit()
        return default_list 