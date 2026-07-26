#!/bin/sh

echo "🚀 [JARVYS] Iniciando serviços no container Coolify..."

# Inicia a automação diária das 18:00 em segundo plano
echo "⏰ [JARVYS] Ativando agendador diário (daily_news_job.py)..."
python daily_news_job.py &

# Define a porta (padrão 5000 ou $PORT injetada pelo Coolify)
PORT=${PORT:-5000}
echo "🌐 [JARVYS] Ativando servidor Webhook na porta $PORT..."

# Executa o servidor Flask em produção via Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 flask_app:app
