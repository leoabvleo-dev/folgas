# Imagem base leve
FROM python:3.12-slim

# Instala git para obter metadados do repositório
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copia e instala dependências primeiro (cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos do repositório
COPY . .

# Salva informações do commit no build
RUN if [ -d .git ]; then git log -1 --format="%h|%ad|%s" --date=format:"%d/%m/%Y %H:%M:%S" > commit_info.txt || true; fi

# Expõe a porta que o uvicorn vai escutar
EXPOSE 5000

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--proxy-headers", "--forwarded-allow-ips", "*"]
