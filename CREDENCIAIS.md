# 🔐 CREDENCIAIS DE TESTE - MUSIC LIST SYSTEM

## 📋 Usuários Padrão do Sistema

### 👑 ADMINISTRADOR
- **Username:** `admin`
- **Email:** `admin@musiclist.com`
- **Senha:** `admin123`
- **Tipo:** Administrador
- **Permissões:** Acesso total ao sistema

### 👤 USUÁRIO COMUM
- **Username:** `teste`
- **Email:** `teste@musiclist.com`
- **Senha:** `teste123`
- **Tipo:** Usuário comum
- **Permissões:** Usar o sistema normalmente

## 🌐 Como Usar

1. **Acesse o sistema:** http://localhost:3000
2. **Na tela de login, use uma das credenciais acima**
3. **Para registrar novo usuário:** Clique em "Registrar" na tela de login

## 🔧 Como Criar Usuários Manualmente

Se os usuários padrão não existirem, você pode:

### Opção 1: Registrar pela Interface
1. Vá para http://localhost:3000
2. Clique em "Registrar"
3. Preencha o formulário

### Opção 2: Via Script (Backend)
```bash
cd backend
.venv\Scripts\python.exe create_admin.py
```

### Opção 3: Via API diretamente
```bash
# Registrar usuário admin
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@musiclist.com",
    "first_name": "Admin",
    "last_name": "Sistema",
    "password": "admin123"
  }'
```

## 🐛 Problemas Comuns

### "Erro ao fazer login"
- Verifique se o backend está rodando: http://localhost:5000
- Certifique-se de usar as credenciais exatas (case-sensitive)
- Tente registrar um novo usuário

### "Erro ao registrar"
- Verifique se todos os campos estão preenchidos
- Certifique-se de que email é válido
- Senha deve ter pelo menos 6 caracteres

### Backend não responde
- Execute: `python start_app.py` no diretório raiz
- Ou manualmente:
  ```bash
  cd backend
  .venv\Scripts\python.exe run.py
  ```

## ✅ Verificar se Sistema Está Funcionando

1. **Backend Health Check:** http://localhost:5000/api/health
2. **Frontend:** http://localhost:3000
3. **API Info:** http://localhost:5000/api

---

💡 **Dica:** Se nada funcionar, execute `python setup_project.py` para reinstalar tudo! 