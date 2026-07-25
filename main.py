import sys
import argparse

# Garante suporte completo a UTF-8 no terminal Windows
sys.stdout.reconfigure(encoding='utf-8')

from groq_agent import GroqNewsAgent

def main():
    parser = argparse.ArgumentParser(description="Agente de Notícias TI & IA WhatsApp (Twilio + Tavily + Groq)")
    parser.add_argument("--test", type=str, help="Simula uma pergunta de usuário no terminal com busca Tavily")
    parser.add_argument("--server", action="store_true", help="Inicia o servidor FastAPI na porta 8000")
    parser.add_argument("--flask", action="store_true", help="Inicia o servidor Flask na porta 5000")
    
    args = parser.parse_args()

    if args.server:
        import uvicorn
        print("Iniciando o servidor FastAPI (Twilio + Tavily + Groq) na porta 8000...")
        uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
    elif args.flask:
        from flask_app import app
        print("Iniciando o servidor Flask (Twilio + Tavily + Groq) na porta 5000...")
        app.run(host="0.0.0.0", port=5000, debug=True)
    elif args.test:
        print(f"\n--- SIMULANDO PIPELINE: TWILIO -> TAVILY -> GROQ -> WHATSAPP ---")
        print(f"Usuário perguntou: \"{args.test}\"\n")
        agent = GroqNewsAgent()
        response = agent.generate_response(args.test, use_search=True)
        print("Resposta Gerada pelo Agente:")
        print("--------------------------------------------------")
        print(response)
        print("--------------------------------------------------\n")
    else:
        print("Uso:")
        print("  Simular teste no terminal:")
        print("    python main.py --test \"Notícias de IA de hoje\"")
        print("\n  Iniciar servidor FastAPI (Porta 8000):")
        print("    python main.py --server")
        print("\n  Iniciar servidor Flask (Porta 5000):")
        print("    python main.py --flask")

if __name__ == "__main__":
    main()
