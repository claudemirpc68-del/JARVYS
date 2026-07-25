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
        msg = message.strip().lower()
        greetings = [
            "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", 
            "tudo bem", "tudo bem?", "fala jarvys", "hey", "hello", 
            "salve", "oie", "opa", "ajuda", "start", "iniciar", "menu"
        ]
        return msg in greetings or any(msg == g for g in greetings)

    def generate_response(self, user_message: str, use_search: bool = True) -> str:
        """
        Gera a resposta do Agente JARVYS via Tavily + Groq API para WhatsApp / SMS.
        """
        system_prompt = get_system_prompt()
        is_greeting_msg = self._is_greeting(user_message)

        news_context = ""
        # Só executa busca se NÃO for uma simples saudação
        if use_search and not is_greeting_msg:
            print(f"[GroqNewsAgent] Pesquisando notícias no Tavily sobre: '{user_message}'...")
            news_context = self.tavily_service.search_news(user_message)
        elif is_greeting_msg:
            print(f"[GroqNewsAgent] Saudação identificada: '{user_message}'. Respondendo com recepção calorosa do JARVYS.")

        user_content = f"MENSAGEM DO USUÁRIO: {user_message}\n\n"
        if news_context:
            user_content += f"{news_context}\n"
            user_content += "Instrução: Com base nas notícias acima, forneça um resumo claro, amigável e resumido formatado para WhatsApp destacando as fontes."
        elif is_greeting_msg:
            user_content += "Instrução: Responda a saudação do usuário com entusiasmo, apresente-se como *JARVYS* (seu assistente de Tecnologia e IA) e pergunte como pode ajudar hoje ou se ele deseja ver as últimas notícias de Inteligência Artificial e TI."

        if not self.client:
            return self._generate_simulated_response(user_message, is_greeting_msg)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                model=self.model,
                temperature=0.4 if is_greeting_msg else 0.3,
            )
            response_content = chat_completion.choices[0].message.content.strip()
            return response_content
        except Exception as e:
            print(f"Erro na chamada à API da Groq: {e}")
            return self._generate_simulated_response(user_message, is_greeting_msg)

    def _generate_simulated_response(self, user_message: str, is_greeting: bool = False) -> str:
        """Resposta de simulação caso a GROQ_API_KEY ainda não esteja ativa."""
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
