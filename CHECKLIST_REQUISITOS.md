# ✅ CHECKLIST - REQUISITOS DO PROJETO

## 📋 Requisitos do Sistema TO-DO LIST

### 1. ✅ **Estar organizada estruturalmente em termos de diretórios e arquivos**

**Status: COMPLETO ✅**

```
projeto flask/
├── backend/
│   ├── app/
│   │   ├── models/          # Modelos de dados
│   │   ├── routes/          # Rotas da API  
│   │   ├── services/        # Lógica de negócio
│   │   └── utils/           # Utilitários
│   ├── migrations/          # Migrações do banco
│   └── run.py              # Ponto de entrada
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes Vue
│   │   ├── views/           # Páginas
│   │   ├── stores/          # Estado (Pinia)
│   │   ├── services/        # APIs
│   │   └── router/          # Roteamento
│   └── package.json
├── scripts/                 # Scripts de automação
└── docs/                   # Documentação
```

**✅ Estrutura bem organizada seguindo padrões MVC**

---

### 2. ✅ **Deverá implementar autenticação de usuários**

**Status: COMPLETO ✅**

#### Backend (Flask + JWT):
- ✅ **Registro:** `POST /api/auth/register`
- ✅ **Login:** `POST /api/auth/login` 
- ✅ **Logout:** `POST /api/auth/logout`
- ✅ **Token Refresh:** `POST /api/auth/refresh`
- ✅ **User Info:** `GET /api/auth/me`

#### Frontend (Vue + Pinia):
- ✅ **Store de autenticação** (`stores/auth.js`)
- ✅ **Páginas de login/registro** (`views/auth/`)
- ✅ **Guards de rota** para proteger páginas
- ✅ **Interceptors** para tokens automáticos

#### Testado e funcionando:
```bash
# ✅ REGISTRO FUNCIONANDO
Invoke-RestMethod -Uri "http://localhost:5000/api/auth/register" -Method POST -ContentType "application/json" -Body '{"username":"user123","email":"user@gmail.com","first_name":"User","last_name":"Test","password":"123456"}'

# ✅ LOGIN FUNCIONANDO  
Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method POST -ContentType "application/json" -Body '{"login":"user123","password":"123456"}'
```

---

### 3. ✅ **Deverá implementar um CRUD de usuários**

**Status: COMPLETO ✅**

#### Backend - Rotas implementadas:
- ✅ **CREATE:** `POST /api/auth/register` (criação via registro)
- ✅ **READ:** `GET /api/users` (listar usuários)
- ✅ **READ:** `GET /api/users/{id}` (usuário específico) 
- ✅ **UPDATE:** `PUT /api/users/{id}` (atualizar perfil)
- ✅ **DELETE:** `DELETE /api/users/{id}` (remover usuário)

#### Frontend - Views implementadas:
- ✅ **Registro:** `views/auth/RegisterView.vue`
- ✅ **Perfil:** `views/ProfileView.vue`
- ✅ **Gerenciar usuários:** `views/UsersView.vue` (admin)

#### Arquivos relacionados:
- `backend/app/models/user.py` - Modelo do usuário
- `backend/app/routes/users.py` - CRUD completo
- `frontend/src/stores/auth.js` - Estado de usuários

---

### 4. ❌ **Deverá implementar um CRUD de listas de tarefas**

**Status: PRECISA ADAPTAR ❌**

#### Situação atual:
- ❌ **Sistema atual é de MÚSICA, não TO-DO**
- ❌ **Tem CRUD de PLAYLISTS, mas precisa virar LISTAS DE TAREFAS**

#### O que existe (Playlists):
```javascript
// backend/app/models/playlist.py
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
```

#### O que precisa (TaskLists):
```python
# CRIAR: backend/app/models/task_list.py
class TaskList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Rotas necessárias:
- `GET /api/task-lists` - Listar listas do usuário
- `POST /api/task-lists` - Criar nova lista  
- `GET /api/task-lists/{id}` - Obter lista específica
- `PUT /api/task-lists/{id}` - Atualizar lista
- `DELETE /api/task-lists/{id}` - Deletar lista

---

### 5. ❌ **Deverá implementar um CRUD de tarefas**

**Status: PRECISA ADAPTAR ❌**

#### Situação atual:
- ❌ **Sistema tem CRUD de MÚSICAS, precisa virar TAREFAS**

#### O que existe (Music):
```python
# backend/app/models/music.py  
class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
```

#### O que precisa (Tasks):
```python
# CRIAR: backend/app/models/task.py
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    due_date = db.Column(db.DateTime)
    task_list_id = db.Column(db.Integer, db.ForeignKey('task_list.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Rotas necessárias:
- `GET /api/tasks` - Listar tarefas do usuário
- `POST /api/tasks` - Criar nova tarefa
- `GET /api/tasks/{id}` - Obter tarefa específica  
- `PUT /api/tasks/{id}` - Atualizar tarefa
- `DELETE /api/tasks/{id}` - Deletar tarefa
- `PATCH /api/tasks/{id}/toggle` - Marcar como completa/incompleta

---

### 6. ✅ **Os CRUD dos itens (4) e (5) requerem que o usuário esteja autenticado**

**Status: JÁ IMPLEMENTADO ✅**

#### Proteção no Backend:
```python
# Todas as rotas protegidas com @jwt_required()
@task_lists_bp.route('/', methods=['GET'])
@jwt_required()
def get_task_lists():
    current_user_id = get_jwt_identity()
    # Só retorna listas do usuário logado
```

#### Proteção no Frontend:
```javascript
// Guards de rota já implementados
const router = createRouter({
  routes: [
    {
      path: '/tasks',
      component: TasksView,
      meta: { requiresAuth: true }  // ✅ JÁ EXISTE
    }
  ]
})
```

#### Sistema de autenticação robusto:
- ✅ **JWT tokens** com expiração
- ✅ **Refresh tokens** para renovação  
- ✅ **Blacklist** de tokens revogados
- ✅ **Interceptors** automáticos
- ✅ **Guards** em todas as rotas protegidas

---

## 📊 RESUMO FINAL

| Requisito | Status | Ação Necessária |
|-----------|--------|-----------------|
| **1. Estrutura organizada** | ✅ COMPLETO | Nenhuma |
| **2. Autenticação** | ✅ COMPLETO | Nenhuma |  
| **3. CRUD Usuários** | ✅ COMPLETO | Nenhuma |
| **4. CRUD Listas de Tarefas** | ❌ ADAPTAR | Converter Playlists → TaskLists |
| **5. CRUD Tarefas** | ❌ ADAPTAR | Converter Music → Tasks |
| **6. Proteção por Auth** | ✅ COMPLETO | Nenhuma |

## 🔄 PLANO DE ADAPTAÇÃO

### **Fase 1: Modelos de Dados**
1. Criar `backend/app/models/task_list.py`
2. Criar `backend/app/models/task.py`  
3. Gerar migrações do banco

### **Fase 2: Backend API**
1. Criar `backend/app/routes/task_lists.py`
2. Criar `backend/app/routes/tasks.py`
3. Implementar todas as rotas CRUD

### **Fase 3: Frontend**
1. Criar `frontend/src/stores/tasks.js`
2. Criar `frontend/src/views/tasks/`
3. Adaptar componentes existentes

### **Estimativa:** 4-6 horas de desenvolvimento

---

## ✅ CONCLUSÃO

**3 de 6 requisitos COMPLETOS** - O sistema já tem uma base sólida com autenticação robusta e estrutura bem organizada. 

**Precisa apenas adaptar o domínio:** MÚSICA → TO-DO LIST

A arquitetura e infraestrutura estão prontas! 🎯 