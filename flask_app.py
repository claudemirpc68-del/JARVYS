from flask import Flask, request, jsonify, Response
from groq_agent import GroqNewsAgent
from dotenv import load_dotenv
from xml.sax.saxutils import escape

load_dotenv()

app = Flask(__name__)
agent = GroqNewsAgent()

# Tenta importar MessagingResponse do Twilio, com fallback para XML puro
try:
    from twilio.twiml.messaging_response import MessagingResponse
    HAS_TWILIO_PACKAGE = True
except ImportError:
    HAS_TWILIO_PACKAGE = False

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "service": "Servidor Flask - Agente de Notícias TI & IA WhatsApp"
    })

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """
    Endpoint Flask do Webhook Twilio -> Tavily Search -> Groq Agent -> WhatsApp
    """
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    if not incoming_msg and request.is_json:
        json_data = request.get_json()
        incoming_msg = json_data.get("message", "").strip()
        sender = json_data.get("user", "")

    print(f"\n[Flask WhatsApp] Mensagem recebida de '{sender}': {incoming_msg}")

    if not incoming_msg:
        incoming_msg = "Buscar notícias de TI e IA em canais confiáveis"

    # Instancia agente dinamicamente por requisição para garantir busca ao vivo
    fresh_agent = GroqNewsAgent()
    agent_reply = fresh_agent.generate_response(user_message=incoming_msg, use_search=True)
    print(f"[Flask WhatsApp] Resposta do Agente:\n{agent_reply}\n")

    # Se o pacote twilio estiver instalado, usa MessagingResponse
    if HAS_TWILIO_PACKAGE:
        twilio_resp = MessagingResponse()
        twilio_resp.message(agent_reply)
        return str(twilio_resp)
    else:
        # Fallback TwiML XML nativo (não requer o pacote 'twilio')
        escaped_reply = escape(agent_reply)
        xml_response = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>{escaped_reply}</Message></Response>"
        return Response(xml_response, mimetype="text/xml")

@app.route("/agent", methods=["POST"])
@app.route("/api/taviliy/agent", methods=["POST"])
def tavily_agent_endpoint():
    """
    Endpoint JSON do Agente (Taviliy/Tavily + Groq)
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
