# Imagem base leve
FROM python:3.12-slim

# Diretório de trabalho
WORKDIR /app

# Copia e instala dependências primeiro (cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY main.py .

# Expõe a porta que o uvicorn vai escutar
EXPOSE 5000

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--proxy-headers", "--forwarded-allow-ips", "*"]
