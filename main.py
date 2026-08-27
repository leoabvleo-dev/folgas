from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import platform
import socket
from datetime import datetime

# root_path="/folgas" garante que redirects e docs funcionem corretamente
# quando a app está atrás do nginx com prefixo /folgas
app = FastAPI(
    title="STI - Folgas API",
    description="Aplicação de teste - Gerência de Operações de Redes / STI UFPB",
    version="1.0.0",
    root_path="/folgas",
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    hostname = socket.gethostname()
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>STI UFPB — Folgas</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet" />
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
                margin-bottom: 2.5rem;
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
                word-break: break-all;
            }}

            .card-value.highlight {{
                color: #818cf8;
                font-family: 'Courier New', monospace;
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

            <div class="card">
                <div class="card-label">URL de Acesso</div>
                <div class="card-value highlight">{request.url}</div>
            </div>

            <div class="grid">
                <div class="card">
                    <div class="card-label">Servidor (Container)</div>
                    <div class="card-value">{hostname}</div>
                </div>
                <div class="card">
                    <div class="card-label">Data / Hora</div>
                    <div class="card-value">{now}</div>
                </div>
                <div class="card">
                    <div class="card-label">Python</div>
                    <div class="card-value">{platform.python_version()}</div>
                </div>
                <div class="card">
                    <div class="card-label">IP do Cliente</div>
                    <div class="card-value">{request.client.host}</div>
                </div>
            </div>

            <div class="card">
                <div class="card-label">Headers recebidos (X-Forwarded)</div>
                <div class="card-value highlight">
                    X-Real-IP: {request.headers.get('x-real-ip', 'n/a')}<br/>
                    X-Forwarded-For: {request.headers.get('x-forwarded-for', 'n/a')}<br/>
                    X-Forwarded-Proto: {request.headers.get('x-forwarded-proto', 'n/a')}
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
        "python": platform.python_version(),
        "hostname": socket.gethostname(),
        "client_ip": request.client.host,
        "headers": dict(request.headers),
        "url": str(request.url),
        "timestamp": datetime.now().isoformat(),
    }
