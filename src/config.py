"""Configuração centralizada do ambiente. Segredos devem ficar em .env."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

CAMINHO_GANSO = os.getenv("CAMINHO_GANSO", r"C:\Ganso\Ganso.exe")
CAMINHO_MGV = os.getenv(
    "CAMINHO_MGV",
    r"C:\Program Files (x86)\Toledo do Brasil\MGV 7\MGV7Central.exe",
)
TIMEOUT_ABERTURA_GANSO = float(os.getenv("TIMEOUT_ABERTURA_GANSO", "30"))
TIMEOUT_ABERTURA_MGV = float(os.getenv("TIMEOUT_ABERTURA_MGV", "30"))
TIMEOUT_TRANSMISSAO_BALANCA = float(os.getenv("TIMEOUT_TRANSMISSAO_BALANCA", "180"))

LOGIN_GANSO = os.getenv("LOGIN_GANSO", "")
SENHA_GANSO = os.getenv("SENHA_GANSO", "")

def parse_callmebot_destinatarios(valor: str) -> list[dict[str, str]]:
    """Converte 'telefone:apikey,...' em destinatários validados."""
    destinatarios = []
    for item in valor.split(","):
        item = item.strip()
        if not item:
            continue
        telefone, separador, apikey = item.partition(":")
        if not separador or not telefone.strip() or not apikey.strip():
            raise ValueError("Destinatário inválido; use o formato telefone:apikey")
        destinatarios.append({"telefone": telefone.strip(), "apikey": apikey.strip()})
    return destinatarios


CALLMEBOT_DESTINATARIOS = parse_callmebot_destinatarios(
    os.getenv("CALLMEBOT_DESTINATARIOS", "")
)

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
EMAIL_SENHA_APP = os.getenv("EMAIL_SENHA_APP", "")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO", "")


def validar_configuracao() -> None:
    """Valida os requisitos essenciais antes de iniciar a automação."""
    erros = []
    if not Path(CAMINHO_GANSO).is_file():
        erros.append(f"Executável do Ganso não encontrado: {CAMINHO_GANSO}")
    if not Path(CAMINHO_MGV).is_file():
        erros.append(f"Executável do MGV não encontrado: {CAMINHO_MGV}")
    if not LOGIN_GANSO or not SENHA_GANSO:
        erros.append("Configure LOGIN_GANSO e SENHA_GANSO no arquivo .env")
    if erros:
        raise RuntimeError("Configuração inválida:\n- " + "\n- ".join(erros))
