import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple

class GreetingContextSkill:
    """
    SKILL especializada em análise temporal, contexto de saudações e gentileza social para o JARVYS.
    Calcula fuso horário do Brasil (UTC-3), período do dia (Manhã/Tarde/Noite) e dias da semana.
    """

    @staticmethod
    def get_time_context() -> Dict[str, str]:
        # Fuso horário do Brasil / Brasília (UTC-3)
        tz_br = timezone(timedelta(hours=-3))
        now = datetime.now(tz_br)

        hour = now.hour
        if 5 <= hour < 12:
            periodo = "Manhã"
            saudacao_sugerida = "Bom dia 🌅"
        elif 12 <= hour < 18:
            periodo = "Tarde"
            saudacao_sugerida = "Boa tarde ☀️"
        else:
            periodo = "Noite"
            saudacao_sugerida = "Boa noite 🌙"

        dias_semana = [
            "Segunda-feira", "Terça-feira", "Quarta-feira",
            "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
        ]
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]

        dia_semana_str = dias_semana[now.weekday()]
        data_extenso = f"{dia_semana_str}, {now.day} de {meses[now.month - 1]} de {now.year}"
        hora_str = now.strftime("%H:%M")

        return {
            "periodo": periodo,
            "saudacao_sugerida": saudacao_sugerida,
            "data_extenso": data_extenso,
            "hora": hora_str,
            "dia_semana": dia_semana_str
        }

    @classmethod
    def is_greeting(cls, message: str) -> Tuple[bool, str]:
        """
        Analisa se a mensagem do usuário contém saudações simples.
        Retorna (is_greeting, saudacao_detectada)
        """
        msg = message.strip().lower()
        # Limpa pontuações e menções ao nome JARVYS
        clean_msg = re.sub(r'[.!😊👍🙏?,]', '', msg)
        clean_msg = clean_msg.replace("jarvys", "").replace("jarvis", "").strip()

        greetings_exact = [
            "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite",
            "tudo bem", "tudo bem?", "fala jarvys", "hey", "hello",
            "salve", "oie", "opa", "start", "iniciar", "menu"
        ]

        greetings_regex = [
            r"\b(oi|ol[áa]|oie|hey|hello|salve|opa)\b",
            r"\b(bom\s+dia|boa\s+tarde|boa\s+noite)\b",
            r"\b(tudo\s+bem|tudo\s+certo|fala\s+jarvys)\b"
        ]

        if clean_msg in greetings_exact or msg in greetings_exact:
            return True, clean_msg

        for pattern in greetings_regex:
            if re.search(pattern, clean_msg):
                return True, clean_msg

        return False, ""
