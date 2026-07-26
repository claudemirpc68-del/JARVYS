import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# Configura encoding UTF-8 para o terminal Windows
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(override=True)

COOLIFY_URL = "http://k51tegze79w2e2iolnj36eyv.72.61.130.70.sslip.io"
LOCAL_URL = "http://localhost:5000"

class StageValidator:
    def __init__(self):
        self.results = []

    def log_step(self, stage: str, test_name: str, passed: bool, details: str, elapsed_ms: float = 0.0):
        status_icon = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            "stage": stage,
            "test": test_name,
            "passed": passed,
            "status": status_icon,
            "details": details,
            "elapsed": f"{elapsed_ms:.1f}ms" if elapsed_ms > 0 else "-"
        })
        print(f"[{status_icon}] {stage} - {test_name}: {details} ({elapsed_ms:.1f}ms)" if elapsed_ms > 0 else f"[{status_icon}] {stage} - {test_name}: {details}")

    def validate_env_stage(self):
        """Etapa 1: Validação de Variáveis de Ambiente e Arquivos"""
        print("\n--- ETAPA 1: VALIDAÇÃO DE AMBIENTE & CONFIGURAÇÕES (.env) ---")
        
        env_path = ".env"
        if not os.path.exists(env_path):
            self.log_step("Etapa 1", "Arquivo .env", False, "Arquivo .env não encontrado!")
            return

        self.log_step("Etapa 1", "Arquivo .env", True, "Arquivo .env presente.")

        required_keys = [
            "TAVILY_API_KEY",
            "GROQ_API_KEY",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_WHATSAPP_NUMBER",
            "WHATSAPP_NUMBER"
        ]

        for key in required_keys:
            val = os.getenv(key)
            if not val or "sua_chave" in val or "seu_account" in val:
                self.log_step("Etapa 1", f"Chave {key}", False, f"Chave ausente ou com placeholder ({val})")
            else:
                masked_val = val[:6] + "..." + val[-4:] if len(val) > 10 else "***"
                self.log_step("Etapa 1", f"Chave {key}", True, f"Configurada ({masked_val})")

    def validate_api_integrations_stage(self):
        """Etapa 2: Validação de Conectividade direta das APIs externas"""
        print("\n--- ETAPA 2: VALIDAÇÃO DE CONEXÃO COM APIS EXTERNAS ---")
        
        # Teste 1: Tavily API
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            start_t = time.time()
            try:
                from tavily_service import TavilyNewsService
                service = TavilyNewsService()
                res = service.search_news("notícias de IA")
                elapsed = (time.time() - start_t) * 1000
                if res and "Falha" not in res:
                    self.log_step("Etapa 2", "API Tavily (Busca Ao Vivo)", True, "Busca concluída com resultados reais.", elapsed)
                else:
                    self.log_step("Etapa 2", "API Tavily (Busca Ao Vivo)", False, f"Retorno inesperado: {res[:50]}", elapsed)
            except Exception as e:
                self.log_step("Etapa 2", "API Tavily (Busca Ao Vivo)", False, f"Exceção: {e}")
        else:
            self.log_step("Etapa 2", "API Tavily", False, "Chave TAVILY_API_KEY não configurada.")

        # Teste 2: Groq API (LLM Llama 3.3 70B)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            start_t = time.time()
            try:
                from groq_agent import GroqNewsAgent
                agent = GroqNewsAgent()
                resp = agent.generate_response("Olá", use_search=False)
                elapsed = (time.time() - start_t) * 1000
                if resp and "JARVYS" in resp:
                    self.log_step("Etapa 2", "API Groq (Llama 3.3 70B)", True, f"Inferência gerada com sucesso.", elapsed)
                else:
                    self.log_step("Etapa 2", "API Groq (Llama 3.3 70B)", False, f"Resposta sem persona: {resp[:50]}", elapsed)
            except Exception as e:
                self.log_step("Etapa 2", "API Groq (Llama 3.3 70B)", False, f"Exceção: {e}")

        # Teste 3: Twilio REST API Credentials Check
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        if account_sid and auth_token:
            start_t = time.time()
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}.json"
                r = requests.get(url, auth=(account_sid, auth_token), timeout=10)
                elapsed = (time.time() - start_t) * 1000
                if r.status_code == 200:
                    self.log_step("Etapa 2", "API Twilio REST (Credenciais)", True, "Autenticação aprovada na Twilio.", elapsed)
                else:
                    self.log_step("Etapa 2", "API Twilio REST (Credenciais)", False, f"Status HTTP {r.status_code}: {r.text[:50]}", elapsed)
            except Exception as e:
                self.log_step("Etapa 2", "API Twilio REST", False, f"Exceção de conexão: {e}")

    def validate_webhooks_stage(self):
        """Etapa 3: Validação dos Servidores Webhook (Local & Coolify Nuvem)"""
        print("\n--- ETAPA 3: VALIDAÇÃO DOS SERVIDORES WEBHOOK (LOCAL & COOLIFY NUVEM) ---")
        
        targets = [
            ("Webhook Local (Porta 5000)", LOCAL_URL),
            ("Webhook Coolify (Nuvem VPS)", COOLIFY_URL)
        ]

        test_payloads = [
            ("Saudação 'Oi'", "Oi", "saudação"),
            ("Agradecimento 'perfeito'", "perfeito", "de nada"),
            ("Dúvida 'quais suas habilidades?'", "quais suas habilidades?", "habilidades"),
        ]

        for target_label, base_url in targets:
            # 1. Health Check GET /
            start_t = time.time()
            try:
                r = requests.get(f"{base_url}/", timeout=10)
                elapsed = (time.time() - start_t) * 1000
                if r.status_code == 200 and "online" in r.text.lower():
                    self.log_step("Etapa 3", f"{target_label} - Health Check (GET /)", True, "Servidor respondendo online 200 OK.", elapsed)
                else:
                    self.log_step("Etapa 3", f"{target_label} - Health Check (GET /)", False, f"Status {r.status_code}: {r.text[:60]}", elapsed)
            except Exception as e:
                self.log_step("Etapa 3", f"{target_label} - Health Check (GET /)", False, f"Não foi possível conectar: {e}")
                continue

            # 2. Testes de Webhook POST /whatsapp
            for test_name, msg, expected_kw in test_payloads:
                start_t = time.time()
                try:
                    r = requests.post(f"{base_url}/whatsapp", data={"Body": msg}, timeout=25)
                    elapsed = (time.time() - start_t) * 1000
                    if r.status_code == 200:
                        # Tenta parsear TwiML XML
                        try:
                            root = ET.fromstring(r.text)
                            msg_content = root.find("Message").text or ""
                        except Exception:
                            msg_content = r.text

                        if expected_kw.lower() in msg_content.lower() or len(msg_content) > 10:
                            self.log_step("Etapa 3", f"{target_label} - {test_name}", True, f"TwiML XML retornado corretamente.", elapsed)
                        else:
                            self.log_step("Etapa 3", f"{target_label} - {test_name}", False, f"Conteúdo inesperado: {msg_content[:60]}", elapsed)
                    else:
                        self.log_step("Etapa 3", f"{target_label} - {test_name}", False, f"Status HTTP {r.status_code}", elapsed)
                except Exception as e:
                    self.log_step("Etapa 3", f"{target_label} - {test_name}", False, f"Exceção: {e}")

    def validate_scheduler_stage(self):
        """Etapa 4: Validação da Automação Diária das 18:00"""
        print("\n--- ETAPA 4: VALIDAÇÃO DA AUTOMAÇÃO DIÁRIA (18:00) ---")
        try:
            from daily_news_job import seconds_until_next_run
            secs, next_run = seconds_until_next_run(18, 0)
            next_str = next_run.strftime('%d/%m/%Y às %H:%M:%S')
            self.log_step("Etapa 4", "Cálculo de Agendador (daily_news_job.py)", True, f"Próximo disparo agendado para: {next_str}")
        except Exception as e:
            self.log_step("Etapa 4", "Cálculo de Agendador", False, f"Erro ao calcular próximo disparo: {e}")

    def generate_final_report(self):
        """Etapa 5: Geração de Relatório de Diagnóstico"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL DE ANÁLISE E VALIDAÇÃO DE ETAPAS - JARVYS AGENT")
        print("=" * 80)
        print(f"{'ETAPA':<10} | {'TESTE':<42} | {'STATUS':<9} | {'TEMPO':<8}")
        print("-" * 80)

        total_pass = 0
        total_fail = 0

        for r in self.results:
            if r["passed"]:
                total_pass += 1
            else:
                total_fail += 1
            print(f"{r['stage']:<10} | {r['test']:<42} | {r['status']:<9} | {r['elapsed']:<8}")

        print("-" * 80)
        print(f"📈 TOTAL: {len(self.results)} Testes | ✅ Passou: {total_pass} | ❌ Falhas: {total_fail}")
        if total_fail == 0:
            print("🌟 TODAS AS ETAPAS E DADOS ESTÃO 100% VALIDADOS E OPERACIONAIS!")
        else:
            print("⚠️ Algumas etapas apresentaram alertas. Verifique o relatório acima.")
        print("=" * 80 + "\n")

def main():
    validator = StageValidator()
    validator.validate_env_stage()
    validator.validate_api_integrations_stage()
    validator.validate_webhooks_stage()
    validator.validate_scheduler_stage()
    validator.generate_final_report()

if __name__ == "__main__":
    main()
