from fastapi import FastAPI, Form, Request, Response
from typing import Optional
from dotenv import load_dotenv
from groq_agent import GroqNewsAgent
from twilio_service import TwilioService
from tavily_service import TavilyNewsService
from xml.sax.saxutils import escape

load_dotenv()

app = FastAPI(title="Agente de Notícias TI & IA WhatsApp (Twilio + Tavily + Groq)")

agent = GroqNewsAgent()
twilio_service = TwilioService()
tavily_service = TavilyNewsService()

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Agente de Notícias TI & IA (WhatsApp / SMS)",
        "pipeline": "Twilio -> Tavily Search -> Groq (Llama 3.3 70B) -> WhatsApp"
    }

@app.post("/webhook/twilio")
@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Endpoint de Webhook para o Twilio (WhatsApp / SMS).
    Suporta requisições Form Data (Twilio) e gera resposta TwiML + envio REST.
    """
    form_data = await request.form()
    incoming_msg = form_data.get("Body", "").strip() if form_data else ""
    sender = form_data.get("From", "") if form_data else ""

    # Se não veio via Form, tenta JSON payload
    if not incoming_msg:
        try:
            json_data = await request.json()
            incoming_msg = json_data.get("message", json_data.get("Body", "")).strip()
            sender = json_data.get("user", json_data.get("From", ""))
        except Exception:
            pass

    print(f"\n[WhatsApp Webhook] Mensagem recebida de '{sender}': {incoming_msg}")

    if not incoming_msg:
        incoming_msg = "Quais as principais notícias de TI e Inteligência Artificial de hoje?"

    # Processa via Tavily + Groq LLM
    agent_reply = agent.generate_response(user_message=incoming_msg, use_search=True)
    print(f"[WhatsApp Webhook] Resposta do Agente:\n{agent_reply}\n")

    # Tenta enviar via REST Twilio se houver sender e número configurado
    if sender and twilio_service.account_sid and not twilio_service.account_sid.startswith("AC99aa2c72ab7b9"):
        twilio_service.send_message(to_number=sender, body=agent_reply)

    # Retorna resposta TwiML formatada para o Twilio
    escaped_reply = escape(agent_reply)
    twiml_content = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>{escaped_reply}</Message></Response>"
    return Response(content=twiml_content, media_type="application/xml")

@app.post("/agent")
@app.post("/api/taviliy/agent")
async def tavily_agent_api(request: Request):
    """
    Endpoint de API REST direta para integração com agentes ou outros serviços.
    """
    json_data = await request.json()
    user_msg = json_data.get("message", "Notícias recentes de TI e IA").strip()
    
    agent_reply = agent.generate_response(user_message=user_msg, use_search=True)
    return {
        "status": "success",
        "user": json_data.get("user", "anonymous"),
        "skill": json_data.get("skill", "news"),
        "reply": agent_reply
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
