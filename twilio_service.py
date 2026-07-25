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
        :param to_number: Número de destino (ex: 'whatsapp:+5511999999999' ou '+5511999999999')
        :param body: Texto da mensagem
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

        data = {
            "From": self.from_number,
            "To": to_number,
            "Body": body
        }

        try:
            response = requests.post(
                self.api_url,
                data=data,
                auth=(self.account_sid, self.auth_token)
            )
            if response.status_code in [200, 201]:
                print(f"[TwilioService] Mensagem enviada com sucesso para {to_number}")
                return True
            else:
                print(f"[TwilioService] Erro ao enviar ({response.status_code}): {response.text}")
                return False
        except Exception as e:
            print(f"[TwilioService] Exceção ao enviar mensagem Twilio: {e}")
            return False

if __name__ == "__main__":
    service = TwilioService()
    print("[TwilioService] Inicializado com sucesso.")
