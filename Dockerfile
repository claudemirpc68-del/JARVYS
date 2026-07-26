FROM python:3.11-slim

# Garante saída limpa de logs em tempo real
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000

WORKDIR /app

# Instala ferramentas essenciais do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código-fonte do repositório
COPY . .

# Garante permissão de execução para o entrypoint
RUN chmod +x /app/entrypoint.sh

# Expõe a porta do Webhook
EXPOSE 5000

# Executa o script de inicialização do container
ENTRYPOINT ["/app/entrypoint.sh"]
