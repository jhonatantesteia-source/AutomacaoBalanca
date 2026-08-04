"""
Inspeciona a tela de Carga do MGV 7 para descobrir seus AutomationIds.

Estratégia (mesma que funcionou para a Importação):
1. Conecta na janela principal (frPrincipal) via UIA.
2. Clica no botão "Carga" da toolOperacoes.
3. Varre TODOS os descendentes da janela principal — porque a tela
   de Carga, assim como a de Importação, provavelmente é um
   formulário filho (não uma janela de topo independente) e por
   isso não aparece em Desktop().windows().
4. Imprime AutomationId, control_type e texto de cada controle
   encontrado, para localizarmos os equivalentes de:
   - lista/checklist de balanças (equivalente ao ckItens)
   - opção "carga completa"
   - botão Enviar
   - botão Fechar/Sair
   - algum indicador de progresso/andamento da transmissão

Rode este script com o MGV 7 aberto e a tela de Carga fechada
(o próprio script abre a tela). Copie a saída do console e envie
de volta para montarmos o método Balanca.enviar_carga().
"""

import time

from pywinauto import Desktop
from loguru import logger


def dump(ctrl, nivel=0):
    try:
        logger.info(
            "{}{!r} | classe={} | control_type={} | auto_id={!r}",
            " " * nivel,
            ctrl.window_text(),
            ctrl.friendly_class_name(),
            ctrl.element_info.control_type,
            ctrl.element_info.automation_id,
        )
    except Exception:
        pass

    try:
        for filho in ctrl.children():
            dump(filho, nivel + 4)
    except Exception:
        pass


def listar_janelas_filhas(principal):
    """
    Lista especificamente os descendentes do tipo Window/Pane,
    que são os candidatos a serem o formulário da tela de Carga
    (equivalente ao frImportarArquivo).
    """
    logger.info("=" * 80)
    logger.info("CANDIDATOS A FORMULÁRIO DE CARGA (control_type Window/Pane)")
    logger.info("=" * 80)

    for ctrl in principal.descendants():
        try:
            tipo = ctrl.element_info.control_type
            if tipo in ("Window", "Pane"):
                logger.info(
                    "{!r} | control_type={} | auto_id={!r}",
                    ctrl.window_text(),
                    tipo,
                    ctrl.element_info.automation_id,
                )
        except Exception:
            pass


def main():
    logger.info("Conectando à janela principal do MGV...")

    principal = Desktop(backend="uia").window(auto_id="frPrincipal")
    principal.wait("visible", timeout=20)
    principal.set_focus()

    logger.success("MGV conectado.")

    logger.info("Abrindo tela de Carga...")

    principal.child_window(
        title="Carga",
        control_type="Button"
    ).wrapper_object().click_input()

    time.sleep(1.5)

    listar_janelas_filhas(principal)

    logger.info("=" * 80)
    logger.info("DUMP COMPLETO A PARTIR DA JANELA PRINCIPAL")
    logger.info("=" * 80)

    dump(principal)


if __name__ == "__main__":
    main()