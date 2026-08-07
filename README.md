# 🎫 Sistema de Tickets de Suporte

Sistema completo de gerenciamento de tickets de suporte desenvolvido com FastAPI e Databricks Lakebase (Postgres).

## 📋 Funcionalidades

- ✅ **CRUD completo de tickets**
- ✅ **Sistema de mensagens** em cada ticket
- ✅ **Controle de acesso** baseado em roles (admin, solver, user)
- ✅ **Interface web** responsiva e moderna
- ✅ **Health check** para monitoramento
- ✅ **Autenticação** via OAuth/Databricks

## 🏗️ Arquitetura

```
databricks-ticket-app/
├── app.py                 # Aplicação principal FastAPI
├── app.yaml              # Configuração do Databricks App
├── requirements.txt      # Dependências Python
├── config.py            # Configurações
├── lakebase.py          # Conexão com banco de dados
├── auth.py              # Autenticação e autorização
├── tickets.py           # API endpoints dos tickets
├── schema_db.sql        # Schema do banco
├── seed_data.sql        # Dados de exemplo
└── templates/
    └── index.html       # Interface web
```

## 🗄️ Schema do Banco de Dados

### Tabela: `app_users`
```sql
user_id VARCHAR(255) PRIMARY KEY
role app_role NOT NULL (admin | solver)
created_at TIMESTAMPTZ
```

### Tabela: `tickets`
```sql
ticket_id SERIAL PRIMARY KEY
title VARCHAR(255)
status ticket_status (open | in_progress | resolved)
created_by VARCHAR(255)
assigned_to VARCHAR(255)
created_at TIMESTAMPTZ
resolved_at TIMESTAMPTZ
```

### Tabela: `ticket_messages`
```sql
message_id SERIAL PRIMARY KEY
ticket_id INT (FK -> tickets)
message_text VARCHAR(1024)
author VARCHAR(255)
created_at TIMESTAMPTZ
```

## 🔧 Endpoints da API

### Health Check
- `GET /health` - Health check da aplicação
- `GET /api/health` - Health check (formato API)

### Interface Web
- `GET /` - Interface web principal

### Tickets
- `GET /api/tickets` - Lista todos os tickets do usuário
- `GET /api/tickets/{id}` - Detalhes de um ticket específico
- `POST /api/tickets` - Cria um novo ticket
- `POST /api/tickets/{id}/messages` - Adiciona mensagem ao ticket
- `PATCH /api/tickets/{id}/status` - Atualiza status (admin/solver only)

## 🎯 Controle de Acesso

### Roles

**Admin:**
- Visualizar todos os tickets
- Criar tickets
- Adicionar mensagens
- Atualizar status de qualquer ticket

**Solver:**
- Visualizar todos os tickets
- Adicionar mensagens
- Atualizar status de qualquer ticket

**User (padrão):**
- Visualizar apenas seus próprios tickets
- Criar tickets
- Adicionar mensagens aos próprios tickets

## ⚙️ Configuração

### 1. Variáveis de Ambiente (app.yaml)

```yaml
env:
  - name: LAKEBASE_SECRET_SCOPE
    value: "database"
  - name: LAKEBASE_SECRET_KEY
    value: "lakebase-url"
  - name: ENV_MODE
    value: "development"  # ou "production"
  - name: DEFAULT_ADMIN
    value: "seu-email@empresa.com"
```

### 2. Configurar Secret do Lakebase

Crie um secret no Databricks com a connection string do Postgres:

```bash
databricks secrets create-scope database
databricks secrets put-secret database lakebase-url
```

Formato da connection string:
```
postgresql://role:password@host:5432/databricks_postgres?sslmode=require
```

### 3. Instalar Dependências

O arquivo `requirements.txt` contém:
```
fastapi
uvicorn
psycopg2-binary
sqlalchemy
databricks-sdk
jinja2
```

## 🚀 Deploy

### Usando Databricks Apps

```bash
# Deploy da aplicação
databricks apps deploy /Users/seu-usuario/databricks-ticket-app

# Ou start para desenvolvimento
databricks apps start /Users/seu-usuario/databricks-ticket-app
```

### Inicialização Automática

No primeiro start, a aplicação automaticamente:
1. Cria o schema do banco (tabelas, tipos, constraints)
2. Carrega dados de exemplo (se `ENV_MODE=development`)
3. Cria o usuário admin padrão

## 🧪 Testando

### Health Check
```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "service": "ticket-system",
  "components": {
    "application": "up",
    "database": "up"
  }
}
```

### Criar um Ticket
```bash
curl -X POST http://localhost:8000/api/tickets \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "title=Problema no sistema&description=Descrição detalhada"
```

### Listar Tickets
```bash
curl http://localhost:8000/api/tickets
```

## 🔍 Otimizações Implementadas

### Query Otimizada (Sem N+1)

O endpoint `GET /api/tickets/{id}` usa uma única query com JOIN:

```sql
SELECT 
    t.ticket_id, t.title, t.status, ...,
    m.message_id, m.message_text, m.author, ...
FROM tickets t
LEFT JOIN ticket_messages m ON t.ticket_id = m.ticket_id
WHERE t.ticket_id = %s
ORDER BY m.created_at ASC
```

Em vez de:
```sql
-- Query 1: buscar ticket
SELECT * FROM tickets WHERE ticket_id = %s

-- Query 2: buscar mensagens (N+1 problem!)
SELECT * FROM ticket_messages WHERE ticket_id = %s
```

### Funções de Banco Corretas

- `run_query()` - SELECTs (sem commit)
- `run_write()` - INSERT/UPDATE/DELETE (com commit)
- `run_write_returning()` - INSERT/UPDATE com RETURNING (com commit)

## 📚 Estrutura do Código

### app.py
Aplicação principal FastAPI com:
- Inicialização do banco
- Registro dos routers
- Endpoint raiz e health check

### tickets.py
Todos os endpoints da API de tickets:
- Validação de permissões
- Queries otimizadas
- Tratamento de erros

### auth.py
Sistema de autenticação:
- `get_current_user()` - Extrai email do header
- `get_user_role()` - Consulta role no banco

### lakebase.py
Gerenciamento do banco:
- Conexão com Postgres
- Funções de query/write
- Inicialização do schema

## 🛠️ Desenvolvimento

### Modo Development

Quando `ENV_MODE=development`:
- Carrega dados de exemplo automaticamente
- Logs mais verbosos
- Mensagens de debug

### Modo Production

Quando `ENV_MODE=production`:
- Sem dados de exemplo
- Logs otimizados
- Pronto para uso real

## 🐛 Troubleshooting

### Erro: "Ticket not found or access denied"
- Verifique se o usuário tem permissão (role)
- Confirme que o ticket_id existe

### Erro: "Unauthorized: Only admin or solver"
- Operação requer role admin ou solver
- Verifique a tabela `app_users`

### Erro de Conexão com Banco
- Verifique o secret `lakebase-url`
- Confirme que o Lakebase está ativo
- Teste a connection string manualmente

## 📝 Licença

Projeto desenvolvido para demonstração de FastAPI + Databricks Lakebase.

## 👥 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**Desenvolvido com ❤️ usando FastAPI e Databricks Lakebase**
