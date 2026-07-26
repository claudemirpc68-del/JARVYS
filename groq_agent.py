import os
from typing import Optional
from dotenv import load_dotenv
from prompt import get_system_prompt
from tavily_service import TavilyNewsService

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
        """Verifica se a mensagem é uma saudação simples."""
        msg = message.strip().lower().strip(".!😊👍🙏")
        greetings = [
            "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", 
            "tudo bem", "tudo bem?", "fala jarvys", "hey", "hello", 
            "salve", "oie", "opa", "start", "iniciar", "menu"
        ]
        return msg in greetings or any(msg == g for g in greetings)

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

    def generate_response(self, user_message: str, use_search: bool = True) -> str:
        """
        Gera a resposta do Agente JARVYS via Tavily + Groq API para WhatsApp / SMS.
        """
        system_prompt = get_system_prompt()
        is_greeting_msg = self._is_greeting(user_message)
        is_thanks_msg = self._is_thanks_or_confirmation(user_message)
        is_help_msg = self._is_help_or_capabilities(user_message)

        news_context = ""
        # Só executa busca se NÃO for saudação, agradecimento ou dúvida de capacidades
        if use_search and not is_greeting_msg and not is_thanks_msg and not is_help_msg:
            print(f"[GroqNewsAgent] Pesquisando notícias no Tavily sobre: '{user_message}'...")
            news_context = self.tavily_service.search_news(user_message)
        elif is_greeting_msg:
            print(f"[GroqNewsAgent] Saudação identificada: '{user_message}'. Respondendo com recepção do JARVYS.")
        elif is_thanks_msg:
            print(f"[GroqNewsAgent] Agradecimento/confirmação identificado: '{user_message}'. Respondendo cortêsmente.")
        elif is_help_msg:
            print(f"[GroqNewsAgent] Pergunta de capacidades/ajuda identificada: '{user_message}'. Explicando recursos do JARVYS.")

        user_content = f"MENSAGEM DO USUÁRIO: {user_message}\n\n"
        if news_context:
            user_content += f"{news_context}\n"
            user_content += "Instrução: Com base nas notícias acima, forneça um resumo claro e objetivo. VÁ DIRETO AO PONTO das notícias sem se reapresentar ou usar saudações longas (NÃO comece repetindo 'Olá! Sou o JARVYS...'). Destaque as fontes ao final."
        elif is_greeting_msg:
            user_content += "Instrução: Responda a saudação do usuário com entusiasmo, apresente-se como *JARVYS* (seu assistente de TI e IA) e pergunte como pode ajudar hoje."
        elif is_thanks_msg:
            user_content += "Instrução: O usuário enviou um agradecimento ou confirmação (ex: 'perfeito', 'obrigado'). Responda com extrema cortesia, confirmando que está à disposição. NÃO busque e NÃO inclua novas notícias."
        elif is_help_msg:
            user_content += "Instrução: O usuário perguntou sobre suas habilidades, aplicações ou como você pode ajudá-lo. Apresente-se brevemente como *JARVYS* e forneça EXPLICAÇÕES BREVES e objetivas em tópicos curtos (máximo 1 linha por item): 1) Notícias de TI & IA ao vivo no _Olhar Digital_ e _Canaltech_; 2) Esclarecimento direto de dúvidas sobre tecnologia e IA; 3) Resumo diário automático no WhatsApp às 18:00. Pergunte de forma sucinta o que ele gostaria de explorar."

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

    def _generate_simulated_response(self, user_message: str, is_greeting: bool = False, is_thanks: bool = False) -> str:
        """Resposta de simulação caso a GROQ_API_KEY ainda não esteja ativa."""
        if is_thanks:
            return "De nada! 😊 Fico feliz em ajudar. Conte comigo se precisar de mais notícias ou informações sobre TI e IA! 🤖👍"
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
