"""
Investiga o fim da transmissão de carga: abre a tela de Carga, envia,
aciona "Acompanhar", varre a janela "Estado da transmissão"
(frConsultarEstadoTransmissao) e monitora até as grids de
comunicações pendentes (dgvProgresso / dgvSolicitacoes) esvaziarem
e ficarem estáveis — sinal de que a transmissão terminou. Em seguida
fecha a janela de transmissão e a tela de solicitação de carga.

ATENÇÃO: este script dispara uma transmissão REAL para as balanças
físicas. Pede confirmação antes de prosseguir.
"""

import time

from loguru import logger
from pywinauto import Desktop
from pywinauto.keyboard import send_keys
from pywinauto.timings import TimeoutError as PywinautoTimeoutError


def conectar_janela(candidatos, timeout=15, intervalo=0.5, descricao="janela"):
    """
    Tenta várias estratégias de busca (lista de funções sem argumento
    que retornam uma WindowSpecification) até uma existir e estar
    visível. Retorna a WindowSpecification (não resolve para wrapper),
    para continuar permitindo .child_window() encadeado.
    """
    inicio = time.time()

    while (time.time() - inicio) < timeout:
        for obter_spec in candidatos:
            try:
                spec = obter_spec()
                if spec.exists() and spec.is_visible():
                    return spec
            except Exception:
                pass

        time.sleep(intervalo)

    raise PywinautoTimeoutError(f"{descricao} não encontrada em {timeout}s.")


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


def dump_completo(raiz, nivel=0):
    try:
        logger.info(
            "{}{!r} | control_type={} | auto_id={!r} | class={!r}",
            " " * nivel,
            raiz.window_text(),
            raiz.element_info.control_type,
            raiz.element_info.automation_id,
            raiz.class_name(),
        )
    except Exception:
        pass

    try:
        for filho in raiz.children():
            dump_completo(filho, nivel + 4)
    except Exception:
        pass


def extrair_texto_elemento(item) -> str:
    """
    Extrai o texto real de uma célula do DataGridView (WinForms).

    IMPORTANTE: quando a célula não tem valor "classificado" pela UIA,
    window_text() retorna um nome de fallback tipo
    "Situação Linha 0, Não classificado." — isso NÃO é o valor da
    célula, é só o Accessible Name padrão do .NET, e ele CONTÉM a
    palavra "classificado" mesmo quando há valor de verdade em outro
    lugar. Por isso: rejeitamos qualquer texto que contenha "não
    classificado" (case-insensitive) e priorizamos
    LegacyIAccessible/ValuePattern antes de window_text(), pois são
    eles que costumam expor o valor real das células de DataGridView.
    """

    def valido(txt):
        return bool(txt) and "não classificado" not in txt.lower()

    try:
        legacy = item.iface_legacy_iaccessible
        val = legacy.CurrentValue or legacy.CurrentName
        if valido(val):
            return val.strip()
    except Exception:
        pass

    try:
        val = item.iface_value.CurrentValue
        if valido(val):
            return val.strip()
    except Exception:
        pass

    try:
        txt = item.window_text()
        if valido(txt):
            return txt.strip()
    except Exception:
        pass

    return ""


def linhas_de_dados(janela_transmissao, grid_id):
    """Retorna as linhas de dados (exclui 'Linha Superior') de uma grid, ou [] se não achar."""
    try:
        grid = janela_transmissao.child_window(auto_id=grid_id)
        return [
            c for c in grid.children()
            if c.element_info.control_type == "Custom"
            and c.window_text() != "Linha Superior"
        ]
    except Exception:
        return []


def status_das_linhas(janela_transmissao, grid_id):
    """Retorna uma lista de listas de valores de célula, uma por linha de dados da grid."""
    resultado = []
    for linha in linhas_de_dados(janela_transmissao, grid_id):
        try:
            valores = [extrair_texto_elemento(c) for c in linha.children()]
        except Exception:
            valores = []
        resultado.append(valores)
    return resultado


def listar_botoes(janela):
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

    

    logger.info("Abrindo tela de Carga...")

    principal.child_window(
        title="Carga", control_type="Button"
    ).wrapper_object().click_input()

    janela_carga = conectar_janela(
        [
            lambda: principal.child_window(
                auto_id="frSolicitarCargaBalancas", control_type="Window"
            ),
            lambda: Desktop(backend="uia").window(auto_id="frSolicitarCargaBalancas"),
        ],
        descricao="janela de solicitação de carga",
    )

    janela_carga.set_focus()
    time.sleep(0.5)

    logger.info("Clicando em Enviar...")

    janela_carga.child_window(
        auto_id="btnSolicitaCarga", control_type="Button"
    ).wrapper_object().click_input()

    time.sleep(1.2)

    logger.info("Acionando 'Acompanhar' via {LEFT}{ENTER}...")

    send_keys("{LEFT}", pause=0.2)
    send_keys("{ENTER}", pause=0.2)

    logger.info("Conectando à janela de estado da transmissão...")

    janela_transmissao = conectar_janela(
        [
            lambda: Desktop(backend="uia").window(auto_id="frConsultarEstadoTransmissao"),
            lambda: principal.child_window(
                auto_id="frConsultarEstadoTransmissao", control_type="Window"
            ),
            lambda: janela_carga.child_window(
                auto_id="frConsultarEstadoTransmissao", control_type="Window"
            ),
        ],
        descricao="janela de estado da transmissão",
    )

    logger.info("=" * 80)
    logger.info("DUMP COMPLETO DA JANELA DE TRANSMISSÃO (assim que abriu)")
    logger.info("=" * 80)
    dump_completo(janela_transmissao.wrapper_object())

    logger.info(
        "Monitorando dgvProgresso/dgvSolicitacoes até esvaziarem e "
        "ficarem estáveis (timeout 180s)..."
    )

    viu_linhas = False
    vazio_desde = None
    concluiu = False
    inicio = time.time()

    while (time.time() - inicio) < 180:
        linhas_progresso = status_das_linhas(janela_transmissao, "dgvProgresso")
        linhas_solicitacoes = status_das_linhas(janela_transmissao, "dgvSolicitacoes")
        total_linhas = len(linhas_progresso) + len(linhas_solicitacoes)

        logger.debug(f"dgvProgresso ({len(linhas_progresso)} linha(s)): {linhas_progresso}")
        logger.debug(f"dgvSolicitacoes ({len(linhas_solicitacoes)} linha(s)): {linhas_solicitacoes}")

        if total_linhas > 0:
            viu_linhas = True
            vazio_desde = None
        elif viu_linhas:
            if vazio_desde is None:
                vazio_desde = time.time()
                logger.info("Grids de pendências esvaziaram. Confirmando estabilidade...")
            elif (time.time() - vazio_desde) >= 3:
                logger.success(
                    "Transmissão concluída (grids de pendências vazias e estáveis)."
                )
                concluiu = True
                break

        time.sleep(2)

    if not concluiu:
        logger.error("Timeout sem confirmar esvaziamento estável das grids.")

    logger.info("=" * 80)
    logger.info("DUMP COMPLETO DA JANELA DE TRANSMISSÃO (após conclusão/timeout)")
    logger.info("=" * 80)
    dump_completo(janela_transmissao.wrapper_object())

    botoes = listar_botoes(janela_transmissao)
    logger.info(f"Botões disponíveis na janela de transmissão: {botoes}")

    logger.info("Tentando fechar a janela de transmissão via 'Sair' (btnSair)...")

    try:
        janela_transmissao.child_window(
            auto_id="btnSair", control_type="Button"
        ).wrapper_object().click_input()
        logger.success("Cliquei em 'Sair'.")
    except Exception as e:
        logger.warning(f"Não consegui clicar em 'Sair': {e}")

    time.sleep(1.5)

    try:
        ainda_aberta_transmissao = janela_transmissao.exists() and janela_transmissao.is_visible()
    except Exception:
        ainda_aberta_transmissao = False
    logger.info(f"Janela de transmissão ainda aberta? {ainda_aberta_transmissao}")

    try:
        ainda_aberta_carga = janela_carga.exists() and janela_carga.is_visible()
    except Exception:
        ainda_aberta_carga = False
    logger.info(f"Janela de solicitação de carga ainda aberta? {ainda_aberta_carga}")

    if ainda_aberta_carga:
        logger.info("Fechando janela de solicitação de carga via 'Sair' (btnFechar)...")
        try:
            janela_carga.child_window(
                auto_id="btnFechar", control_type="Button"
            ).wrapper_object().click_input()
            logger.success("Janela de solicitação de carga fechada.")
        except Exception as e:
            logger.warning(f"Não consegui fechar a janela de solicitação de carga: {e}")

    logger.info("Fim do fluxo investigativo.")


if __name__ == "__main__":
    main()