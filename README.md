# 🤖 JARVYS - Agente de Notícias de Tecnologia & IA (WhatsApp)

O **JARVYS** é um assistente pessoal inteligente desenvolvido em **Python**, que realiza a busca ao vivo de notícias nos principais portais de tecnologia (**Olhar Digital** e **Canaltech**), sintetiza os resumos com o modelo **Llama 3.3 70B (Groq)** e entrega tudo formatado via **WhatsApp / Twilio**.

---

## 🚀 Funcionalidades Principais

- 🤖 **Persona JARVYS**: Atendimento cortês e inteligente com tratamento especial para saudações (*"Oi"*, *"Bom dia"*, etc.).
- 🌐 **Busca ao Vivo em Portais Focados**: Integração com **Tavily Search API** restrita a portais de alta credibilidade (`olhardigital.com.br` e `canaltech.com.br`).
- ⚡ **IA de Alta Performance**: Geração de resumos e respostas com **Groq API** (`llama-3.3-70b-versatile`).
- 💬 **Integração WhatsApp**: Webhook via **Flask / FastAPI** e serviço REST **Twilio**.
- ⏰ **Automação Diária (18:00)**: Script agendador ([daily_news_job.py](file:///c:/Users/FAMÍLIA/Desktop/ALLON%20HASHTAG/daily_news_job.py)) que realiza o raspagem e envio automático todos os dias às 18:00.

---

## 📁 Estrutura do Projeto

```text
ALLON HASHTAG/
├── prompt.py               # System Prompt e Persona do JARVYS
├── tavily_service.py       # Serviço de busca ao vivo de notícias (Tavily API)
├── groq_agent.py           # Agente IA (Groq Llama 3.3 70B)
├── twilio_service.py       # Serviço REST de envio via Twilio (WhatsApp/SMS)
├── flask_app.py            # Servidor Webhook Flask (Porta 5000)
├── server.py               # Servidor Webhook FastAPI (Porta 8000)
├── main.py                 # CLI principal de execução
├── daily_news_job.py       # Agendador da automação diária das 18:00
├── test_whatsapp_agent.py  # Bateria de testes do Webhook
├── test_advanced_features.py # Testes avançados de busca por tópicos e envio
├── .env                    # Variáveis de ambiente (Chaves de API) - Protegido pelo .gitignore
├── .env.example            # Exemplo de configuração de variáveis
├── .gitignore              # Proteção contra commit de dados sensíveis
└── README.md               # Documentação oficial do projeto
```

---

## ⚙️ Configuração do Ambiente (.env)

Crie o arquivo `.env` com as seguintes credenciais:

```env
# Configurações do Tavily (Busca de Notícias TI/IA)
TAVILY_API_KEY=tvly-sua_chave_tavily_aqui

# Configurações da API do Groq
GROQ_API_KEY=gsk_sua_chave_groq_aqui

# Configurações do Twilio (WhatsApp / SMS)
TWILIO_ACCOUNT_SID=seu_account_sid_aqui
TWILIO_AUTH_TOKEN=seu_auth_token_aqui
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
WHATSAPP_NUMBER=5511999999999
```

---

## 💻 Como Executar

### 1. Iniciar o Servidor Flask (WhatsApp Webhook)
```powershell
python main.py --flask
```

### 2. Expor o Servidor com Ngrok
```powershell
npx ngrok http 5000
```
Copie a URL HTTPS gerada (ex: `https://xxxx.ngrok-free.app/whatsapp`) e insira no painel do Twilio Sandbox (**Messaging > WhatsApp Sandbox Settings > WHEN A MESSAGE COMES IN**).

### 3. Iniciar a Automação Diária das 18:00
```powershell
python daily_news_job.py
```
*(Para testar o disparo imediatamente, use `python daily_news_job.py --now`)*.

---

## 🔒 Segurança

O arquivo [.gitignore](file:///c:/Users/FAMÍLIA/Desktop/ALLON%20HASHTAG/.gitignore) está configurado para **proibir** o envio de chaves de API e arquivos `.env` para o GitHub.
