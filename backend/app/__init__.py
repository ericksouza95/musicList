import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar extensões
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Configuração do banco de dados
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///todo_app.db')
    
    # Ajustar URL do PostgreSQL se necessário
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_SIZE', 16777216))  # 16MB
    
    # Configurar diretório de uploads
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, '..', 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configurar CORS
    cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # Importar modelos (para migrations)
    from app.models import user, music, playlist, task_list, task
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.music import music_bp
    from app.routes.playlists import playlists_bp
    from app.routes.task_lists import task_lists_bp
    from app.routes.tasks import tasks_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(music_bp, url_prefix='/api/music')
    app.register_blueprint(playlists_bp, url_prefix='/api/playlists')
    app.register_blueprint(task_lists_bp, url_prefix='/api/task-lists')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    
    # Rota raiz
    @app.route('/')
    def index_root():
        return {
            'name': 'TO-DO List API',
            'version': '1.0.0',
            'description': 'API para gerenciamento de listas de tarefas',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'info': '/api',
                'auth': '/api/auth',
                'users': '/api/users',
                'task_lists': '/api/task-lists',
                'tasks': '/api/tasks',
                'music': '/api/music',  # Manter para compatibilidade
                'playlists': '/api/playlists'  # Manter para compatibilidade
            }
        }
    
    # Rotas de saúde e informações
    @app.route('/api/health')
    def health():
        try:
            # Testar conexão com o banco
            with app.app_context():
                db.session.execute('SELECT 1')
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return {
            'status': 'healthy', 
            'message': 'TO-DO List API is running',
            'database': db_status
        }
    
    @app.route('/api')
    def index():
        return {
            'name': 'TO-DO List API',
            'version': '1.0.0',
            'description': 'API para gerenciamento de listas de tarefas',
            'database': 'PostgreSQL' if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite',
            'features': [
                'Autenticação JWT',
                'CRUD de usuários',
                'CRUD de listas de tarefas',
                'CRUD de tarefas',
                'Dashboard com estatísticas',
                'Operações em lote'
            ]
        }
    
    return app 