import os
import sys
from flask import Flask, request, jsonify, Response
from groq_agent import GroqNewsAgent
from twilio_service import TwilioService
from dotenv import load_dotenv
from xml.sax.saxutils import escape

load_dotenv()

app = Flask(__name__)

# Tenta importar MessagingResponse do Twilio, com fallback para XML puro
try:
    from twilio.twiml.messaging_response import MessagingResponse
    HAS_TWILIO_PACKAGE = True
except ImportError:
    HAS_TWILIO_PACKAGE = False

twilio_service = TwilioService()


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "service": "JARVYS - Agente de Notícias TI & IA WhatsApp",
        "pipeline": "Twilio -> Tavily Search -> ML (Naive Bayes + KMeans) -> Groq LLM -> WhatsApp"
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check para monitoramento do Coolify."""
    return jsonify({"status": "healthy"}), 200


@app.route("/", methods=["POST"])
@app.route("/whatsapp", methods=["POST"])
@app.route("/webhook/twilio", methods=["POST"])
def whatsapp_webhook():
    """
    Endpoint do Webhook Twilio -> Tavily Search -> Groq Agent -> WhatsApp.
    Suporta as rotas /, /whatsapp e /webhook/twilio.
    Retorna TwiML síncrono com a resposta formatada para entrega imediata no WhatsApp.
    """
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    # Fallback para JSON payload
    if not incoming_msg and request.is_json:
        json_data = request.get_json() or {}
        incoming_msg = json_data.get("message", json_data.get("Body", "")).strip()
        sender = json_data.get("user", json_data.get("From", ""))

    print(f"\n[Flask WhatsApp] 📥 Mensagem recebida de '{sender}': {incoming_msg}")
    sys.stdout.flush()

    if not incoming_msg:
        incoming_msg = "Buscar notícias de TI e IA em canais confiáveis"

    # Processamento síncrono inline (Tavily + ML + Groq)
    try:
        fresh_agent = GroqNewsAgent()
        agent_reply = fresh_agent.generate_response(user_message=incoming_msg, use_search=True)
        print(f"[Flask WhatsApp] 🤖 Resposta do Agente gerada ({len(agent_reply)} chars):\n{agent_reply}\n")
        sys.stdout.flush()
    except Exception as e:
        print(f"[Flask WhatsApp] ❌ Erro ao gerar resposta: {e}")
        sys.stdout.flush()
        agent_reply = "⚠️ Desculpe, Claudemir! Ocorreu um erro ao processar sua mensagem. Tente novamente em instantes. 🤖"

    # Twilio aceita até 1600 caracteres por mensagem TwiML
    MAX_TWIML_CHARS = 1500

    if len(agent_reply) <= MAX_TWIML_CHARS:
        twiml_reply = agent_reply
    else:
        # Se for maior que 1500 chars, envia os primeiros 1500 via TwiML e o restante via REST
        twiml_reply = agent_reply[:MAX_TWIML_CHARS] + "\n...(continua)"
        remaining_reply = "(continuação)...\n" + agent_reply[MAX_TWIML_CHARS:]
        
        if sender and twilio_service.account_sid and twilio_service.auth_token:
            print(f"[Flask WhatsApp] 📤 Enviando parte 2 via REST Twilio para {sender}...")
            sys.stdout.flush()
            twilio_service.send_message(to_number=sender, body=remaining_reply)

    # Retorna resposta TwiML síncrona
    if HAS_TWILIO_PACKAGE:
        twilio_resp = MessagingResponse()
        twilio_resp.message(twiml_reply)
        return Response(str(twilio_resp), mimetype="text/xml")
    else:
        escaped_reply = escape(twiml_reply)
        xml_response = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped_reply}</Message></Response>'
        return Response(xml_response, mimetype="text/xml")


@app.route("/agent", methods=["POST"])
@app.route("/api/taviliy/agent", methods=["POST"])
def tavily_agent_endpoint():
    """
    Endpoint JSON do Agente (Tavily + Groq) para integração direta.
    """
    data = request.get_json(silent=True) or {}
    incoming_msg = data.get("message", "Notícias de TI e IA").strip()
    sender = data.get("user", "anonymous")

    fresh_agent = GroqNewsAgent()
    agent_reply = fresh_agent.generate_response(user_message=incoming_msg, use_search=True)

    return jsonify({
        "status": "success",
        "user": sender,
        "skill": data.get("skill", "news"),
        "reply": agent_reply
    })


if __name__ == "__main__":
    print("Iniciando servidor Flask na porta 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
