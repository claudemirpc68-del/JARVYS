import os
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

# Domínios confiáveis alvos para busca de tecnologia
DEFAULT_TARGET_DOMAINS = ["olhardigital.com.br", "canaltech.com.br"]

class TavilyNewsService:
    def __init__(self, api_key: Optional[str] = None, target_domains: Optional[List[str]] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client = None
        self.target_domains = target_domains or DEFAULT_TARGET_DOMAINS

    def _ensure_client(self):
        """Garante que a chave de API e o cliente Tavily estejam atualizados."""
        load_dotenv(override=True)
        self.api_key = os.getenv("TAVILY_API_KEY")
        if self.api_key and not self.api_key.startswith("tvly-sua_chave"):
            if not self.client:
                try:
                    from tavily import TavilyClient
                    self.client = TavilyClient(api_key=self.api_key)
                    print(f"[TavilyNewsService] Cliente Tavily ativado! Domínios focados: {self.target_domains}")
                except Exception as e:
                    print(f"[TavilyNewsService] Erro ao inicializar TavilyClient: {e}")

    def search_news(self, query: str = "tecnologia e inteligência artificial", max_results: int = 5) -> str:
        """
        Busca notícias de TI e IA atualizadas especificamente nos portais configurados (ex: Olhar Digital, Canaltech).
        Retorna o contexto formatado em texto para ser injetado no LLM (Groq).
        """
        self._ensure_client()

        if not self.api_key or self.api_key.startswith("tvly-sua_chave"):
            print("[TavilyNewsService] Chave TAVILY_API_KEY não configurada. Usando modo simulado.")
            return self._get_simulated_news(query)

        print(f"[TavilyNewsService] Executando busca FOCADA ({self.target_domains}) para: '{query}'...")

        try:
            results = []
            
            # Tenta busca focada nos domínios alvos
            if self.client:
                try:
                    response = self.client.search(
                        query=f"{query} notícias tecnologia inteligência artificial",
                        topic="news",
                        include_domains=self.target_domains,
                        max_results=max_results,
                        search_depth="basic"
                    )
                    results = response.get("results", [])
                except Exception as ex_dom:
                    print(f"[TavilyNewsService] Aviso busca por domínios: {ex_dom}")

            # Fallback HTTP REST API se client não retornar nada
            if not results:
                url = "https://api.tavily.com/search"
                payload = {
                    "api_key": self.api_key,
                    "query": f"{query} notícias tecnologia inteligência artificial",
                    "topic": "news",
                    "include_domains": self.target_domains,
                    "max_results": max_results,
                    "search_depth": "basic"
                }
                res = requests.post(url, json=payload, timeout=10)
                if res.status_code == 200:
                    results = res.json().get("results", [])

            # Se a busca restrita aos domínios não retornar nada, faz busca aberta na Web como fallback
            if not results:
                print(f"[TavilyNewsService] Sem resultados específicos em {self.target_domains}. Efetuando busca geral na web...")
                if self.client:
                    response = self.client.search(query=query, topic="news", max_results=max_results)
                    results = response.get("results", [])

            if not results:
                print("[TavilyNewsService] Nenhum resultado retornado do Tavily.")
                return "Nenhuma notícia recente encontrada nos portais configurados para esta busca."

            news_context = f"NOTÍCIAS E ARTIGOS RECENTES EM TEMPO REAL (PORTAIS: {', '.join(self.target_domains)}):\n\n"
            for idx, item in enumerate(results, start=1):
                title = item.get("title", "Sem título")
                snippet = item.get("content", "Sem conteúdo")
                url = item.get("url", "")
                published_date = item.get("published_date", "")
                source = url.split("/")[2] if "//" in url else "Fonte Web"

                news_context += f"{idx}. TÍTULO: {title}\n"
                news_context += f"   FONTE/PORTAL: {source} ({published_date if published_date else 'recente'})\n"
                news_context += f"   RESUMO/TRECHO: {snippet}\n"
                news_context += f"   LINK: {url}\n\n"

            print(f"[TavilyNewsService] Busca concluída com sucesso. {len(results)} notícias encontradas.")
            return news_context

        except Exception as e:
            print(f"[TavilyNewsService] Exceção ao buscar notícias no Tavily: {e}")
            return self._get_simulated_news(query)

    def _get_simulated_news(self, query: str) -> str:
        """Retorna contexto simulado caso a TAVILY_API_KEY ainda não esteja configurada."""
        return (
            "NOTÍCIAS RECENTES ENCONTRADOS (PORTAIS: Olhar Digital, Canaltech):\n\n"
            "1. TÍTULO: Novidades e avanços em Inteligência Artificial no Brasil\n"
            "   FONTE/PORTAL: olhar-digital.com.br (2026)\n"
            "   RESUMO/TRECHO: Novos modelos de linguagem em português são lançados com alta precisão e baixo custo computacional.\n\n"
            "2. TÍTULO: Como a IA está transformando o setor de tecnologia nacional\n"
            "   FONTE/PORTAL: canaltech.com.br (2026)\n"
            "   RESUMO/TRECHO: Ferramentas de automação e segurança impulsionam a produtividade das empresas brasileiras.\n"
        )

if __name__ == "__main__":
    service = TavilyNewsService()
    print("=== TESTE TAVILY NEWS SERVICE (OLHAR DIGITAL & CANALTECH) ===")
    print(service.search_news("Inteligência Artificial"))
