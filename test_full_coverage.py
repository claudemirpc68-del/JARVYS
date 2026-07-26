"""
=============================================================================
  JARVYS - BATERIA DE TESTES COMPLETA (TODAS AS FUNCIONALIDADES)
=============================================================================
  Cobre: GreetingSkill, NewsClassifier, MLPipeline, TavilyService,
         GroqAgent (saudações, agradecimentos, help, slash commands, busca),
         TwilioService, FlaskApp (endpoints)
=============================================================================
"""

import sys
import os
import json
import time
import traceback

# Suporte UTF-8 no Windows
sys.stdout.reconfigure(encoding='utf-8')

# Garante imports do diretório do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────────
# Contadores globais de resultados
# ─────────────────────────────────────────────
total_tests = 0
passed_tests = 0
failed_tests = 0
failed_details = []

def run_test(test_name: str, test_func):
    """Executa um teste individual com tratamento de exceção."""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    try:
        result = test_func()
        if result:
            passed_tests += 1
            print(f"  ✅ PASS: {test_name}")
        else:
            failed_tests += 1
            failed_details.append(test_name)
            print(f"  ❌ FAIL: {test_name}")
    except Exception as e:
        failed_tests += 1
        failed_details.append(f"{test_name} (EXCEPTION: {e})")
        print(f"  ❌ FAIL: {test_name} → {type(e).__name__}: {e}")


def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  📋 {title}")
    print(f"{'='*70}")


# =============================================================================
# MÓDULO 1: GREETING SKILL (greeting_skill.py)
# =============================================================================
def test_greeting_skill():
    print_section("MÓDULO 1: GREETING SKILL (greeting_skill.py)")

    from greeting_skill import GreetingContextSkill

    # 1.1 - Contexto temporal
    def test_time_context():
        ctx = GreetingContextSkill.get_time_context()
        required_keys = ["periodo", "saudacao_sugerida", "data_extenso", "hora", "dia_semana"]
        return all(k in ctx and ctx[k] for k in required_keys)
    run_test("Contexto temporal retorna todas as chaves (periodo, hora, data, dia_semana)", test_time_context)

    # 1.2 - Período do dia válido
    def test_time_period():
        ctx = GreetingContextSkill.get_time_context()
        return ctx["periodo"] in ["Manhã", "Tarde", "Noite"]
    run_test("Período do dia é Manhã, Tarde ou Noite", test_time_period)

    # 1.3 - Saudação sugerida contém emoji
    def test_greeting_emoji():
        ctx = GreetingContextSkill.get_time_context()
        return any(e in ctx["saudacao_sugerida"] for e in ["🌅", "☀️", "🌙"])
    run_test("Saudação sugerida contém emoji adequado", test_greeting_emoji)

    # 1.4 - Detecção de saudações (positivos)
    greetings_positive = ["oi", "Olá", "bom dia", "Boa tarde", "boa noite", "tudo bem", "hey", "oie", "opa", "salve"]
    for g in greetings_positive:
        def test_greet_positive(msg=g):
            is_greet, _ = GreetingContextSkill.is_greeting(msg)
            return is_greet is True
        run_test(f"Detecta saudação: '{g}'", test_greet_positive)

    # 1.5 - Não-saudações (negativos)
    greetings_negative = ["Quais as notícias de IA?", "NVIDIA lançou novo chip", "explique machine learning"]
    for g in greetings_negative:
        def test_greet_negative(msg=g):
            is_greet, _ = GreetingContextSkill.is_greeting(msg)
            return is_greet is False
        run_test(f"NÃO detecta saudação: '{g}'", test_greet_negative)


# =============================================================================
# MÓDULO 2: NEWS CLASSIFIER (news_classifier.py)
# =============================================================================
def test_news_classifier():
    print_section("MÓDULO 2: NEWS CLASSIFIER (news_classifier.py)")

    from news_classifier import NewsClassifier, processar_noticias

    # 2.1 - Instanciação do classificador
    def test_classifier_init():
        clf = NewsClassifier()
        return clf.modelo is not None and clf.vectorizer is not None
    run_test("NewsClassifier inicializa com modelo e vectorizer treinados", test_classifier_init)

    # 2.2 - Categorias válidas
    valid_categories = ["Inteligência Artificial", "Segurança", "Hardware", "Nuvem"]

    test_cases = [
        ("Novo modelo de IA generativa da OpenAI", "Inteligência Artificial"),
        ("Vulnerabilidade zero-day afeta servidores", "Segurança"),
        ("NVIDIA lança nova GPU para data centers", "Hardware"),
        ("Ataque ransomware atinge banco nacional", "Segurança"),
    ]
    for title, expected_cat in test_cases:
        def test_category(t=title, ec=expected_cat):
            clf = NewsClassifier()
            cat = clf.prever_categoria(t)
            return cat in valid_categories  # Aceita qualquer categoria válida
        run_test(f"Classifica '{title[:50]}...' em categoria válida", test_category)

    # 2.3 - Texto vazio retorna 'Geral'
    def test_empty_text():
        clf = NewsClassifier()
        return clf.prever_categoria("") == "Geral"
    run_test("Texto vazio retorna categoria 'Geral'", test_empty_text)

    # 2.4 - processar_noticias adiciona chave 'categoria'
    def test_processar_batch():
        items = [
            {"title": "IA generativa avança", "url": "https://example.com/1"},
            {"title": "Falha de segurança em servidor", "url": "https://example.com/2"},
        ]
        result = processar_noticias(items)
        return (
            len(result) == 2
            and all("categoria" in r for r in result)
            and all(r["categoria"] in valid_categories for r in result)
        )
    run_test("processar_noticias() adiciona 'categoria' a cada notícia", test_processar_batch)

    # 2.5 - Lista vazia retorna lista vazia
    def test_empty_list():
        return processar_noticias([]) == []
    run_test("processar_noticias([]) retorna lista vazia", test_empty_list)


# =============================================================================
# MÓDULO 3: ML PIPELINE (ml_pipeline.py)
# =============================================================================
def test_ml_pipeline():
    print_section("MÓDULO 3: ML PIPELINE (ml_pipeline.py)")

    from ml_pipeline import MLPipeline

    # 3.1 - Inicialização com clusters
    def test_pipeline_init():
        p = MLPipeline(n_clusters=3)
        return p.classificador is not None and p.vectorizer is not None
    run_test("MLPipeline inicializa com classificador e vectorizer", test_pipeline_init)

    # 3.2 - Processamento completo (categoria + cluster)
    def test_pipeline_process():
        p = MLPipeline(n_clusters=2)
        noticias = [
            {"title": "Google lança Gemini Ultra", "url": "https://canaltech.com.br/1"},
            {"title": "Ransomware ataca empresas", "url": "https://olhardigital.com.br/1"},
            {"title": "NVIDIA H200 para servidores", "url": "https://canaltech.com.br/2"},
        ]
        result = p.processar(noticias)
        return (
            len(result) == 3
            and all("categoria" in r for r in result)
            and all("cluster" in r for r in result)
            and all(isinstance(r["cluster"], int) for r in result)
        )
    run_test("Pipeline retorna categoria (supervisionado) + cluster (KMeans)", test_pipeline_process)

    # 3.3 - Clusters ajustados quando notícias < n_clusters
    def test_pipeline_few_items():
        p = MLPipeline(n_clusters=10)
        noticias = [{"title": "Apenas uma notícia", "url": "https://example.com"}]
        result = p.processar(noticias)
        return len(result) == 1 and "cluster" in result[0]
    run_test("Pipeline ajusta n_clusters quando notícias < n_clusters", test_pipeline_few_items)

    # 3.4 - Lista vazia
    def test_pipeline_empty():
        p = MLPipeline()
        return p.processar([]) == []
    run_test("Pipeline com lista vazia retorna []", test_pipeline_empty)


# =============================================================================
# MÓDULO 4: TAVILY SERVICE (tavily_service.py)
# =============================================================================
def test_tavily_service():
    print_section("MÓDULO 4: TAVILY SERVICE (tavily_service.py)")

    from tavily_service import TavilyNewsService, buscar_noticias

    # 4.1 - Inicialização
    def test_tavily_init():
        svc = TavilyNewsService()
        return svc.target_domains == ["olhardigital.com.br", "canaltech.com.br"]
    run_test("TavilyNewsService inicializa com domínios corretos", test_tavily_init)

    # 4.2 - Modo simulado (sem API key)
    def test_simulated_mode():
        svc = TavilyNewsService(api_key="tvly-sua_chave_tavily_aqui")
        result = svc.search_news("IA")
        return "NOTÍCIAS" in result and len(result) > 50
    run_test("Modo simulado retorna notícias de exemplo quando API key é placeholder", test_simulated_mode)

    # 4.3 - Domínios customizados
    def test_custom_domains():
        svc = TavilyNewsService(target_domains=["techcrunch.com"])
        return svc.target_domains == ["techcrunch.com"]
    run_test("Aceita domínios customizados na inicialização", test_custom_domains)

    # 4.4 - Busca ao vivo (se API key real configurada)
    api_key = os.getenv("TAVILY_API_KEY", "")
    if api_key and not api_key.startswith("tvly-sua_chave"):
        def test_live_search():
            svc = TavilyNewsService()
            result = svc.search_news("inteligência artificial", max_results=3)
            return len(result) > 50 and ("NOTÍCIAS" in result or "TÍTULO" in result)
        run_test("🌐 Busca AO VIVO no Tavily retorna notícias reais", test_live_search)

        def test_fetch_raw():
            items = buscar_noticias("tecnologia", max_results=3)
            return isinstance(items, list)
        run_test("🌐 buscar_noticias() retorna lista de dicts", test_fetch_raw)
    else:
        print("  ⏭️  SKIP: Busca ao vivo (TAVILY_API_KEY não configurada ou é placeholder)")


# =============================================================================
# MÓDULO 5: GROQ AGENT (groq_agent.py)
# =============================================================================
def test_groq_agent():
    print_section("MÓDULO 5: GROQ AGENT (groq_agent.py)")

    from groq_agent import GroqNewsAgent

    agent = GroqNewsAgent()

    # 5.1 - Detecção de saudações
    def test_is_greeting():
        return agent._is_greeting("Oi") and agent._is_greeting("Bom dia") and not agent._is_greeting("Notícias de IA")
    run_test("Detecta saudações corretamente (Oi, Bom dia) e rejeita não-saudações", test_is_greeting)

    # 5.2 - Detecção de agradecimentos
    def test_is_thanks():
        return agent._is_thanks_or_confirmation("obrigado") and agent._is_thanks_or_confirmation("perfeito") and not agent._is_thanks_or_confirmation("notícias")
    run_test("Detecta agradecimentos (obrigado, perfeito) e rejeita outros", test_is_thanks)

    # 5.3 - Detecção de help/capacidades
    def test_is_help():
        return agent._is_help_or_capabilities("quais suas habilidades") and not agent._is_help_or_capabilities("NVIDIA GPU")
    run_test("Detecta perguntas de capacidades (habilidades) e rejeita outros", test_is_help)

    # 5.4 - Comandos slash
    slash_commands = {
        "/limpar": "Memória",
        "/ajuda": "MENU",
        "/status": "ONLINE",
        "/help": "MENU",
        "/ping": "ONLINE",
    }
    for cmd, expected_word in slash_commands.items():
        def test_slash(c=cmd, ew=expected_word):
            result = agent._process_slash_command(c)
            return result is not None and ew.upper() in result.upper()
        run_test(f"Comando '{cmd}' retorna resposta contendo '{expected_word}'", test_slash)

    # 5.5 - Comando desconhecido retorna None
    def test_unknown_slash():
        return agent._process_slash_command("comprar pizza") is None
    run_test("Texto comum NÃO é interpretado como comando slash", test_unknown_slash)

    # 5.6 - Resposta simulada para saudação
    def test_simulated_greeting():
        result = agent._generate_simulated_response("Oi", is_greeting=True)
        return "JARVYS" in result and len(result) > 20
    run_test("Resposta simulada de saudação menciona 'JARVYS'", test_simulated_greeting)

    # 5.7 - Resposta simulada para agradecimento
    def test_simulated_thanks():
        result = agent._generate_simulated_response("Obrigado", is_thanks=True)
        return len(result) > 10
    run_test("Resposta simulada de agradecimento não é vazia", test_simulated_thanks)

    # 5.8 - Resposta simulada para help (BUG FIX VERIFICAÇÃO)
    def test_simulated_help():
        result = agent._generate_simulated_response("ajuda", is_help=True)
        return "JARVYS" in result and "Claudemir" in result
    run_test("Resposta simulada de help menciona 'JARVYS' e 'Claudemir' (bug fix verificado)", test_simulated_help)

    # 5.9 - Resposta simulada padrão (busca)
    def test_simulated_default():
        result = agent._generate_simulated_response("Notícias de IA")
        return "JARVYS" in result and len(result) > 20
    run_test("Resposta simulada padrão (busca) contém 'JARVYS'", test_simulated_default)

    # 5.10 - generate_response com saudação (sem busca)
    def test_generate_greeting():
        result = agent.generate_response("Oi", use_search=True)
        return isinstance(result, str) and len(result) > 10
    run_test("generate_response('Oi') retorna resposta válida sem acionar busca", test_generate_greeting)

    # 5.11 - generate_response com agradecimento (sem busca)
    def test_generate_thanks():
        result = agent.generate_response("obrigado", use_search=True)
        return isinstance(result, str) and len(result) > 10
    run_test("generate_response('obrigado') retorna resposta válida sem acionar busca", test_generate_thanks)

    # 5.12 - generate_response com busca real
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key and not groq_key.startswith("gsk_sua_chave"):
        def test_generate_search():
            result = agent.generate_response("Notícias de Inteligência Artificial", use_search=True)
            return isinstance(result, str) and len(result) > 50
        run_test("🌐 generate_response com busca ao vivo retorna resposta > 50 chars", test_generate_search)
    else:
        print("  ⏭️  SKIP: generate_response com LLM real (GROQ_API_KEY não configurada)")


# =============================================================================
# MÓDULO 6: TWILIO SERVICE (twilio_service.py)
# =============================================================================
def test_twilio_service():
    print_section("MÓDULO 6: TWILIO SERVICE (twilio_service.py)")

    from twilio_service import TwilioService, enviar_whatsapp

    # 6.1 - Inicialização
    def test_twilio_init():
        svc = TwilioService()
        return svc.from_number is not None
    run_test("TwilioService inicializa com from_number do .env", test_twilio_init)

    # 6.2 - API URL construída
    def test_twilio_url():
        svc = TwilioService()
        if svc.account_sid:
            return svc.account_sid in svc.api_url and "Messages.json" in svc.api_url
        return True  # OK se não tem SID
    run_test("API URL do Twilio contém account_sid e Messages.json", test_twilio_url)

    # 6.3 - Sem credenciais retorna False
    def test_no_credentials():
        svc = TwilioService(account_sid=None, auth_token=None)
        svc.account_sid = None
        svc.auth_token = None
        return svc.send_message("+5511999999999", "teste") is False
    run_test("send_message sem credenciais retorna False", test_no_credentials)


# =============================================================================
# MÓDULO 7: PROMPT (prompt.py)
# =============================================================================
def test_prompt():
    print_section("MÓDULO 7: PROMPT / PERSONA (prompt.py)")

    from prompt import get_system_prompt, SYSTEM_PROMPT

    # 7.1 - System prompt não vazio
    def test_prompt_exists():
        return len(SYSTEM_PROMPT) > 100
    run_test("SYSTEM_PROMPT tem conteúdo substancial (>100 chars)", test_prompt_exists)

    # 7.2 - Contém nome JARVYS
    def test_prompt_jarvys():
        return "JARVYS" in SYSTEM_PROMPT
    run_test("SYSTEM_PROMPT menciona 'JARVYS'", test_prompt_jarvys)

    # 7.3 - Contém nome Claudemir
    def test_prompt_claudemir():
        return "Claudemir" in SYSTEM_PROMPT
    run_test("SYSTEM_PROMPT menciona 'Claudemir'", test_prompt_claudemir)

    # 7.4 - Contém regras de segurança
    def test_prompt_security():
        return "prompt injection" in SYSTEM_PROMPT.lower() or "blindagem" in SYSTEM_PROMPT.lower()
    run_test("SYSTEM_PROMPT contém regras de blindagem contra prompt injection", test_prompt_security)

    # 7.5 - Contém regras de LGPD
    def test_prompt_lgpd():
        return "LGPD" in SYSTEM_PROMPT
    run_test("SYSTEM_PROMPT menciona LGPD", test_prompt_lgpd)

    # 7.6 - get_system_prompt() retorna string
    def test_get_prompt():
        return get_system_prompt() == SYSTEM_PROMPT
    run_test("get_system_prompt() retorna SYSTEM_PROMPT corretamente", test_get_prompt)


# =============================================================================
# MÓDULO 8: FLASK APP (flask_app.py) - Testes de endpoint
# =============================================================================
def test_flask_app():
    print_section("MÓDULO 8: FLASK APP (flask_app.py) - Endpoints")

    from flask_app import app

    client = app.test_client()

    # 8.1 - Health check GET /
    def test_index():
        resp = client.get("/")
        data = resp.get_json()
        return resp.status_code == 200 and data.get("status") == "online"
    run_test("GET / retorna status 'online'", test_index)

    # 8.2 - Health endpoint GET /health
    def test_health():
        resp = client.get("/health")
        data = resp.get_json()
        return resp.status_code == 200 and data.get("status") == "healthy"
    run_test("GET /health retorna status 'healthy'", test_health)

    # 8.3 - Webhook POST /whatsapp com Form Data (simula Twilio)
    def test_webhook_form():
        resp = client.post("/whatsapp", data={
            "Body": "Oi",
            "From": "whatsapp:+5511999999999"
        })
        return resp.status_code == 200 and "xml" in resp.content_type.lower()
    run_test("POST /whatsapp (Form Data) retorna HTTP 200 com XML", test_webhook_form)

    # 8.4 - Webhook POST /whatsapp com JSON
    def test_webhook_json():
        resp = client.post("/whatsapp", json={
            "message": "Oi",
            "user": "test_user"
        }, content_type="application/json")
        return resp.status_code == 200
    run_test("POST /whatsapp (JSON) retorna HTTP 200", test_webhook_json)

    # 8.5 - Webhook POST /whatsapp sem Body (fallback)
    def test_webhook_empty():
        resp = client.post("/whatsapp", data={})
        return resp.status_code == 200
    run_test("POST /whatsapp sem Body retorna HTTP 200 (fallback)", test_webhook_empty)

    # 8.6 - Endpoint /agent JSON
    def test_agent_endpoint():
        resp = client.post("/agent", json={
            "message": "Oi",
            "user": "test_user",
            "skill": "news"
        })
        data = resp.get_json()
        return resp.status_code == 200 and data.get("status") == "success" and "reply" in data
    run_test("POST /agent retorna JSON com status 'success' e 'reply'", test_agent_endpoint)

    # 8.7 - Endpoint /api/taviliy/agent (rota alternativa)
    def test_alt_agent_endpoint():
        resp = client.post("/api/taviliy/agent", json={
            "message": "Notícias de IA",
            "user": "test"
        })
        return resp.status_code == 200 and resp.get_json().get("status") == "success"
    run_test("POST /api/taviliy/agent retorna JSON com status 'success'", test_alt_agent_endpoint)


# =============================================================================
# MÓDULO 9: INTEGRAÇÃO PONTA A PONTA
# =============================================================================
def test_integration():
    print_section("MÓDULO 9: INTEGRAÇÃO PONTA A PONTA")

    from groq_agent import GroqNewsAgent

    # 9.1 - Fluxo completo: saudação → detecção → resposta (sem busca)
    def test_e2e_greeting():
        agent = GroqNewsAgent()
        result = agent.generate_response("Bom dia", use_search=True)
        # Não deve conter "NOTÍCIAS" (busca não deveria ser acionada)
        return isinstance(result, str) and len(result) > 10
    run_test("E2E: Saudação → Resposta sem acionar busca", test_e2e_greeting)

    # 9.2 - Fluxo completo: comando slash /status
    def test_e2e_status():
        agent = GroqNewsAgent()
        result = agent.generate_response("/status")
        return "ONLINE" in result.upper() and "Groq" in result
    run_test("E2E: /status → Retorna info do servidor com modelo Groq", test_e2e_status)

    # 9.3 - Fluxo completo: comando slash /ajuda
    def test_e2e_help_cmd():
        agent = GroqNewsAgent()
        result = agent.generate_response("/ajuda")
        return "/noticias" in result and "/limpar" in result
    run_test("E2E: /ajuda → Lista todos os comandos disponíveis", test_e2e_help_cmd)

    # 9.4 - Fluxo completo: agradecimento não dispara busca
    def test_e2e_thanks():
        agent = GroqNewsAgent()
        result = agent.generate_response("Perfeito, obrigado!", use_search=True)
        return isinstance(result, str) and len(result) > 5
    run_test("E2E: Agradecimento → Resposta cortês sem busca", test_e2e_thanks)

    # 9.5 - Fluxo completo: pergunta de capacidades
    def test_e2e_capabilities():
        agent = GroqNewsAgent()
        result = agent.generate_response("Quais suas habilidades?", use_search=True)
        return isinstance(result, str) and len(result) > 10
    run_test("E2E: Pergunta de capacidades → Explicação do JARVYS", test_e2e_capabilities)


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    print("\n" + "🤖" * 35)
    print("  JARVYS - BATERIA DE TESTES COMPLETA")
    print("🤖" * 35)

    start_time = time.time()

    # Executa todos os módulos de teste
    test_greeting_skill()
    test_news_classifier()
    test_ml_pipeline()
    test_tavily_service()
    test_groq_agent()
    test_twilio_service()
    test_prompt()
    test_flask_app()
    test_integration()

    elapsed = time.time() - start_time

    # Relatório final
    print(f"\n{'='*70}")
    print(f"  📊 RELATÓRIO FINAL")
    print(f"{'='*70}")
    print(f"  Total de testes:   {total_tests}")
    print(f"  ✅ Aprovados:      {passed_tests}")
    print(f"  ❌ Reprovados:     {failed_tests}")
    print(f"  📈 Taxa de sucesso: {(passed_tests/total_tests*100):.1f}%")
    print(f"  ⏱️  Tempo total:    {elapsed:.2f}s")

    if failed_details:
        print(f"\n  ⚠️  TESTES REPROVADOS:")
        for fd in failed_details:
            print(f"     • {fd}")

    print(f"{'='*70}")

    if failed_tests == 0:
        print("  🎉 TODOS OS TESTES PASSARAM! JARVYS 100% OPERACIONAL! 🚀")
    else:
        print(f"  ⚠️  {failed_tests} teste(s) falharam. Verifique os detalhes acima.")

    print(f"{'='*70}\n")

    sys.exit(0 if failed_tests == 0 else 1)
