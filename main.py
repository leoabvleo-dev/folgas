from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import platform
import socket
import os
import subprocess
from datetime import datetime

# root_path="/folgas" garante que redirects e docs funcionem corretamente
# quando a app está atrás do nginx com prefixo /folgas
app = FastAPI(
    title="STI - Folgas API",
    description="Aplicação de teste - Gerência de Operações de Redes / STI UFPB",
    version="1.0.0",
    root_path="/folgas",
)


def get_commit_info():
    """Obtém hash, data e mensagem do último commit."""
    # 1. Tenta via comando git local
    try:
        raw_info = subprocess.check_output(
            ["git", "log", "-1", "--format=%h|%ad|%s", "--date=format:%d/%m/%Y %H:%M:%S"],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(os.path.abspath(__file__))
        ).decode("utf-8").strip()
        if raw_info and "|" in raw_info:
            parts = raw_info.split("|", 2)
            return {
                "hash": parts[0],
                "date": parts[1],
                "message": parts[2] if len(parts) > 2 else ""
            }
    except Exception:
        pass

    # 2. Tenta via arquivo de metadados se gerado no build
    commit_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commit_info.txt")
    if os.path.exists(commit_file):
        try:
            with open(commit_file, "r", encoding="utf-8") as f:
                raw_info = f.read().strip()
                if raw_info and "|" in raw_info:
                    parts = raw_info.split("|", 2)
                    return {
                        "hash": parts[0],
                        "date": parts[1],
                        "message": parts[2] if len(parts) > 2 else ""
                    }
        except Exception:
            pass

    # 3. Fallback para variáveis de ambiente (Coolify / CI)
    sha = (
        os.environ.get("SOURCE_COMMIT")
        or os.environ.get("COOLIFY_GIT_COMMIT_SHA")
        or os.environ.get("GITHUB_SHA")
        or "c098bb6"
    )
    return {
        "hash": sha[:7] if sha else "n/a",
        "date": os.environ.get("COMMIT_DATE", datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
        "message": os.environ.get("COMMIT_MESSAGE", "ci: card de informações do commit adicionado")
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    hostname = socket.gethostname()
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    commit = get_commit_info()

    # URL pública: usa variável de ambiente (Coolify), headers do proxy, ou request.url
    forwarded_host = request.headers.get("x-forwarded-host")
    forwarded_proto = request.headers.get("x-forwarded-proto", "https")
    forwarded_prefix = request.headers.get("x-forwarded-prefix", "")
    if public_url_env := os.environ.get("PUBLIC_URL"):
        public_url = public_url_env.rstrip("/") + "/"
    elif forwarded_host:
        public_url = f"{forwarded_proto}://{forwarded_host}{forwarded_prefix}/"
    else:
        public_url = str(request.url)

    # Identifica o IP Real do Usuário através dos headers do proxy
    if x_client_ip := (request.headers.get("x-client-ip") or request.headers.get("true-client-ip")):
        client_ip = x_client_ip.split(",")[0].strip()
    elif forwarded_for := request.headers.get("x-forwarded-for"):
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.headers.get("x-real-ip") or (request.client.host if request.client else "n/a")

    # Lista formatada de todos os headers recebidos para debug
    headers_debug = "<br/>".join(f"<strong>{k}:</strong> {v}" for k, v in sorted(request.headers.items()))

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>STI UFPB — Folgas</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
        <style>
            *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

            body {{
                font-family: 'Inter', sans-serif;
                background: #0f1117;
                color: #e2e8f0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2rem;
            }}

            .container {{
                max-width: 700px;
                width: 100%;
            }}

            .badge {{
                display: inline-flex;
                align-items: center;
                gap: .5rem;
                background: rgba(34,197,94,.15);
                border: 1px solid rgba(34,197,94,.4);
                color: #4ade80;
                padding: .35rem .9rem;
                border-radius: 999px;
                font-size: .8rem;
                font-weight: 600;
                letter-spacing: .05em;
                text-transform: uppercase;
                margin-bottom: 1.5rem;
            }}

            .badge::before {{
                content: '';
                width: 8px; height: 8px;
                background: #4ade80;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}

            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: .3; }}
            }}

            h1 {{
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #60a5fa, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                line-height: 1.2;
                margin-bottom: .5rem;
            }}

            .subtitle {{
                color: #94a3b8;
                font-size: 1rem;
                margin-bottom: 2rem;
            }}

            .card {{
                background: rgba(255,255,255,.04);
                border: 1px solid rgba(255,255,255,.08);
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                backdrop-filter: blur(10px);
                transition: border-color .2s, transform .2s;
            }}

            .card:hover {{
                border-color: rgba(99,102,241,.5);
                transform: translateY(-2px);
            }}

            .card-commit {{
                background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.08));
                border: 1px solid rgba(99,102,241,0.3);
            }}

            .card-commit:hover {{
                border-color: rgba(168,85,247,0.6);
            }}

            .commit-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.85rem;
            }}

            .commit-hash-pill {{
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                background: rgba(99,102,241,0.25);
                border: 1px solid rgba(99,102,241,0.4);
                color: #c7d2fe;
                padding: 0.2rem 0.6rem;
                border-radius: 6px;
                font-size: 0.85rem;
                font-weight: 600;
            }}

            .card-label {{
                font-size: .75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: .08em;
                color: #64748b;
                margin-bottom: .4rem;
            }}

            .card-value {{
                font-size: 1.05rem;
                font-weight: 500;
                color: #e2e8f0;
                word-break: break-word;
            }}

            .card-value.highlight {{
                color: #818cf8;
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                font-size: .95rem;
            }}

            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                margin-bottom: 1rem;
            }}

            .footer {{
                text-align: center;
                margin-top: 2rem;
                color: #475569;
                font-size: .82rem;
            }}

            .footer a {{
                color: #6366f1;
                text-decoration: none;
            }}

            @media (max-width: 500px) {{
                .grid {{ grid-template-columns: 1fr; }}
                h1 {{ font-size: 1.8rem; }}
                .commit-header {{ flex-direction: column; align-items: flex-start; gap: 0.5rem; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="badge">✓ Aplicação Online</div>

            <h1>STI UFPB<br/>Sistema de Folgas</h1>
            <p class="subtitle">
                Gerência de Operações de Redes — Ambiente de teste via Coolify
            </p>

            <!-- Card do Commit -->
            <div class="card card-commit">
                <div class="commit-header">
                    <div class="card-label" style="color: #a5b4fc; margin-bottom: 0;">🚀 Informações da Versão / Commit</div>
                    <span class="commit-hash-pill">#{commit['hash']}</span>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <div class="card-label">Mensagem do Commit</div>
                    <div class="card-value" style="font-weight: 600; color: #f8fafc;">
                        💬 {commit['message']}
                    </div>
                </div>
                <div>
                    <div class="card-label">Data / Hora do Commit</div>
                    <div class="card-value" style="font-size: 0.95rem; color: #cbd5e1;">
                        🕒 {commit['date']}
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-label">URL de Acesso</div>
                <div class="card-value highlight">{public_url}</div>
            </div>

            <div class="grid">
                <div class="card">
                    <div class="card-label">Servidor (Container)</div>
                    <div class="card-value">{hostname}</div>
                </div>
                <div class="card">
                    <div class="card-label">Data / Hora Atual</div>
                    <div class="card-value">{now}</div>
                </div>
                <div class="card">
                    <div class="card-label">Python</div>
                    <div class="card-value">{platform.python_version()}</div>
                </div>
                <div class="card">
                    <div class="card-label">IP do Cliente</div>
                    <div class="card-value">{client_ip}</div>
                </div>
            </div>

            <div class="card">
                <div class="card-label">Todos os Headers Recebidos (Debug)</div>
                <div class="card-value highlight" style="font-size: 0.8rem; line-height: 1.6; word-break: break-all;">
                    {headers_debug}
                </div>
            </div>

            <div class="footer">
                STI UFPB &mdash; <a href="/folgas/docs">Documentação da API</a> &mdash;
                <a href="/folgas/health">Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/health")
async def health():
    """Endpoint para health check do Coolify/load balancer."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
    }


@app.get("/info")
async def info(request: Request):
    """Retorna informações do ambiente em JSON."""
    return {
        "app": "STI Folgas",
        "version": "1.0.0",
        "commit": get_commit_info(),
        "python": platform.python_version(),
        "hostname": socket.gethostname(),
        "client_ip": request.client.host,
        "headers": dict(request.headers),
        "url": str(request.url),
        "timestamp": datetime.now().isoformat(),
    }
