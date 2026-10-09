import time
from loguru import logger
from pywinauto import Desktop


def valor_legacy(ctrl):
    try:
        return ctrl.legacy_properties()["Value"]
    except Exception:
        return None


def valor_pattern(ctrl):
    try:
        return ctrl.iface_value.CurrentValue
    except Exception:
        return None


def dump_controle(ctrl, nivel=0):
    prefixo = "    " * nivel

    try:
        nome = ctrl.window_text()
    except Exception:
        nome = None

    try:
        auto_id = ctrl.element_info.automation_id
    except Exception:
        auto_id = None

    try:
        tipo = ctrl.element_info.control_type
    except Exception:
        tipo = None

    logger.info(
        "{}{} | texto={!r} | auto_id={!r}",
        prefixo,
        tipo,
        nome,
        auto_id,
    )

    legacy = valor_legacy(ctrl)
    if legacy:
        logger.info("{}    legacy = {!r}", prefixo, legacy)

    value = valor_pattern(ctrl)
    if value:
        logger.info("{}    value  = {!r}", prefixo, value)


def dump_hierarquia(ctrl, nivel=0):
    dump_controle(ctrl, nivel)

    try:
        filhos = ctrl.children()
    except Exception:
        return

    for filho in filhos:
        dump_hierarquia(filho, nivel + 1)


def esperar_janela():
    logger.info("Aguardando Estado da transmissão...")

    desktop = Desktop(backend="uia")

    while True:

        try:
            janela = desktop.window(
                auto_id="frConsultarEstadoTransmissao"
            )

            if janela.exists(timeout=0.2):
                logger.success("Janela encontrada.")
                return janela

        except Exception:
            pass

        time.sleep(0.2)


def main():

    janela = esperar_janela()

    logger.info("=" * 80)
    logger.info("DUMP COMPLETO")
    logger.info("=" * 80)

    dump_hierarquia(janela)


if __name__ == "__main__":
    main()