import os
import sys
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Garante codificação UTF-8 no terminal Windows
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(override=True)

from ml_pipeline import MLPipeline
from tavily_service import buscar_noticias, TavilyNewsService
from twilio_service import enviar_whatsapp, TwilioService
from groq_agent import GroqNewsAgent
from greeting_skill import GreetingContextSkill

TARGET_HOUR = 20
TARGET_MINUTE = 0

# Fuso horário de Brasília (UTC-3)
TZ_BRASILIA = timezone(timedelta(hours=-3))


def execute_daily_news_dispatch():
    """
    Executa a raspagem de notícias ao vivo no Olhar Digital e Canaltech,
    classifica via ML Pipeline e envia o resumo formatado para o WhatsApp.

    ESTRATÉGIA DE BUSCA (3 tentativas com queries progressivamente mais amplas):
    1. Query curta focada em TI/IA nos domínios alvos
    2. Query genérica nos domínios alvos
    3. Busca geral na web (fallback sem restrição de domínio)
    """
    now_br = datetime.now(TZ_BRASILIA)
    now_str = now_br.strftime('%d/%m/%Y %H:%M:%S')
    print("=" * 70)
    print(f"⏰ [{now_str}] EXECUTANDO RASPAGEM DIÁRIA DO JARVYS (20:00 BRASÍLIA)")
    print("=" * 70)

    user_phone = os.getenv("WHATSAPP_NUMBER", "5511961909818")

    # === ETAPA 1: BUSCA DE NOTÍCIAS (com múltiplas tentativas) ===
    queries = [
        "inteligência artificial tecnologia",
        "IA machine learning novidades",
        "tecnologia inovação Brasil",
    ]

    noticias_raw = []
    for i, query in enumerate(queries, 1):
        print(f"[JARVYS Daily] Tentativa {i}/3 — Buscando: '{query}'...")
        noticias_raw = buscar_noticias(query, max_results=5)
        if noticias_raw and len(noticias_raw) >= 2:
            print(f"[JARVYS Daily] ✅ {len(noticias_raw)} notícias encontradas na tentativa {i}.")
            break
        print(f"[JARVYS Daily] ⚠️ Tentativa {i} retornou {len(noticias_raw)} resultado(s). Tentando próxima query...")

    # Fallback: busca geral sem restrição de domínio
    if not noticias_raw or len(noticias_raw) < 2:
        print("[JARVYS Daily] Tentando busca geral na web (sem restrição de domínio)...")
        try:
            tavily_svc = TavilyNewsService(target_domains=[])
            tavily_svc._ensure_client()
            if tavily_svc.client:
                response = tavily_svc.client.search(
                    query="últimas notícias tecnologia inteligência artificial Brasil",
                    topic="news",
                    max_results=5,
                    search_depth="basic"
                )
                results = response.get("results", [])
                noticias_raw = [
                    {
                        "title": r.get("title", "Sem título"),
                        "url": r.get("url", ""),
                        "snippet": r.get("content", ""),
                        "published_date": r.get("published_date", "")
                    }
                    for r in results
                ]
                print(f"[JARVYS Daily] Busca geral retornou {len(noticias_raw)} notícias.")
        except Exception as e:
            print(f"[JARVYS Daily] Erro na busca geral: {e}")

    if not noticias_raw:
        msg_erro = (
            "🌙 *[RASPAGEM DIÁRIA 20:00 - JARVYS]* 🤖📱\n\n"
            "⚠️ Nenhuma notícia foi encontrada nos portais monitorados neste momento, Claudemir.\n"
            "Tente o comando /raspagem manualmente mais tarde. 🤖"
        )
        enviar_whatsapp(msg_erro, user_phone)
        print("⚠️ Nenhuma notícia encontrada. Mensagem de aviso enviada.")
        return

    # === ETAPA 2: CLASSIFICAÇÃO ML (Naive Bayes + KMeans) ===
    print(f"[JARVYS Daily] Classificando {len(noticias_raw)} notícias via ML Pipeline...")
    pipeline = MLPipeline(n_clusters=min(3, len(noticias_raw)))
    noticias_processadas = pipeline.processar(noticias_raw)

    # === ETAPA 3: FORMATAR MENSAGEM ===
    time_ctx = GreetingContextSkill.get_time_context()
    mensagem = (
        f"🌙 *[RASPAGEM DIÁRIA 20:00 - JARVYS]* 🤖📰\n"
        f"📅 {time_ctx['data_extenso']} às {time_ctx['hora']}\n"
        f"🎯 Portais: _Olhar Digital_ e _Canaltech_\n\n"
    )

    for i, n in enumerate(noticias_processadas, 1):
        title = n.get("title", "Sem título")
        url = n.get("url", "")
        categoria = n.get("categoria", "Geral")
        cluster = n.get("cluster", 0)
        snippet = n.get("snippet", n.get("content", ""))

        mensagem += f"*{i}.* 📰 *{title}*\n"
        mensagem += f"   🏷️ _{categoria}_ | Cluster {cluster}\n"
        if snippet:
            trecho = snippet[:150] + "..." if len(snippet) > 150 else snippet
            mensagem += f"   📝 {trecho}\n"
        mensagem += f"   🔗 {url}\n\n"

    mensagem += f"✅ *{len(noticias_processadas)} notícias raspadas e classificadas via ML Pipeline*"

    # === ETAPA 4: ENVIAR VIA WHATSAPP ===
    print(f"[JARVYS Daily] Enviando raspagem para {user_phone}...")
    success = enviar_whatsapp(mensagem, user_phone)

    if success:
        print(f"✅ Raspagem diária enviada com sucesso! ({len(noticias_processadas)} notícias)")
    else:
        print("❌ Falha ao enviar raspagem diária via Twilio.")


def seconds_until_next_run(target_hour=20, target_minute=0):
    """Calcula os segundos até a próxima execução no horário de Brasília (UTC-3)."""
    now = datetime.now(TZ_BRASILIA)
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if now >= target_time:
        target_time += timedelta(days=1)
    return (target_time - now).total_seconds(), target_time


def run_scheduler_loop():
    print("=" * 70)
    print("🚀 AGENDADOR DIÁRIO DO JARVYS INICIADO!")
    print("📌 Canais Focados: Olhar Digital (olhardigital.com.br) & Canaltech (canaltech.com.br)")
    print(f"⏰ Horário Agendado: Todos os dias às {TARGET_HOUR:02d}:{TARGET_MINUTE:02d} (Brasília / UTC-3)")
    print("Pressione Ctrl+C no terminal para encerrar.")
    print("=" * 70 + "\n")

    while True:
        wait_seconds, next_run = seconds_until_next_run(TARGET_HOUR, TARGET_MINUTE)
        next_run_str = next_run.strftime('%d/%m/%Y às %H:%M:%S')
        hours = int(wait_seconds // 3600)
        minutes = int((wait_seconds % 3600) // 60)
        print(f"⏳ Próxima execução agendada para: {next_run_str} (daqui a {hours}h {minutes}m)")

        # Loop de espera com verificações a cada 30 segundos
        while datetime.now(TZ_BRASILIA) < next_run:
            time.sleep(30)

        # Executa a raspagem das 20:00
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
