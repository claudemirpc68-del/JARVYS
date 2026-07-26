# 🤖 JARVYS - Agente de Notícias de Tecnologia & IA (WhatsApp)

![Status](https://img.shields.io/badge/Status-Ativo%20%26%20Testado-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange)
![Tavily](https://img.shields.io/badge/Tavily-Live%20Search-purple)
![Twilio](https://img.shields.io/badge/Twilio-WhatsApp%20API-red)
![Deploy](https://img.shields.io/badge/Deploy-Coolify%20Docker-blueviolet)

O **JARVYS** é um assistente pessoal inteligente desenvolvido em **Python**, projetado para automatizar a busca ao vivo de notícias de tecnologia e Inteligência Artificial nos principais portais do Brasil (**Olhar Digital** e **Canaltech**). O sistema sintetiza os resumos em tempo real utilizando o modelo **Llama 3.3 70B (Groq)** e entrega tudo formatado diretamente via **WhatsApp / Twilio**.

---

## 🏗️ Arquitetura do Sistema

```text
[ Usuário (WhatsApp) ]
          │
          ▼
[ Twilio Sandbox Cloud ]
          │
          ▼ (Webhook HTTPS via Coolify / Ngrok)
[ Servidor Flask + Gunicorn (Porta 5000) ]
          │
          ├─► [ Tavily Search API ] (Busca focada em olhardigital.com.br & canaltech.com.br)
          │
          ├─► [ ML Pipeline ] (TF-IDF + Naive Bayes + KMeans Clustering)
          │
          └─► [ Groq LLM API ] (Modelo llama-3.3-70b-versatile + Persona JARVYS)
          │
          ▼
[ Resposta Assíncrona via REST Twilio (Anti-Timeout) ]
```

---

## 🚀 Funcionalidades Principais

- 🤖 **Persona JARVYS**: Atendimento cortês, inteligente e humano, com tratamento especial para saudações (*"Oi"*, *"Bom dia"*, etc.) e respostas estruturadas com emojis e markdown do WhatsApp.
- 🌐 **Busca ao Vivo Focada**: Integração com a **Tavily Search API** restrita a portais de alta credibilidade (`olhardigital.com.br` e `canaltech.com.br`).
- ⚡ **IA de Alta Performance**: Resumos gerados em milissegundos via **Groq API** utilizando o modelo `llama-3.3-70b-versatile`.
- 💬 **Integração WhatsApp Webhook**: Suporte completo a **Flask (porta 5000)** e **FastAPI (porta 8000)** gerando respostas nativas **TwiML XML**.
- 🔄 **Modo Assíncrono Anti-Timeout**: O webhook responde imediatamente ao Twilio (dentro do limite de 15s) e processa a mensagem em background, enviando a resposta via REST Twilio de forma assíncrona.
- 🧠 **Pipeline de Machine Learning**: Classificação automática de notícias via **TF-IDF + Naive Bayes** (supervisionado) e agrupamento via **KMeans Clustering** (não supervisionado).
- ⏰ **Automação Diária (18:00)**: Script agendador (`daily_news_job.py`) que realiza a busca e envio automático todos os dias às 18:00 para o número configurado.
- 🧪 **Bateria de Testes Automatizados**: Scripts prontos para validação de pipeline CLI, testes de carga no webhook e disparo direto via API REST.
- 📋 **Comandos Slash**: `/noticias`, `/diario`, `/status`, `/limpar`, `/ajuda` — comandos rápidos diretamente no WhatsApp.

---

## 📁 Estrutura do Projeto

```text
JARVYS/
├── flask_app.py              # Servidor Webhook Flask (Porta 5000) com modo assíncrono
├── server.py                 # Servidor Webhook FastAPI (Porta 8000)
├── main.py                   # CLI principal de execução do projeto
├── prompt.py                 # System Prompt e Persona do JARVYS
├── groq_agent.py             # Agente IA (Groq Llama 3.3 70B) com detecção inteligente de intenção
├── tavily_service.py         # Serviço de busca ao vivo de notícias (Tavily API)
├── twilio_service.py         # Serviço REST de envio via Twilio (WhatsApp/SMS)
├── greeting_skill.py         # Skill de saudação inteligente com contexto temporal (UTC-3)
├── ml_pipeline.py            # Pipeline de ML (Supervisionado Naive Bayes + Clustering KMeans)
├── news_classifier.py        # Classificador de notícias via TF-IDF + Naive Bayes
├── daily_news_job.py         # Agendador da automação diária das 18:00 (--now para teste imediato)
├── test_whatsapp_agent.py    # Bateria de testes automatizados do Webhook
├── test_advanced_features.py # Testes avançados de busca por tópicos e envio ativo
├── verify_all_stages.py      # Script de validação completa de todas as etapas
├── Dockerfile                # Container Docker (Python 3.11-slim + Gunicorn)
├── entrypoint.sh             # Script de inicialização do container (Gunicorn + Agendador)
├── requirements.txt          # Dependências Python do projeto
├── .env                      # Variáveis de ambiente (Chaves de API) - Protegido pelo .gitignore
├── .env.example              # Modelo para configuração das variáveis de ambiente
├── .gitignore                # Regras de segurança para impedir commit de credenciais
└── README.md                 # Documentação oficial do projeto
```

---

## ⚙️ Configuração do Ambiente (.env)

Certifique-se de que o arquivo `.env` contenha as chaves de API necessárias:

```env
# Configurações do Tavily (Busca de Notícias TI/IA)
TAVILY_API_KEY=tvly-sua_chave_tavily_aqui

# Configurações da API do Groq
GROQ_API_KEY=gsk_sua_chave_groq_aqui

# Configurações do Twilio (WhatsApp / SMS)
TWILIO_ACCOUNT_SID=AC_seu_account_sid_aqui
TWILIO_AUTH_TOKEN=seu_auth_token_aqui
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
WHATSAPP_NUMBER=5511999999999
```

---

## 💻 Como Executar o Projeto

### 1. Iniciar o Servidor Webhook (Flask na Porta 5000)
```powershell
python main.py --flask
```

### 2. Expor o Servidor Local via Ngrok
Em um terminal paralelo, execute:
```powershell
npx ngrok http 5000
```
Copie a URL HTTPS gerada (exemplo: `https://xxxx.ngrok-free.app/whatsapp`) e insira no painel da Twilio Sandbox:
> **Console Twilio > Messaging > Settings > WhatsApp Sandbox Settings > WHEN A MESSAGE COMES IN**

### 3. Iniciar o Agendador de Notícias Diárias (18:00)
```powershell
python daily_news_job.py
```
*(Para testar o disparo direto imediatamente no seu celular, execute: `python daily_news_job.py --now`)*

---

## 🐳 Deploy com Docker (Coolify)

O projeto inclui um `Dockerfile` pronto para deploy em servidores como **Coolify**, **Railway** ou qualquer plataforma Docker:

```powershell
# Build local
docker build -t jarvys .

# Executar
docker run -p 5000:5000 --env-file .env jarvys
```

No **Coolify**, basta apontar o repositório GitHub e configurar as variáveis de ambiente no painel. O container:
- Inicia o **Gunicorn** (2 workers) na porta 5000
- Ativa o **agendador diário** em background automaticamente
- Expõe o endpoint `/health` para monitoramento de saúde

---

## 🔄 Modo Assíncrono (Anti-Timeout Twilio)

O Twilio impõe um **timeout de 15 segundos** para webhooks. Como o pipeline completo do JARVYS (Tavily + ML + Groq) pode exceder esse limite, o sistema utiliza uma estratégia de **resposta assíncrona**:

1. O webhook recebe a mensagem do WhatsApp
2. Responde **imediatamente** com TwiML vazio (HTTP 200) para o Twilio
3. Processa a mensagem em uma **thread separada** (Tavily → ML → Groq)
4. Envia a resposta final via **REST Twilio** diretamente para o usuário

Isso garante que o bot **nunca fica mudo** por timeout.

---

## 🧪 Bateria de Testes Automatizados

Para testar a inteligência do bot e a integridade dos webhooks sem depender do celular:

- **Teste CLI de Pergunta (Simulação)**:
  ```powershell
  python main.py --test "Quais as últimas notícias de Inteligência Artificial?"
  ```

- **Teste Automatizado no Servidor Webhook (Flask)**:
  ```powershell
  python test_whatsapp_agent.py
  ```

- **Teste de Envio Ativo e Recursos Avançados**:
  ```powershell
  python test_advanced_features.py
  ```

- **Validação Completa de Todas as Etapas**:
  ```powershell
  python verify_all_stages.py
  ```

---

## 📋 Comandos Slash (WhatsApp)

| Comando | Descrição |
|---------|-----------|
| `/noticias` | Busca notícias de TI e IA ao vivo no Olhar Digital e Canaltech |
| `/diario` | Receba o resumo executivo das principais novidades de hoje |
| `/limpar` | Reseta o contexto de conversa |
| `/status` | Verifica o status do servidor e da infraestrutura |
| `/ajuda` | Exibe o menu de comandos rápidos |

---

## 🔒 Segurança & Governança

- O repositório utiliza proteção estrita via `.gitignore` para prevenir qualquer vazamento acidental de tokens e chaves privadas (`.env`, logs e chaves de API).
- Todas as mensagens enviadas seguem a política de privacidade e conformidade com LGPD para assistentes virtuais automatizados.
- O system prompt inclui **blindagem contra prompt injection** — o JARVYS nunca revela código-fonte, chaves de API ou modifica sua persona.

---

## 🛠️ Stack Tecnológico

| Tecnologia | Uso |
|------------|-----|
| Python 3.10+ | Linguagem principal |
| Flask + Gunicorn | Servidor webhook de produção |
| FastAPI + Uvicorn | Servidor alternativo |
| Groq API | LLM (Llama 3.3 70B Versatile) |
| Tavily Search API | Busca de notícias ao vivo |
| Twilio API | Integração WhatsApp/SMS |
| Scikit-Learn | ML (TF-IDF, Naive Bayes, KMeans) |
| Docker | Containerização para deploy |
| Coolify | Plataforma de deploy em nuvem |
