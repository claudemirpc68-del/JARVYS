import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Garante codificação UTF-8 no terminal Windows
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(override=True)

from ml_pipeline import MLPipeline
from tavily_service import buscar_noticias, TavilyNewsService
from twilio_service import enviar_whatsapp, TwilioService

TARGET_HOUR = 18
TARGET_MINUTE = 0

def job_diario():
    """Rotina diária com Machine Learning (Classificação + KMeans Clustering)"""
    print("[JARVYS Daily ML] Buscando notícias para pipeline de ML...")
    noticias = buscar_noticias("tecnologia e inteligência artificial", max_results=5)
    if not noticias:
        print("[JARVYS Daily ML] Nenhuma notícia encontrada.")
        return

    pipeline = MLPipeline(n_clusters=3)
    noticias_processadas = pipeline.processar(noticias)

    mensagem = "🤖 *JARVYS News 18h* 📰📱\n\n"
    for n in noticias_processadas:
        mensagem += f"📰 *[{n['categoria']}]* (Cluster {n['cluster']})\n{n['title']}\n🔗 {n['url']}\n\n"

    enviar_whatsapp(mensagem)

def execute_daily_news_dispatch():
    """
    Executa a raspagem de notícias ao vivo no Olhar Digital e Canaltech
    e envia o resumo diário formatado diretamente para o WhatsApp do usuário.
    """
    now_str = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print("=" * 70)
    print(f"⏰ [{now_str}] EXECUTANDO ROTINA DIÁRIA DO JARVYS (NOTÍCIAS 18:00)")
    print("=" * 70)

    agent = GroqNewsAgent()
    user_phone = os.getenv("WHATSAPP_NUMBER", "5511961909818")

    prompt_msg = "Principais notícias e destaques de hoje no Olhar Digital e Canaltech sobre tecnologia e inteligência artificial"
    print(f"[JARVYS Daily] Raspando notícias ao vivo nos canais alvos (Olhar Digital & Canaltech)...")
    news_digest = agent.generate_response(user_message=prompt_msg, use_search=True)

    header = "🌅 *[RESUMO DIÁRIO DAS 18:00 - JARVYS]* 🤖📱\n\n"
    final_message = header + news_digest

    print(f"[JARVYS Daily] Enviando resumo diário para {user_phone}...")
    success = enviar_whatsapp(final_message, user_phone)

    if success:
        print("✅ Resumo diário enviado com sucesso para o WhatsApp!")
    else:
        print("❌ Falha ao enviar resumo diário via Twilio.")

def seconds_until_next_run(target_hour=18, target_minute=0):
    """Calcula os segundos até a próxima execução às 18:00."""
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if now >= target_time:
        target_time += timedelta(days=1)
    return (target_time - now).total_seconds(), target_time

def run_scheduler_loop():
    print("=" * 70)
    print("🚀 AGENDADOR DIÁRIO DO JARVYS INICIADO!")
    print("📌 Canais Focados: Olhar Digital (olhardigital.com.br) & Canaltech (canaltech.com.br)")
    print(f"⏰ Horário Agendado: Todos os dias às {TARGET_HOUR:02d}:{TARGET_MINUTE:02d}")
    print("Pressione Ctrl+C no terminal para encerrar.")
    print("=" * 70 + "\n")

    while True:
        wait_seconds, next_run = seconds_until_next_run(TARGET_HOUR, TARGET_MINUTE)
        next_run_str = next_run.strftime('%d/%m/%Y às %H:%M:%S')
        hours = int(wait_seconds // 3600)
        minutes = int((wait_seconds % 3600) // 60)
        print(f"⏳ Próxima execução agendada para: {next_run_str} (daqui a {hours}h {minutes}m)")
        
        # Loop de espera com verificações a cada 30 segundos
        while datetime.now() < next_run:
            time.sleep(30)

        # Executa a automação das 18:00
        try:
            execute_daily_news_dispatch()
        except Exception as e:
            print(f"❌ Erro na execução da automação diária: {e}")

        # Aguarda 60s para evitar execução duplicada no mesmo minuto
        time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        print("⚡ Executando disparo imediato de teste (--now)...")
        execute_daily_news_dispatch()
    else:
        run_scheduler_loop()
