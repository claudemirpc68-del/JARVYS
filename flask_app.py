import os
import threading
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

# Serviço Twilio para envio assíncrono via REST
twilio_service = TwilioService()


def _process_and_reply_async(incoming_msg: str, sender: str):
    """
    Processa a mensagem em background (Tavily + ML + Groq)
    e envia a resposta via REST Twilio, evitando o timeout de 15s do webhook.
    """
    try:
        print(f"[Flask Async] Processando mensagem de '{sender}': {incoming_msg}")
        fresh_agent = GroqNewsAgent()
        agent_reply = fresh_agent.generate_response(user_message=incoming_msg, use_search=True)
        print(f"[Flask Async] Resposta gerada ({len(agent_reply)} chars). Enviando via REST Twilio...")

        # Envia via REST Twilio para o remetente
        success = twilio_service.send_message(to_number=sender, body=agent_reply)
        if success:
            print(f"[Flask Async] ✅ Resposta enviada com sucesso para {sender}")
        else:
            print(f"[Flask Async] ❌ Falha ao enviar resposta para {sender}")
    except Exception as e:
        print(f"[Flask Async] ❌ Erro no processamento assíncrono: {e}")
        # Tenta enviar mensagem de erro ao usuário
        try:
            twilio_service.send_message(
                to_number=sender,
                body="⚠️ Desculpe, Claudemir! Ocorreu um erro ao processar sua solicitação. Tente novamente em alguns instantes. 🤖"
            )
        except Exception:
            pass


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


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """
    Endpoint Flask do Webhook Twilio -> Tavily Search -> Groq Agent -> WhatsApp.

    ESTRATÉGIA ANTI-TIMEOUT:
    O Twilio impõe um timeout de 15 segundos para webhooks.
    Como nosso pipeline (Tavily + ML + Groq) excede esse limite,
    respondemos IMEDIATAMENTE com TwiML vazio (HTTP 200) e processamos
    a mensagem em uma thread separada, enviando a resposta via REST.
    """
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    # Fallback para JSON payload
    if not incoming_msg and request.is_json:
        json_data = request.get_json()
        incoming_msg = json_data.get("message", "").strip()
        sender = json_data.get("user", "")

    print(f"\n[Flask WhatsApp] Mensagem recebida de '{sender}': {incoming_msg}")

    if not incoming_msg:
        incoming_msg = "Buscar notícias de TI e IA em canais confiáveis"

    # Verifica se temos credenciais Twilio válidas para envio REST assíncrono
    has_valid_twilio = (
        twilio_service.account_sid
        and twilio_service.auth_token
        and sender
    )

    if has_valid_twilio:
        # MODO ASSÍNCRONO: Responde TwiML vazio imediatamente e processa em background
        thread = threading.Thread(
            target=_process_and_reply_async,
            args=(incoming_msg, sender),
            daemon=True
        )
        thread.start()

        # Retorna TwiML vazio imediatamente (HTTP 200) para o Twilio não dar timeout
        empty_twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        return Response(empty_twiml, mimetype="text/xml")
    else:
        # MODO SÍNCRONO (fallback): Processa e responde diretamente via TwiML
        # Útil para testes locais ou quando Twilio REST não está configurado
        print("[Flask WhatsApp] Modo síncrono (sem Twilio REST). Processando inline...")
        fresh_agent = GroqNewsAgent()
        agent_reply = fresh_agent.generate_response(user_message=incoming_msg, use_search=True)
        print(f"[Flask WhatsApp] Resposta do Agente:\n{agent_reply}\n")

        if HAS_TWILIO_PACKAGE:
            twilio_resp = MessagingResponse()
            twilio_resp.message(agent_reply)
            return Response(str(twilio_resp), mimetype="text/xml")
        else:
            escaped_reply = escape(agent_reply)
            xml_response = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{escaped_reply}</Message></Response>'
            return Response(xml_response, mimetype="text/xml")


@app.route("/agent", methods=["POST"])
@app.route("/api/taviliy/agent", methods=["POST"])
def tavily_agent_endpoint():
    """
    Endpoint JSON do Agente (Tavily + Groq) para integração com outros serviços.
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
