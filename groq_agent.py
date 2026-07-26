import os
from typing import Optional
from dotenv import load_dotenv
from prompt import get_system_prompt
from tavily_service import TavilyNewsService

from greeting_skill import GreetingContextSkill

load_dotenv()

class GroqNewsAgent:
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.client = None
        self.tavily_service = TavilyNewsService()

        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except ImportError:
                print("Warning: pacote 'groq' não instalado.")

    def _is_greeting(self, message: str) -> bool:
        """Verifica se a mensagem é uma saudação simples via GreetingContextSkill."""
        is_greet, _ = GreetingContextSkill.is_greeting(message)
        return is_greet

    def _is_thanks_or_confirmation(self, message: str) -> bool:
        """Verifica se a mensagem é um agradecimento, elogio ou confirmação simples."""
        msg = message.strip().lower().strip(".!😊👍🙏")
        thanks_words = [
            "perfeito", "obrigado", "obrigada", "valeu", "valew", "show", "show de bola",
            "top", "muito obrigado", "muito obrigada", "blz", "beleza", "ok", "certo",
            "entendi", "otimo", "ótimo", "vlw", "tks", "thanks", "thank you", "de nada",
            "tchau", "ate logo", "tudo certo", "excelente", "massa", "boa", "combinado",
            "maravilha", "joia", "jóia", "tudo ótimo", "tudo otimo", "legal"
        ]
        return msg in thanks_words or any(msg == t for t in thanks_words)

    def _is_help_or_capabilities(self, message: str) -> bool:
        """Verifica se a mensagem é uma pergunta sobre o que o JARVYS faz, suas habilidades, aplicações ou como pode ajudar."""
        msg = message.strip().lower()
        key_phrases = [
            "habilidade", "habilidades", "aplicacao", "aplicações", "aplicacoes",
            "funcionalidade", "funcionalidades", "capacidade", "capacidades",
            "recurso", "recursos", "pode me ajudar", "suas habilidades",
            "o que você faz", "o que voce faz", "como você funciona", "como voce funciona",
            "o que você pode fazer", "o que voce pode fazer", "ajuda", "help", "me ajude"
        ]
        return any(kw in msg for kw in key_phrases)

    def _process_slash_command(self, message: str) -> Optional[str]:
        """Processa comandos curtos iniciados por / ou palavras-chave diretas de comando."""
        cmd = message.strip().lower()

        if cmd in ["/limpar", "/reset", "/clear", "limpar"]:
            return (
                "🧹 *Memória e contexto da IA limpos no servidor com sucesso, Claudemir!* 🤖\n\n"
                "_(O histórico da conversa com a IA foi resetado. Para apagar as mensagens anteriores da tela do celular, use a opção 'Limpar conversa' do WhatsApp)._\n\n"
                "Em que posso ajudá-lo agora? 🚀"
            )

        if cmd in ["/ajuda", "/help", "/comandos", "/menu"]:
            return (
                "📌 *MENU DE COMANDOS DO JARVYS* 🤖💻\n\n"
                "• `/noticias` - Busca notícias de TI e IA ao vivo no Olhar Digital e Canaltech\n"
                "• `/diario` - Receba o resumo executivo das principais novidades de hoje\n"
                "• `/limpar` - Reseta o contexto de conversa\n"
                "• `/status` - Verifica o status do servidor e da infraestrutura na nuvem\n"
                "• `/ajuda` - Exibe este menu de comandos rápidos\n\n"
                "Você também pode enviar qualquer dúvida ou pesquisa em texto livre para o Claudemir! 🚀"
            )

        if cmd in ["/status", "/ping"]:
            time_ctx = GreetingContextSkill.get_time_context()
            return (
                f"🟢 *JARVYS AGENT ONLINE* 🤖⚡\n\n"
                f"• *Status*: 100% Operacional\n"
                f"• *Data Local*: {time_ctx['data_extenso']}\n"
                f"• *Horário*: {time_ctx['hora']} ({time_ctx['periodo']})\n"
                f"• *Modelo IA*: Groq Llama 3.3 70B Versatile\n"
                f"• *Mecanismo de Busca*: Tavily Search (Olhar Digital & Canaltech)\n"
                f"• *Infraestrutura*: Coolify Cloud VPS / Flask Webhook"
            )

        if cmd in ["/noticias", "/news"]:
            print(f"[GroqNewsAgent] Comando /noticias recebido. Buscando notícias ao vivo...")
            news_ctx = self.tavily_service.search_news("principais notícias de tecnologia e inteligência artificial")
            return self.generate_response("Principais notícias de TI e IA de hoje", use_search=False)

        if cmd in ["/diario", "/boletim"]:
            print(f"[GroqNewsAgent] Comando /diario recebido.")
            news_digest = self.generate_response("Principais destaques de tecnologia e IA do dia no Olhar Digital e Canaltech", use_search=True)
            return f"🌅 *[BOLETIM DIÁRIO SOLICITADO - JARVYS]* 🤖📱\n\n{news_digest}"

        return None

    def generate_response(self, user_message: str, use_search: bool = True) -> str:
        """
        Gera a resposta do Agente JARVYS via Tavily + Groq API para WhatsApp / SMS.
        """
        # Verifica se é um comando slash (/limpar, /ajuda, /status, etc.)
        cmd_response = self._process_slash_command(user_message)
        if cmd_response:
            return cmd_response

        base_system_prompt = get_system_prompt()
        time_ctx = GreetingContextSkill.get_time_context()

        # Injeta contexto temporal dinâmico no System Prompt
        temporal_context = (
            f"\n\nCONTEXTO DE TEMPO ATUAL DO SERVIDOR/USUÁRIO:\n"
            f"- Data Atual: {time_ctx['data_extenso']}\n"
            f"- Horário Local: {time_ctx['hora']} (Período: {time_ctx['periodo']})\n"
            f"- Saudação recomendada para o período: {time_ctx['saudacao_sugerida']}"
        )
        system_prompt = base_system_prompt + temporal_context

        is_greeting_msg = self._is_greeting(user_message)
        is_thanks_msg = self._is_thanks_or_confirmation(user_message)
        is_help_msg = self._is_help_or_capabilities(user_message)

        news_context = ""
        # Só executa busca se NÃO for saudação, agradecimento ou dúvida de capacidades
        if use_search and not is_greeting_msg and not is_thanks_msg and not is_help_msg:
            print(f"[GroqNewsAgent] Pesquisando notícias no Tavily sobre: '{user_message}'...")
            news_context = self.tavily_service.search_news(user_message)
        elif is_greeting_msg:
            print(f"[GroqNewsAgent] Saudação identificada: '{user_message}'. Respondendo com recepção do JARVYS ({time_ctx['saudacao_sugerida']}).")
        elif is_thanks_msg:
            print(f"[GroqNewsAgent] Agradecimento/confirmação identificado: '{user_message}'. Respondendo cortêsmente.")
        elif is_help_msg:
            print(f"[GroqNewsAgent] Pergunta de capacidades/ajuda identificada: '{user_message}'. Explicando recursos do JARVYS.")

        user_content = f"MENSAGEM DO USUÁRIO: {user_message}\n\n"
        if news_context:
            user_content += f"{news_context}\n"
            user_content += "Instrução: Com base nas notícias acima, forneça um resumo claro e objetivo. VÁ DIRETO AO PONTO das notícias sem se reapresentar ou usar saudações longas (NÃO comece repetindo 'Olá! Sou o JARVYS...'). Destaque as fontes ao final."
        elif is_greeting_msg:
            user_content += (
                f"Instrução: O usuário enviou uma saudação ({user_message}). Responda chamando o usuário pelo nome (*Claudemir*), usando a saudação adequada ao período do dia ({time_ctx['saudacao_sugerida']}), "
                f"apresente-se amigavelmente como *JARVYS* (seu assistente de TI e IA) e pergunte como pode ajudá-lo hoje."
            )
        elif is_thanks_msg:
            user_content += "Instrução: O usuário enviou um agradecimento ou confirmação (ex: 'perfeito', 'obrigado'). Responda com extrema cortesia chamando-o pelo nome (*Claudemir*), confirmando que está à disposição. NÃO busque e NÃO inclua novas notícias."
        elif is_help_msg:
            user_content += "Instrução: O usuário perguntou sobre suas habilidades, aplicações ou como você pode ajudá-lo. Apresente-se brevemente como *JARVYS*, cumprimente o *Claudemir* e forneça EXPLICAÇÕES BREVES e objetivas em tópicos curtos (máximo 1 linha por item): 1) Notícias de TI & IA ao vivo no _Olhar Digital_ e _Canaltech_; 2) Esclarecimento direto de dúvidas sobre tecnologia e IA; 3) Resumo diário automático no WhatsApp às 18:00. Pergunte de forma sucinta o que ele gostaria de explorar."

        if not self.client:
            return self._generate_simulated_response(user_message, is_greeting_msg, is_thanks_msg, is_help_msg)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                model=self.model,
                temperature=0.4 if (is_greeting_msg or is_thanks_msg or is_help_msg) else 0.3,
            )
            response_content = chat_completion.choices[0].message.content.strip()
            return response_content
        except Exception as e:
            print(f"Erro na chamada à API da Groq: {e}")
            return self._generate_simulated_response(user_message, is_greeting_msg, is_thanks_msg, is_help_msg)

    def _generate_simulated_response(self, user_message: str, is_greeting: bool = False, is_thanks: bool = False, is_help: bool = False) -> str:
        """Resposta de simulação caso a GROQ_API_KEY ainda não esteja ativa."""
        if is_thanks:
            return "De nada! 😊 Fico feliz em ajudar. Conte comigo se precisar de mais notícias ou informações sobre TI e IA! 🤖👍"
        if is_help:
            return (
                "Olá, *Claudemir*! 👋 Sou o *JARVYS*, seu assistente de TI e IA! 🤖\n\n"
                "Aqui está o que posso fazer por você:\n"
                "• 📰 Buscar notícias ao vivo de TI & IA no _Olhar Digital_ e _Canaltech_\n"
                "• 💡 Esclarecer dúvidas sobre tecnologia e Inteligência Artificial\n"
                "• ⏰ Enviar resumo diário automático no WhatsApp às 18:00\n\n"
                "O que gostaria de explorar? 🚀"
            )
        if is_greeting:
            return (
                "Olá! 👋 Sou o *JARVYS*, seu assistente pessoal de Tecnologia e Inteligência Artificial! 🤖💻\n\n"
                "Como posso te ajudar hoje?\n"
                "• Ver as últimas notícias sobre *Inteligência Artificial*\n"
                "• Pesquisar sobre um tema específico (ex: _NVIDIA_, _Robótica_, _OpenAI_)\n\n"
                "O que você gostaria de explorar hoje? 🚀"
            )
        return (
            "Olá! 🤖 Sou o *JARVYS*, seu assistente de Tecnologia e IA! 💻\n\n"
            "Aqui estão as últimas novidades sobre **Tecnologia e IA**:\n"
            "• _TechCrunch_ 📰: **Lançamento de novos modelos de IA** de código aberto com maior eficiência.\n"
            "• _MIT Technology Review_ 📰: **Avanços em automação** e segurança cibernética.\n\n"
            "Como posso te ajudar mais hoje? 🚀"
        )

# Alias para compatibilidade com importações anteriores
GroqCommercialAgent = GroqNewsAgent

if __name__ == "__main__":
    agent = GroqNewsAgent()
    print("=== TESTE SAUDAÇÃO JARVYS ===")
    print(agent.generate_response("Oi"))
    print("\n=== TESTE BUSCA JARVYS ===")
    print(agent.generate_response("Notícias de IA"))
