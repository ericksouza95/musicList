from datetime import datetime
from app import db


class Task(db.Model):
    """Modelo para tarefas individuais"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Foreign Keys
    task_list_id = db.Column(db.Integer, db.ForeignKey('task_lists.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'task_list_id': self.task_list_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'task_list_title': self.task_list.title if self.task_list else None,
            'is_overdue': self.is_overdue(),
            'days_until_due': self.days_until_due()
        }
    
    def toggle_completion(self):
        """Alterna o status de conclusão da tarefa"""
        self.completed = not self.completed
        self.completed_at = datetime.utcnow() if self.completed else None
        self.updated_at = datetime.utcnow()
    
    def is_overdue(self):
        """Verifica se a tarefa está atrasada"""
        if not self.due_date or self.completed:
            return False
        return datetime.utcnow() > self.due_date
    
    def days_until_due(self):
        """Calcula quantos dias faltam para o vencimento"""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.utcnow()
        return delta.days
    
    @staticmethod
    def get_priority_color(priority):
        """Retorna a cor associada à prioridade"""
        colors = {
            'low': '#4caf50',      # Verde
            'medium': '#ff9800',   # Laranja  
            'high': '#f44336',     # Vermelho
            'urgent': '#9c27b0'    # Roxo
        }
        return colors.get(priority, '#9e9e9e')
    
    @staticmethod
    def get_priorities():
        """Retorna as prioridades disponíveis"""
        return [
            {'value': 'low', 'label': 'Baixa', 'color': '#4caf50'},
            {'value': 'medium', 'label': 'Média', 'color': '#ff9800'},
            {'value': 'high', 'label': 'Alta', 'color': '#f44336'},
            {'value': 'urgent', 'label': 'Urgente', 'color': '#9c27b0'}
        ] 