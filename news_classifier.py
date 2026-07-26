import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from typing import List, Dict, Any

# Configura suporte a UTF-8 no console Windows
sys.stdout.reconfigure(encoding='utf-8')

class NewsClassifier:
    def __init__(self):
        # Dados de treino expandidos para cobrir o ecossistema de Tecnologia e IA
        self.noticias = [
            "Novo chip da NVIDIA acelera treinamento de IA",
            "Microsoft lança atualização crítica de segurança no Windows",
            "Apple apresenta novo MacBook com chip M3",
            "Pesquisadores avançam em modelos de linguagem generativa",
            "Hackers exploram falha em servidores Linux",
            "Google Cloud expande infraestrutura de data centers para IA",
            "Ataque de ransomware afeta sistemas de grandes empresas",
            "Intel anuncia novos processadores com NPU integrada",
            "OpenAI lança nova versão do ChatGPT com suporte a áudio",
            "Vazamento de dados expõe milhões de credenciais na web",
            "Amazon AWS lança novos serviços de nuvem gerenciada",
            "Meta lança modelo de código aberto Llama 3 para desenvolvedores",
            "Falha de segurança em biblioteca Python é corrigida",
            "AMD lança aceleradores de IA para superar concorrentes",
            "Desenvolvedores adotam novas ferramentas de IA para programação"
        ]
        
        self.categorias = [
            "Inteligência Artificial",
            "Segurança",
            "Hardware",
            "Inteligência Artificial",
            "Segurança",
            "Nuvem",
            "Segurança",
            "Hardware",
            "Inteligência Artificial",
            "Segurança",
            "Nuvem",
            "Inteligência Artificial",
            "Segurança",
            "Hardware",
            "Inteligência Artificial"
        ]

        # Vetorização e treinamento do modelo Naive Bayes
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        X = self.vectorizer.fit_transform(self.noticias)
        self.modelo = MultinomialNB()
        self.modelo.fit(X, self.categorias)

    def prever_categoria(self, texto_noticia: str) -> str:
        """Recebe o texto da notícia e retorna a categoria prevista."""
        if not texto_noticia:
            return "Geral"
        X_novo = self.vectorizer.transform([texto_noticia])
        return self.modelo.predict(X_novo)[0]

# Instância global do classificador
classifier = NewsClassifier()

def processar_noticias(noticias_raspadas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Recebe uma lista de dicionários contendo notícias e adiciona a chave 'categoria'
    com base na previsão do classificador Machine Learning.
    """
    noticias_processadas = []
    for noticia in noticias_raspadas:
        titulo = noticia.get("title") or noticia.get("titulo") or ""
        categoria = classifier.prever_categoria(titulo)
        
        item_processado = dict(noticia)
        item_processado["categoria"] = categoria
        noticias_processadas.append(item_processado)
        
    return noticias_processadas

if __name__ == "__main__":
    print("=== TESTE DO NEWS CLASSIFIER ===")
    test_items = [
        {"title": "Novo modelo de IA generativa revoluciona criação de vídeos", "url": "https://canaltech.com.br/ia1"},
        {"title": "Vulnerabilidade zero-day afeta navegadores web", "url": "https://olhardigital.com.br/sec1"},
        {"title": "Nova placa de vídeo para computação gráfica é lançada", "url": "https://canaltech.com.br/hw1"}
    ]
    
    resultado = processar_noticias(test_items)
    for r in resultado:
        print(f"📌 [{r['categoria']}] {r['title']} -> {r['url']}")
