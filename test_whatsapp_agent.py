import sys
import requests
import xml.etree.ElementTree as ET

# Garante suporte a UTF-8 no terminal Windows
sys.stdout.reconfigure(encoding='utf-8')

SERVER_URL = "http://localhost:5000/whatsapp"

def run_whatsapp_test(pergunta: str):
    print("=" * 70)
    print(f"📱 ENVIANDO MENSAGEM SIMULADA DO WHATSAPP:")
    print(f"   Pergunta: \"{pergunta}\"")
    print("=" * 70)

    payload = {
        "Body": pergunta,
        "From": "whatsapp:+5511999999999"
    }

    try:
        response = requests.post(SERVER_URL, data=payload, timeout=30)
        print(f"Status HTTP: {response.status_code}")

        if response.status_code == 200:
            print("\n📥 RESPOSTA RECEBIDA DO JARVYS (TWIML XML):")
            print("-" * 50)
            
            # Tenta extrair a mensagem dentro da tag <Message>
            try:
                root = ET.fromstring(response.text)
                msg_body = root.find("Message").text
                print(msg_body)
            except Exception:
                print(response.text)

            print("-" * 50)
            print("✅ TESTE CONCLUÍDO COM SUCESSO!\n")
        else:
            print(f"❌ Erro ao chamar webhook: Status {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Exceção ao conectar no servidor: {e}")

def main():
    print("\n🚀 INICIANDO BATERIA DE TESTES AUTOMATIZADOS NO JARVYS (FLASK + TAVILY + GROQ)\n")

    testes = [
        "Quais as novidades sobre modelos de código aberto em IA?",
        "Últimas notícias sobre segurança cibernética e inteligência artificial",
        "O que há de novo sobre robótica e automação no setor de TI?"
    ]

    for idx, pergunta in enumerate(testes, start=1):
        print(f"\n--- EXECUÇÃO DO TESTE {idx} de {len(testes)} ---")
        run_whatsapp_test(pergunta)

if __name__ == "__main__":
    main()
