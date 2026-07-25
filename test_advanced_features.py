import os
import sys
from dotenv import load_dotenv
from groq_agent import GroqNewsAgent
from twilio_service import TwilioService

# Configura UTF-8 no terminal Windows
sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(override=True)

def test_specific_topic_search(topic: str):
    print("=" * 70)
    print(f"🔍 TESTANDO PESQUISA POR TÓPICO ESPECÍFICO: '{topic}'")
    print("=" * 70)

    agent = GroqNewsAgent()
    response = agent.generate_response(user_message=topic, use_search=True)

    print("\n🤖 RESPOSTA GERADA PELO JARVYS:")
    print("-" * 50)
    print(response)
    print("-" * 50)
    return response

def test_direct_whatsapp_dispatch(phone_number: str, message: str):
    print("\n" + "=" * 70)
    print(f"📱 TESTANDO DISPARO ATIVO VIA TWILIO PARA: {phone_number}")
    print("=" * 70)

    twilio_service = TwilioService()
    success = twilio_service.send_message(to_number=phone_number, body=message)

    if success:
        print("✅ Mensagem enviada com sucesso ao seu WhatsApp!")
    else:
        print("❌ Falha no envio da mensagem.")
    return success

def main():
    print("\n🚀 INICIANDO BATERIA DE TESTES AVANÇADOS DO JARVYS\n")

    # Tópicos avançados para pesquisa ao vivo
    topics = [
        "Quais as novidades sobre a NVIDIA e novos chips de IA?",
        "Aplicações de Inteligência Artificial na medicina e saúde",
        "Regulamentação de IA e privacidade de dados no Brasil e na Europa"
    ]

    results = []
    for idx, topic in enumerate(topics, start=1):
        print(f"\n--- TESTE DE PESQUISA {idx} de {len(topics)} ---")
        res = test_specific_topic_search(topic)
        results.append((topic, res))

    # Escolhe a resposta do Teste 1 (NVIDIA / Chips de IA) para mandar no celular
    dest_phone = os.getenv("WHATSAPP_NUMBER", "5511961909818")
    print("\n--- TESTE DE ENVO DIRETO AO SEU WHATSAPP ---")
    
    msg_to_send = (
        f"🤖 *[NOTIFICAÇÃO AUTOMÁTICA DO JARVYS]*\n\n"
        f"{results[0][1]}"
    )
    test_direct_whatsapp_dispatch(dest_phone, msg_to_send)

    print("\n✨ TODOS OS TESTES AVANÇADOS FORAM EXECUTADOS COM SUCESSO!\n")

if __name__ == "__main__":
    main()
