import smtplib
from email.mime.text import MIMEText

import requests
from loguru import logger

from src.config import (
    CALLMEBOT_DESTINATARIOS,
    EMAIL_REMETENTE,
    EMAIL_SENHA_APP,
    EMAIL_DESTINATARIO,
)


def enviar_whatsapp(mensagem: str) -> None:
    """
    Envia uma mensagem de WhatsApp para todos os números configurados,
    via CallMeBot.

    Nunca levanta exceção: uma falha ao notificar (sem internet, API
    fora do ar, etc.) não deve impedir o restante do script de rodar
    nem mascarar o erro original que estava sendo reportado.

    Configuração necessária em config.py: CALLMEBOT_DESTINATARIOS
    (lista de {"telefone": ..., "apikey": ...}, um por número — veja
    instruções de ativação no config.py).
    """
    if not CALLMEBOT_DESTINATARIOS:
        logger.warning(
            "CallMeBot não configurado (CALLMEBOT_DESTINATARIOS vazio "
            "em config.py); aviso por WhatsApp não enviado."
        )
        return

    for destinatario in CALLMEBOT_DESTINATARIOS:
        telefone = destinatario.get("telefone")
        apikey = destinatario.get("apikey")

        if not telefone or not apikey:
            logger.warning(f"Destinatário CallMeBot mal configurado: {destinatario}")
            continue

        try:
            resposta = requests.get(
                "https://api.callmebot.com/whatsapp.php",
                params={
                    "phone": telefone,
                    "text": mensagem,
                    "apikey": apikey,
                },
                timeout=15,
            )

            if resposta.status_code == 200:
                logger.success(f"Aviso enviado por WhatsApp para {telefone}.")
            else:
                logger.warning(
                    f"Falha ao enviar aviso por WhatsApp para {telefone} "
                    f"(status {resposta.status_code}): {resposta.text}"
                )
        except Exception as e:
            logger.warning(f"Erro ao tentar enviar aviso por WhatsApp para {telefone}: {e}")


def enviar_email(assunto: str, mensagem: str) -> None:
    """
    Envia um e-mail de aviso para o responsável, via Gmail (SMTP).

    Nunca levanta exceção: uma falha ao notificar não deve impedir o
    restante do script de rodar nem mascarar o erro original que
    estava sendo reportado.

    Configuração necessária em config.py: EMAIL_REMETENTE (a conta
    Gmail que envia), EMAIL_SENHA_APP (senha de app gerada em
    https://myaccount.google.com/apppasswords) e EMAIL_DESTINATARIO
    (quem recebe o aviso).
    """
    if not EMAIL_REMETENTE or not EMAIL_SENHA_APP or not EMAIL_DESTINATARIO:
        logger.warning(
            "E-mail não configurado (EMAIL_REMETENTE/EMAIL_SENHA_APP/"
            "EMAIL_DESTINATARIO ausentes em config.py); aviso por e-mail "
            "não enviado."
        )
        return

    try:
        msg = MIMEText(mensagem, _charset="utf-8")
        msg["Subject"] = assunto
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = EMAIL_DESTINATARIO

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA_APP)
            servidor.sendmail(EMAIL_REMETENTE, [EMAIL_DESTINATARIO], msg.as_string())

        logger.success("Aviso enviado por e-mail.")
    except Exception as e:
        logger.warning(f"Erro ao tentar enviar aviso por e-mail: {e}")
