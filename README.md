# 🤖 JARVYS - Agente de Notícias de Tecnologia & IA (WhatsApp)

![Status](https://img.shields.io/badge/Status-Ativo%20%26%20Testado-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange)
![Tavily](https://img.shields.io/badge/Tavily-Live%20Search-purple)
![Twilio](https://img.shields.io/badge/Twilio-WhatsApp%20API-red)

O **JARVYS** é um assistente pessoal inteligente desenvolvido em **Python**, projetado para automatizar a busca ao vivo de notícias de tecnologia e Inteligência Artificial nos principais portais do Brasil (**Olhar Digital** e **Canaltech**). O sistema sintetiza os resumos em tempo real utilizando o modelo **Llama 3.3 70B (Groq)** e entrega tudo formatado diretamente via **WhatsApp / Twilio**.

---

## 🏗️ Arquitetura do Sistema

```text
[ Usuário (WhatsApp) ]
          │
          ▼
[ Twilio Sandbox Cloud ]
          │
          ▼ (Webhook HTTPS via Ngrok)
[ Servidor Flask / FastAPI (Porta 5000 / 8000) ]
          │
          ├─► [ Tavily Search API ] (Busca focada em olhardigital.com.br & canaltech.com.br)
          │
          └─► [ Groq LLM API ] (Modelo llama-3.3-70b-versatile + Persona JARVYS)
          │
          ▼
[ Resposta Formatada em TwiML XML / Envio Direct REST ]
```

---

## 🚀 Funcionalidades Principais

- 🤖 **Persona JARVYS**: Atendimento cortês, inteligente e humano, com tratamento especial para saudações (*"Oi"*, *"Bom dia"*, etc.) e respostas estruturadas com emojis e markdown do WhatsApp.
- 🌐 **Busca ao Vivo Focada**: Integração com a **Tavily Search API** restrita a portais de alta credibilidade (`olhardigital.com.br` e `canaltech.com.br`).
- ⚡ **IA de Alta Performance**: Resumos gerados em milissegundos via **Groq API** utilizando o modelo `llama-3.3-70b-versatile`.
- 💬 **Integração WhatsApp Webhook**: Suporte completo a **Flask (porta 5000)** e **FastAPI (porta 8000)** gerando respostas nativas **TwiML XML**.
- ⏰ **Automação Diária (18:00)**: Script agendador ([daily_news_job.py](file:///c:/Users/FAMÍLIA/Desktop/ALLON%20HASHTAG/daily_news_job.py)) que realiza a busca e envio automático todos os dias às 18:00 para o número configurado.
- 🧪 **Bateria de Testes Automatizados**: Scripts prontos para validação de pipeline CLI, testes de carga no webhook e disparo direto via API REST.

---

## 📁 Estrutura do Projeto

```text
JARVYS/
├── prompt.py                 # System Prompt e Persona do JARVYS
├── tavily_service.py         # Serviço de busca ao vivo de notícias (Tavily API)
├── groq_agent.py             # Agente IA (Groq Llama 3.3 70B)
├── twilio_service.py         # Serviço REST de envio via Twilio (WhatsApp/SMS)
├── flask_app.py              # Servidor Webhook Flask (Porta 5000)
├── server.py                 # Servidor Webhook FastAPI (Porta 8000)
├── main.py                   # CLI principal de execução do projeto
├── daily_news_job.py         # Agendador da automação diária das 18:00 (--now para teste imediato)
├── test_whatsapp_agent.py    # Bateria de testes automatizados do Webhook
├── test_advanced_features.py # Testes avançados de busca por tópicos e envio ativo
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
WHATSAPP_NUMBER=5511961909818
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

---

## 🔒 Segurança & Governança

- O repositório utiliza proteção estrita via [.gitignore](file:///c:/Users/FAMÍLIA/Desktop/ALLON%20HASHTAG/.gitignore) para prevenir qualquer vazamento acidental de tokens e chaves privadas (`.env`, logs e chaves de API).
- Todas as mensagens enviadas seguem a política de privacidade e conformidade com LGPD para assistentes virtuais automatizados.
