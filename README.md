# Sistema de Lista de Músicas

Uma aplicação web moderna para gerenciamento de listas de músicas pessoais, desenvolvida com Flask (backend) e Vue.js + Vuetify (frontend).

## Funcionalidades

- 🎵 **Gerenciamento de Músicas**: Adicione, edite e remova músicas
- 📝 **Listas Personalizadas**: Crie e organize suas próprias playlists
- 👤 **Autenticação de Usuários**: Sistema completo de login/registro
- 🔍 **Busca de Músicas**: Integração com APIs de música para descoberta
- 📱 **Interface Responsiva**: Design moderno com Material Design (Vuetify)
- 🎧 **Upload de Músicas**: Faça upload de suas próprias músicas
- 🗄️ **Banco PostgreSQL**: Sistema robusto com PostgreSQL

## 🚀 Início Rápido

### Opção 1: Instalação Automática (Recomendado)

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd projeto-flask

# 2. Execute o setup automático
python setup_project.py

# 3. Inicie o sistema
python start_app.py
```

### Opção 2: Duplo clique (Windows)

1. Baixe o projeto
2. Duplo clique em `start.bat`
3. Siga as instruções na tela

### Opção 3: Configuração Manual

Siga as instruções detalhadas abaixo.

## Estrutura do Projeto

```
projeto-flask/
├── backend/                 # API Flask
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/         # Modelos do banco de dados
│   │   ├── routes/         # Rotas da API
│   │   ├── services/       # Lógica de negócio
│   │   └── utils/          # Utilitários
│   ├── migrations/         # Migrações do banco
│   ├── requirements.txt
│   ├── setup_database.py   # Script para configurar PostgreSQL
│   └── run.py
├── frontend/               # Vue.js + Vuetify
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── services/
│   │   └── router/
│   ├── package.json
│   └── vue.config.js
├── start_app.py           # 🚀 Launcher automático
├── setup_project.py       # 🔧 Setup inicial
├── start.bat              # 🪟 Launcher Windows
├── .gitignore
└── README.md
```

## Pré-requisitos

- **Python 3.8+**
- **Node.js 16+**
- **PostgreSQL 12+** (opcional, usa SQLite por padrão)
- **npm ou yarn**

## Scripts de Automação

### `start_app.py` - Launcher Principal
Inicia frontend e backend automaticamente:
```bash
python start_app.py
```
**Funcionalidades:**
- ✅ Inicia Flask (backend) em background
- ✅ Inicia Vue.js (frontend) 
- ✅ Abre navegador automaticamente
- ✅ Monitora processos
- ✅ Para tudo com Ctrl+C

### `setup_project.py` - Configuração Inicial
Instala todas as dependências automaticamente:
```bash
python setup_project.py
```
**Funcionalidades:**
- ✅ Verifica Python e Node.js
- ✅ Cria ambiente virtual
- ✅ Instala dependências Python e Node.js
- ✅ Configura banco de dados
- ✅ Executa migrações

### `start.bat` - Launcher Windows
Para usuários Windows (duplo clique):
- ✅ Interface simples
- ✅ Verifica dependências
- ✅ Inicia sistema completo

## Configuração Manual (Avançado)

### 1. PostgreSQL (Opcional - Recomendado para Produção)

#### Instalação Automática
```powershell
# Execute como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\backend\install_postgresql.ps1
```

#### Instalação Manual
1. Baixe PostgreSQL: https://www.postgresql.org/download/windows/
2. Execute o instalador
3. Configure senha do usuário `postgres`
4. Use configurações padrão (porta 5432)

#### Configuração do Banco
```bash
cd backend
python setup_database.py
```

### 2. Backend (Flask)

```bash
cd backend

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
copy env.example .env  # Windows
cp env.example .env    # Linux/Mac

# Executar migrações
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Iniciar servidor
python run.py
```

### 3. Frontend (Vue.js)

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run serve
```

## Desenvolvimento com SQLite (Padrão)

O sistema usa SQLite por padrão. Para usar PostgreSQL:

1. Instale PostgreSQL
2. Configure o arquivo `.env`:
   ```env
   # DATABASE_URL=sqlite:///music_app.db
   DATABASE_URL=postgresql://music_user:music_password@localhost:5432/music_app_db
   ```
3. Execute: `python setup_database.py`

## Scripts Úteis

### Geral
```bash
# Setup completo
python setup_project.py

# Iniciar sistema
python start_app.py

# Windows (duplo clique)
start.bat
```

### Backend
```bash
# Testar conexão com banco
python setup_database.py test

# Criar migração
flask db migrate -m "Descrição"

# Aplicar migrações
flask db upgrade

# Reverter migração
flask db downgrade
```

### Frontend
```bash
# Servidor de desenvolvimento
npm run serve

# Build para produção
npm run build

# Linting
npm run lint
```

## URLs da Aplicação

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health
- **API Info**: http://localhost:5000/api

## Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **PostgreSQL**: Banco de dados principal (SQLite para desenvolvimento)
- **Flask-JWT-Extended**: Autenticação JWT
- **Flask-CORS**: Suporte a CORS
- **Flask-Migrate**: Migrações de banco
- **Psycopg2**: Driver PostgreSQL
- **Werkzeug**: Upload de arquivos

### Frontend
- **Vue.js 3**: Framework JavaScript reativo
- **Vuetify 3**: Framework de UI Material Design
- **Vue Router**: Roteamento SPA
- **Axios**: Cliente HTTP
- **Pinia**: Gerenciamento de estado

### APIs Externas
- **Spotify Web API**: Busca e informações de músicas
- **LastFM API**: Dados adicionais de músicas e artistas

## Migração para PostgreSQL

Para migrar do SQLite para PostgreSQL, consulte: [`backend/migrate_to_postgresql.md`](backend/migrate_to_postgresql.md)

## Solução de Problemas

### Problemas Comuns

1. **"Python não encontrado"**
   ```bash
   # Instale Python 3.8+
   # Windows: https://python.org
   # Linux: sudo apt install python3
   # Mac: brew install python3
   ```

2. **"Node.js não encontrado"**
   ```bash
   # Instale Node.js 16+
   # https://nodejs.org/
   ```

3. **"Erro ao instalar dependências"**
   ```bash
   # Backend
   cd backend
   pip install --upgrade pip
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm cache clean --force
   npm install
   ```

4. **"Erro de conexão com banco"**
   ```bash
   # Verificar se PostgreSQL está rodando
   net start postgresql-x64-15  # Windows
   sudo systemctl start postgresql  # Linux
   
   # Testar conexão
   python backend/setup_database.py test
   ```

### Logs e Debug

```bash
# Ver logs do Flask
python backend/run.py

# Ver logs do Vue.js
cd frontend && npm run serve

# Verificar saúde do sistema
curl http://localhost:5000/api/health
```

## Desenvolvimento

### Estrutura de Desenvolvimento
```bash
# Terminal 1: Backend
cd backend
.venv\Scripts\activate
python run.py

# Terminal 2: Frontend  
cd frontend
npm run serve

# Ou use o launcher automático:
python start_app.py
```

### Hot Reload
- ✅ **Backend**: Reinicia automaticamente com mudanças
- ✅ **Frontend**: Hot reload automático
- ✅ **Banco**: Migrações automáticas detectadas



## Licença

Este projeto está licenciado sob a MIT License. Veja o arquivo [LICENSE](LICENSE) para detalhes. 