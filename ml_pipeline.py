import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.cluster import KMeans
from typing import List, Dict, Any

# Suporte a UTF-8 no Windows
sys.stdout.reconfigure(encoding='utf-8')

class MLPipeline:
    def __init__(self, n_clusters: int = 3):
        self.n_clusters = n_clusters

        # Dados de treino supervisionado expandidos
        self.noticias_treino = [
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
        
        self.categorias_treino = [
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

        # Vetorizador TF-IDF compartilhado
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))

        # Treino supervisionado (Naive Bayes)
        X = self.vectorizer.fit_transform(self.noticias_treino)
        self.classificador = MultinomialNB()
        self.classificador.fit(X, self.categorias_treino)

    def processar(self, noticias_raspadas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recebe lista de notícias raspadas e retorna com categoria (supervisionada) e cluster (não supervisionada)"""
        if not noticias_raspadas:
            return []

        titulos = [n.get("title") or n.get("titulo") or "" for n in noticias_raspadas]

        # Vetorizar todas as notícias recebidas
        X_todas = self.vectorizer.transform(titulos)

        # 1. Predição supervisionada (Categoria)
        categorias_previstas = self.classificador.predict(X_todas)

        # 2. Agrupamento não supervisionado (KMeans)
        # Ajusta número de clusters caso a quantidade de notícias seja menor que n_clusters
        effective_clusters = max(1, min(self.n_clusters, len(titulos)))
        kmeans = KMeans(n_clusters=effective_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_todas)

        # Montar resultado
        noticias_processadas = []
        for i, noticia in enumerate(noticias_raspadas):
            item = dict(noticia)
            item["categoria"] = str(categorias_previstas[i])
            item["cluster"] = int(clusters[i])
            noticias_processadas.append(item)

        return noticias_processadas

if __name__ == "__main__":
    print("=== TESTE DO ML PIPELINE (SUPERVISIONADO + KMEANS CLUSTERING) ===")
    test_noticias = [
        {"title": "Google lança novo modelo Gemini Ultra para desenvolvedores", "url": "https://canaltech.com.br/ia1"},
        {"title": "Vulnerabilidade em servidores Linux expõe senhas corporativas", "url": "https://olhardigital.com.br/sec1"},
        {"title": "NVIDIA lança GPUs H200 com maior largura de banda para servidores", "url": "https://canaltech.com.br/hw1"},
        {"title": "Novo ransomware ataca bancos e exige resgate em Bitcoin", "url": "https://olhardigital.com.br/sec2"},
        {"title": "OpenAI atualiza ChatGPT com busca em tempo real na web", "url": "https://canaltech.com.br/ia2"}
    ]

    pipeline = MLPipeline(n_clusters=3)
    resultado = pipeline.processar(test_noticias)

    for n in resultado:
        print(f"📰 [{n['categoria']}] (Cluster {n['cluster']}) -> {n['title']}")
