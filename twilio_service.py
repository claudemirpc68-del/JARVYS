import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class TwilioService:
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = from_number or os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        self.api_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json" if self.account_sid else ""

    def send_message(self, to_number: str, body: str) -> bool:
        """
        Envia uma mensagem (WhatsApp ou SMS) para o número do destinatário usando a API REST do Twilio.
        Mensagens longas são divididas automaticamente em partes de até 1500 caracteres.
        """
        if not self.account_sid or not self.auth_token:
            print("[TwilioService] TWILIO_ACCOUNT_SID ou TWILIO_AUTH_TOKEN não configurados.")
            return False

        # Garante o formato correto whatsapp:+55...
        clean_num = to_number.replace("whatsapp:", "").strip()
        if not clean_num.startswith("+"):
            clean_num = f"+{clean_num}"

        if self.from_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{clean_num}"
        else:
            to_number = clean_num

        # Divide mensagens longas (limite Twilio Sandbox: 1600 chars)
        MAX_CHARS = 1500
        if len(body) <= MAX_CHARS:
            parts = [body]
        else:
            parts = self._split_message(body, MAX_CHARS)
            print(f"[TwilioService] Mensagem dividida em {len(parts)} parte(s).")

        all_success = True
        for i, part in enumerate(parts, 1):
            if len(parts) > 1:
                part_header = f"({i}/{len(parts)}) " if i > 1 else ""
                part = part_header + part if i > 1 else part

            data = {
                "From": self.from_number,
                "To": to_number,
                "Body": part
            }

            try:
                response = requests.post(
                    self.api_url,
                    data=data,
                    auth=(self.account_sid, self.auth_token)
                )
                if response.status_code in [200, 201]:
                    print(f"[TwilioService] Parte {i}/{len(parts)} enviada com sucesso para {to_number}")
                else:
                    print(f"[TwilioService] Erro ao enviar parte {i} ({response.status_code}): {response.text}")
                    all_success = False
            except Exception as e:
                print(f"[TwilioService] Exceção ao enviar parte {i}: {e}")
                all_success = False

            # Pequeno delay entre partes para evitar rate limiting
            if i < len(parts):
                import time
                time.sleep(1)

        return all_success

    @staticmethod
    def _split_message(text: str, max_chars: int = 1500) -> list:
        """Divide uma mensagem longa em partes, quebrando em linhas inteiras."""
        lines = text.split("\n")
        parts = []
        current_part = ""

        for line in lines:
            # Se adicionar esta linha ultrapassa o limite, salva a parte atual
            if len(current_part) + len(line) + 1 > max_chars and current_part:
                parts.append(current_part.rstrip())
                current_part = ""
            current_part += line + "\n"

        if current_part.strip():
            parts.append(current_part.rstrip())

        return parts if parts else [text[:max_chars]]

def enviar_whatsapp(body: str, to_number: Optional[str] = None) -> bool:
    """Função auxiliar global para enviar mensagem via Twilio WhatsApp."""
    dest = to_number or os.getenv("WHATSAPP_NUMBER", "5511961909818")
    service = TwilioService()
    return service.send_message(to_number=dest, body=body)

if __name__ == "__main__":
    service = TwilioService()
    print("[TwilioService] Inicializado com sucesso.")
