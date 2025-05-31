# Guia de Migração: SQLite para PostgreSQL

Este guia explica como migrar seu sistema de música do SQLite para PostgreSQL.

## ⚠️ Importante: Backup dos Dados

Antes de migrar, faça backup dos seus dados:

```bash
# Fazer backup do banco SQLite
cp music_app.db music_app_backup.db

# Fazer backup das músicas
cp -r static/uploads static/uploads_backup
```

## Passo 1: Instalar PostgreSQL

### Opção A: Instalação Automática (Recomendado)

Execute o PowerShell como **Administrador** e rode:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install_postgresql.ps1
```

### Opção B: Instalação Manual

1. Baixe PostgreSQL do site oficial: https://www.postgresql.org/download/windows/
2. Execute o instalador
3. Configure a senha do usuário `postgres`
4. Mantenha as configurações padrão (porta 5432)

## Passo 2: Configurar Banco de Dados

```bash
# Ativar ambiente virtual
.venv\Scripts\activate

# Instalar driver PostgreSQL
pip install psycopg2-binary

# Configurar banco de dados
python setup_database.py
```

## Passo 3: Atualizar Configurações

Edite o arquivo `.env`:

```env
# Comentar SQLite
# DATABASE_URL=sqlite:///music_app.db

# Descomentar PostgreSQL
DATABASE_URL=postgresql://music_user:music_password@localhost:5432/music_app_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=music_app_db
POSTGRES_USER=music_user
POSTGRES_PASSWORD=music_password
```

## Passo 4: Executar Migrações

```bash
# Remover migrações antigas do SQLite
rm -rf migrations/

# Inicializar migrações para PostgreSQL
flask db init

# Criar migração inicial
flask db migrate -m "Initial PostgreSQL migration"

# Aplicar migrações
flask db upgrade
```

## Passo 5: Migrar Dados (Opcional)

Se você tem dados importantes no SQLite:

```bash
# Instalar ferramenta de migração
pip install sqlite3-to-postgresql

# Executar migração
python migrate_data.py
```

## Passo 6: Testar Sistema

```bash
# Testar conexão
python setup_database.py test

# Iniciar servidor
python run.py
```

## Passo 7: Configurar para Produção

### Configurações de Segurança

1. **Altere as senhas padrão**:
   ```env
   SECRET_KEY=sua-chave-super-secreta-aqui
   JWT_SECRET_KEY=sua-chave-jwt-super-secreta
   POSTGRES_PASSWORD=senha-forte-aqui
   ```

2. **Configure SSL** (recomendado para produção):
   ```env
   DATABASE_URL=postgresql://music_user:senha@localhost:5432/music_app_db?sslmode=require
   ```

3. **Configure backup automático**:
   ```bash
   # Adicionar ao crontab (Linux) ou Task Scheduler (Windows)
   pg_dump music_app_db > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

## Verificação Final

1. **Teste todas as funcionalidades**:
   - ✅ Login/Registro
   - ✅ Upload de músicas
   - ✅ Criação de playlists
   - ✅ Busca no Spotify

2. **Verifique performance**:
   - Tempo de carregamento das páginas
   - Velocidade de upload
   - Responsividade da busca

3. **Monitore logs**:
   ```bash
   # Ver logs do PostgreSQL
   tail -f /var/log/postgresql/postgresql-15-main.log
   ```

## Solução de Problemas

### Erro de Conexão
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql  # Linux
net start postgresql-x64-15       # Windows

# Verificar configurações
psql -U postgres -h localhost -p 5432
```

### Erro de Permissão
```sql
-- Conectar como postgres e executar:
GRANT ALL PRIVILEGES ON DATABASE music_app_db TO music_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO music_user;
```

### Performance Lenta
```sql
-- Criar índices para melhor performance
CREATE INDEX idx_music_title ON music(title);
CREATE INDEX idx_music_artist ON music(artist);
CREATE INDEX idx_playlist_created_at ON playlist_music(created_at);
```

## Benefícios do PostgreSQL

- ✅ **Performance**: Muito mais rápido para grandes volumes de dados
- ✅ **Confiabilidade**: ACID compliance e transações robustas
- ✅ **Recursos Avançados**: JSON, arrays, full-text search
- ✅ **Escalabilidade**: Suporte a milhões de registros
- ✅ **Backup/Restore**: Ferramentas profissionais
- ✅ **Monitoring**: Logs detalhados e métricas

## Próximos Passos

Após a migração bem-sucedida:

1. **Configure monitoramento** com pgAdmin ou similar
2. **Implemente backup automático**
3. **Configure SSL/TLS** para conexões seguras
4. **Otimize queries** com EXPLAIN ANALYZE
5. **Configure connection pooling** para produção

---

**Dúvidas?** Execute `python setup_database.py test` para verificar a conexão. 