"""Ponto de entrada: coordena os serviços sem concentrar a lógica neles."""
from __future__ import annotations

import sys

from src.balanca import Balanca, FalhaTransmissaoBalanca
from src.config import validar_configuracao
from src.erp import ERP
from src.logger import logger
from src.notificacao import enviar_email, enviar_whatsapp


def notificar(assunto: str, mensagem: str) -> None:
    """Notificações são auxiliares: não devem mascarar o resultado principal."""
    enviar_whatsapp(mensagem)
    enviar_email(assunto=assunto, mensagem=mensagem)


def executar_automacao() -> None:
    """Executa o fluxo de ponta a ponta; cada etapa pode ser testada isoladamente."""
    erp = ERP()
    balanca = Balanca()

    if not erp.garantir_ganso_fechado():
        raise RuntimeError("Não foi possível garantir que o Ganso está fechado.")

    erp.abrir()
    erp.conectar_principal()
    erp.abrir_gerador_balanca()
    erp.conectar_exportacao()
    erp.gerar_arquivo_balanca()

    balanca.abrir()
    balanca.conectar()
    balanca.importar_arquivo()
    balanca.enviar_carga()


def main() -> int:
    logger.info("Iniciando automação da balança")
    try:
        validar_configuracao()
        executar_automacao()
    except FalhaTransmissaoBalanca as exc:
        logger.exception("Transmissão concluída com falhas")
        balancas = ", ".join(exc.balancas_com_falha)
        notificar(
            "Falha de comunicação em balança(s)",
            f"A transmissão terminou, mas não foi possível confirmar o sucesso em: {balancas}.",
        )
        return 2
    except Exception as exc:
        logger.exception("Falha na automação")
        notificar("Falha na automação da balança", f"A automação falhou: {exc}")
        return 1

    logger.success("Automação concluída com sucesso")
    notificar(
        "Automação da balança concluída com sucesso",
        "Arquivo gerado e carga enviada para as balanças.",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
