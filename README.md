# Aplicação Python — STI UFPB / Folgas

Aplicação de teste em **FastAPI** para validar o ambiente de hospedagem via **Coolify**,
com reverse proxy pelo **nginx** na rota `https://sti.ufpb.br/folgas`.

## Stack

- **Python 3.12**
- **FastAPI** + **Uvicorn**
- **Docker** (build pelo Coolify)

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/folgas/` | Página de status visual |
| GET | `/folgas/health` | Health check (JSON) |
| GET | `/folgas/info` | Informações do ambiente (JSON) |
| GET | `/folgas/docs` | Documentação automática (Swagger UI) |

## Rodar localmente

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
# Acesse: http://localhost:5000/folgas/
```

## Rodar com Docker

```bash
docker build -t folgas-app .
docker run -p 5000:5000 folgas-app
# Acesse: http://localhost:5000/folgas/
```

## Deploy no Coolify

1. Criar nova **Application** → Source: **GitHub** → repo `leoabvleo/folgas`
2. Build Pack: **Dockerfile**
3. Port: **5000**
4. Domain: `http://folgas.apps.ufpb.br`
5. Health Check Path: `/folgas/health`

## Arquitetura

```
Usuário (HTTPS)
      │
      ▼
nginx2 (sti.ufpb.br:443)
  location /folgas → proxy_pass http://150.165.254.70  Host: folgas.apps.ufpb.br
      │
      ▼
Coolify Traefik (:80)
  roteia pelo Host header → container FastAPI (:5000)
```

<!-- Deploy automático via Coolify e GitHub Actions ativo -->
