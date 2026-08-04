"""
Observa a grid "Estado de operação" (dtGrdEstadoOperacao) da janela
principal do MGV antes, durante e depois do envio de uma carga, e
detecta automaticamente qualquer popup/diálogo que apareça ao clicar
em "Enviar" — varrendo todas as janelas de topo do desktop, não só
os descendentes de frPrincipal (um popup normalmente é uma janela
de topo separada, não um filho de frPrincipal).

ATENÇÃO: este script clica de verdade em "Enviar" na tela de Carga,
ou seja, DISPARA UMA TRANSMISSÃO REAL para as balanças físicas.
Ele pede confirmação antes de prosseguir.
"""

import time

from loguru import logger
from pywinauto import Desktop

COLUNAS = ["Código", "Lojas", "Estado das Lojas", "Andamento", "Observações"]


def localizar_linha_estado(tabela):
    """Retorna a primeira linha de dados da grid (ignora o cabeçalho)."""
    linhas = [
        c for c in tabela.children()
        if c.element_info.control_type == "Custom"
        and c.window_text() != "Linha Superior"
    ]
    return linhas[0] if linhas else None


def dump_linha(linha): #jhfdjhfdkagcgsacasgcg
    textos = []
    for cel in linha.children():
        try:
            textos.append(cel.window_text())
        except Exception:
            textos.append("?")

    partes = [f"{nome}={valor!r}" for nome, valor in zip(COLUNAS, textos)]
    logger.info(" | ".join(partes))


def assinatura(ctrl):
    """Identifica um controle de forma relativamente estável."""
    try:
        return (
            ctrl.element_info.control_type,
            ctrl.window_text(),
            ctrl.element_info.automation_id,
            ctrl.class_name(),
        )
    except Exception:
        return None


def dump_novos_controles(raiz, conhecidos):
    """Registra e imprime apenas os controles novos encontrados a partir de `raiz`."""
    novos = 0

    for ctrl in raiz.descendants():
        sig = assinatura(ctrl)

        if not sig or sig in conhecidos:
            continue

        conhecidos.add(sig)
        novos += 1

        try:
            rect = ctrl.rectangle()
        except Exception:
            rect = None

        logger.info(
            "[NOVO] tipo={!r} texto={!r} auto_id={!r} class={!r} rect={}",
            sig[0], sig[1], sig[2], sig[3], rect,
        )

    return novos


def mapear_janelas_topo():
    """
    Retorna {handle: janela} com todas as janelas de topo visíveis
    no desktop agora — usado para detectar popups por diferença,
    já que eles não são descendentes de frPrincipal.
    """
    janelas = {}
    for w in Desktop(backend="uia").windows():
        try:
            janelas[w.handle] = w
        except Exception:
            pass
    return janelas


def detectar_popup_novo(janelas_antes, timeout=5):
    """Aguarda até `timeout`s por uma janela de topo nova e a retorna (ou None)."""
    inicio = time.time()

    while time.time() - inicio < timeout:
        atuais = mapear_janelas_topo()
        novas = [h for h in atuais if h not in janelas_antes]

        if novas:
            return atuais[novas[0]]

        time.sleep(0.3)

    return None


def descrever_botoes(janela):
    botoes = []
    for ctrl in janela.descendants(control_type="Button"):
        try:
            botoes.append((ctrl.window_text(), ctrl.element_info.automation_id))
        except Exception:
            pass
    return botoes


def main():
    logger.info("Conectando à janela principal do MGV...")

    principal = Desktop(backend="uia").window(auto_id="frPrincipal")
    principal.wait("visible", timeout=20)
    principal.set_focus()

    tabela = principal.child_window(
        auto_id="dtGrdEstadoOperacao",
        control_type="Table",
    )

    logger.info("Estado ANTES do envio:")

    linha = localizar_linha_estado(tabela)
    if linha:
        dump_linha(linha)
    else:
        logger.warning("Nenhuma linha encontrada.")

    confirmar = input(
        "\nATENÇÃO: isso vai abrir a tela de Carga, clicar em "
        "'Enviar' e transmitir de verdade para as balanças.\n"
        "Digite 'sim' para continuar: "
    )

    if confirmar.strip().lower() != "sim":
        logger.warning("Cancelado pelo usuário. Nada foi enviado.")
        return

    logger.info("Abrindo tela de Carga...")

    principal.child_window(
        title="Carga",
        control_type="Button",
    ).wrapper_object().click_input()

    time.sleep(1.5)

    janela_carga = principal.child_window(
        auto_id="frSolicitarCargaBalancas",
        control_type="Window",
    )
    janela_carga.wait("visible", timeout=10)

    logger.info("Mapeando controles e janelas existentes...")

    conhecidos = set()
    for ctrl in principal.descendants():
        sig = assinatura(ctrl)
        if sig:
            conhecidos.add(sig)

    janelas_antes = mapear_janelas_topo()

    logger.info(
        f"{len(conhecidos)} controles e {len(janelas_antes)} janelas conhecidas."
    )

    logger.info("Clicando em Enviar...")

    janela_carga.child_window(
        auto_id="btnSolicitaCarga",
        control_type="Button",
    ).wrapper_object().click_input()

    logger.info("Enviado. Procurando popup de confirmação (até 5s)...")

    popup = detectar_popup_novo(janelas_antes, timeout=5)

    if popup:
        try:
            titulo = popup.window_text()
            auto_id = popup.element_info.automation_id
            classe = popup.class_name()
        except Exception:
            titulo, auto_id, classe = "?", "?", "?"

        logger.success(
            "Popup detectado: título={!r} auto_id={!r} classe={!r}",
            titulo, auto_id, classe,
        )

        botoes = descrever_botoes(popup)
        logger.info(f"Botões do popup: {botoes}")
        logger.warning(
            "Popup NÃO foi fechado automaticamente por este script — "
            "feche manualmente e anote qual botão usar, para "
            "automatizarmos isso na próxima versão."
        )
    else:
        logger.info("Nenhum popup novo detectado nesses 5s.")

    logger.info("Monitorando novos controles em frPrincipal por 10 segundos...")

    for i in range(10):
        logger.info(f"===== t+{i + 1}s =====")
        dump_novos_controles(principal, conhecidos)
        time.sleep(1)

    logger.info("Fim do monitoramento.")


if __name__ == "__main__":
    main()