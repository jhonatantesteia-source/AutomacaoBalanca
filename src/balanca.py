import subprocess
import time
from time import sleep

from pywinauto import Desktop
from pywinauto.keyboard import send_keys
from pywinauto.timings import TimeoutError as PywinautoTimeoutError

from config import CAMINHO_MGV, TIMEOUT_ABERTURA_MGV
from logger import logger


class FalhaTransmissaoBalanca(Exception):
    """
    Levantada quando a transmissão da carga termina, mas uma ou mais
    balanças falharam na comunicação OU tiveram seu status final não
    confirmado (a linha sumiu da grid sem nunca mostrarmos "Sucesso na
    comunicação" — pode ser uma falha rápida que o polling não pegou a
    tempo). Guarda a lista das balanças nessa situação para que quem
    tratar o erro (ex: notificação) possa informar exatamente quais
    precisam ser verificadas.
    """

    def __init__(self, balancas_com_falha):
        self.balancas_com_falha = balancas_com_falha
        mensagem = (
            "Transmissão da carga terminou com falha ou status não "
            f"confirmado na(s) balança(s): {', '.join(balancas_com_falha)}"
        )
        super().__init__(mensagem)


class Balanca:
    def __init__(self, caminho_executavel=CAMINHO_MGV):
        self.app = None
        self.janela = None
        self.caminho_executavel = caminho_executavel

    def esta_aberto(self) -> bool:
        """Verifica se o MGV já está rodando, sem levantar exceção se não estiver."""
        try:
            return Desktop(backend="uia").window(auto_id="frPrincipal").exists()
        except Exception:
            return False

    def abrir(self, timeout=TIMEOUT_ABERTURA_MGV, intervalo=2):
        """
        Garante que o MGV está aberto, iniciando o executável se
        necessário. Não faz nada se já estiver rodando.
        """
        if self.esta_aberto():
            logger.info("MGV já está aberto.")
            return

        logger.info(f"Abrindo o MGV ({self.caminho_executavel})...")

        subprocess.Popen(self.caminho_executavel)

        inicio = time.time()

        while (time.time() - inicio) < timeout:
            if self.esta_aberto():
                logger.success("MGV abriu.")
                return

            sleep(intervalo)

        raise TimeoutError(f"MGV não abriu em {timeout}s.")

    def conectar(self):
        """Conecta na janela principal do MGV."""

        logger.info("Conectando ao MGV...")

        self.janela = Desktop(backend="uia").window(
            auto_id="frPrincipal"
        )

        self.janela.wait("visible", timeout=20)
        self.janela.set_focus()

        logger.success("MGV conectado.")
        time.sleep(2)  # Aguarda a tela principal carregar completamente

    def abrir_importacao(self):
        """Abre a tela de Importação."""

        logger.info("Abrindo tela de importação...")

        self.janela.child_window(
            title="Importação",
            control_type="Button"
        ).wrapper_object().click_input()

        sleep(1)

        logger.success("Tela de importação aberta.")

    def importar_arquivo(self):
        """Importa o arquivo TXT da pasta padrão."""

        self.abrir_importacao()

        logger.info("Iniciando importação...")

        janela_importacao = self.janela.child_window(
            auto_id="frImportarArquivo",
            control_type="Window"
        )

        janela_importacao.wait("visible", timeout=10)

        janela_importacao.child_window(
            auto_id="btnSalvar",
            control_type="Button"
        ).wrapper_object().click_input()

        logger.info("Confirmando diretório...")

        sleep(2)

        send_keys("{ENTER}")

        logger.info("Aguardando importação...")

        sleep(5)

        send_keys("{ENTER}")

        janela_importacao.child_window(
            auto_id="btnFechar",
            control_type="Button"
        ).wrapper_object().click_input()

        logger.success("Importação concluída.")

    def abrir_carga(self):
        """Abre a tela de carga."""

        logger.info("Abrindo tela de carga...")

        self.janela.child_window(
            title="Carga",
            control_type="Button"
        ).wrapper_object().click_input()

        sleep(1)

        logger.success("Tela de carga aberta.")

    def _conectar_janela(self, auto_id, escopos_extra=None, timeout=15, intervalo=0.5):
        """
        Localiza uma janela por AutomationId tentando múltiplos escopos
        de busca, até um deles existir e estar visível.

        Nem todo formulário do MGV é enumerado como janela de topo pelo
        backend UIA — frSolicitarCargaBalancas e frConsultarEstadoTransmissao,
        por exemplo, só são encontradas como descendentes de frPrincipal
        (ou de outra janela já aberta), nunca via Desktop().window() puro.
        Por isso tentamos vários escopos em vez de assumir um só;
        `escopos_extra` recebe janelas adicionais onde procurar.
        """
        candidatos = [
            lambda: self.janela.child_window(auto_id=auto_id, control_type="Window"),
            lambda: Desktop(backend="uia").window(auto_id=auto_id),
        ]

        for escopo in (escopos_extra or []):
            candidatos.append(
                lambda escopo=escopo: escopo.child_window(auto_id=auto_id, control_type="Window")
            )

        inicio = time.time()

        while (time.time() - inicio) < timeout:
            for obter_spec in candidatos:
                try:
                    spec = obter_spec()
                    if spec.exists() and spec.is_visible():
                        # Devolve a WindowSpecification (não o wrapper
                        # resolvido), para continuar permitindo
                        # .child_window() encadeado.
                        return spec
                except Exception:
                    pass

            sleep(intervalo)

        raise PywinautoTimeoutError(
            f"Janela com auto_id={auto_id!r} não encontrada em {timeout}s."
        )

    @staticmethod
    def _extrair_texto_elemento(item) -> str:
        """
        Extrai o texto real de uma célula do DataGridView (WinForms).

        window_text() de uma célula "sem valor classificado" pela UIA
        retorna um nome de fallback tipo "Situação Linha 0, Não
        classificado." — isso NÃO é o valor da célula. Por isso
        priorizamos LegacyIAccessible/ValuePattern (que expõem o valor
        real) e só usamos window_text() como último recurso, rejeitando
        qualquer texto que contenha "não classificado".
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

    def _linhas_de_dados(self, janela_transmissao, grid_id):
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

    def _capturar_progresso(self, janela_transmissao) -> dict:
        """
        Retorna {identificador_da_balança: [valores_da_linha]} para as
        linhas atualmente presentes em dgvProgresso (ex.: chave
        "01 - 192.168.2.182", valores ["01 - 192.168.2.182", tentativas,
        estado_comunicacao, progresso]).
        """
        progresso = {}

        for linha in self._linhas_de_dados(janela_transmissao, "dgvProgresso"):
            try:
                valores = [self._extrair_texto_elemento(c) for c in linha.children()]
            except Exception:
                continue

            if valores and valores[0]:
                progresso[valores[0]] = valores

        return progresso

    def _avaliar_resultado(self, ultimo_status: dict):
        """
        Avalia o último status conhecido de cada balança (capturado
        antes da linha sumir da grid) para decidir se a transmissão
        terminou com sucesso ou com falha em alguma balança.

        IMPORTANTE: exigimos confirmação EXPLÍCITA de "sucesso" —
        não basta a ausência da palavra "falha". Se a linha sumir da
        grid entre dois ciclos de polling logo após uma falha rápida,
        o último status capturado pode ser um estado neutro (ex.:
        "Verificando balança...") sem nunca termos visto o texto de
        falha. Assumir sucesso nesse caso já gerou um aviso de
        "sucesso" para uma balança que na verdade falhou. Por isso
        qualquer balança sem confirmação explícita de sucesso entra
        no alerta, mesmo que não tenhamos capturado a palavra "falha".

        Retorna uma tupla (status, balancas_com_problema).
        """
        falhas = []
        indeterminadas = []

        for chave, valores in ultimo_status.items():
            textos = [v.lower() for v in valores]

            if any("falha" in t for t in textos):
                falhas.append(chave)
            elif not any("sucesso" in t for t in textos):
                indeterminadas.append(chave)

        if falhas:
            logger.warning(f"Balanças com falha confirmada: {falhas}")

        if indeterminadas:
            logger.warning(
                "Balanças sem confirmação explícita de sucesso (linha sumiu "
                f"da grid sem nunca mostrar 'Sucesso na comunicação'): {indeterminadas}"
            )

        if falhas or indeterminadas:
            return "TERMINADO_COM_FALHA", falhas + indeterminadas

        logger.success("Transmissão concluída com sucesso confirmado em todas as balanças.")
        return "CONCLUIDO", []

    def _aguardar_transmissao(self, janela_transmissao, timeout=180, intervalo=1, estabilidade=2):
        """
        Acompanha a transmissão até as grids de comunicações pendentes
        (dgvProgresso / dgvSolicitacoes) esvaziarem e ficarem estáveis
        por `estabilidade` segundos — esse é o sinal real de conclusão
        (o texto "Terminado" nunca chega a aparecer nessas grids).

        `intervalo` foi reduzido de 2s para 1s: um estado de falha pode
        aparecer e a linha sumir da grid em uma janela curta, e um
        polling mais lento aumenta a chance de nunca capturarmos o
        texto de falha antes da linha desaparecer.

        Retorna uma tupla (status, balancas_com_problema).
        """
        logger.info("Acompanhando transmissão...")

        ultimo_status = {}
        viu_linhas = False
        vazio_desde = None
        inicio = time.time()

        while (time.time() - inicio) < timeout:
            progresso_atual = self._capturar_progresso(janela_transmissao)
            ultimo_status.update(progresso_atual)

            total_linhas = len(progresso_atual) + len(
                self._linhas_de_dados(janela_transmissao, "dgvSolicitacoes")
            )

            if total_linhas > 0:
                viu_linhas = True
                vazio_desde = None
                logger.info(f"Transmissão em andamento: {list(progresso_atual.values())}")
            elif viu_linhas:
                if vazio_desde is None:
                    vazio_desde = time.time()
                elif (time.time() - vazio_desde) >= estabilidade:
                    return self._avaliar_resultado(ultimo_status)

            sleep(intervalo)

        logger.error("Timeout aguardando o esvaziamento das grids de transmissão.")
        return "TIMEOUT", []

    def enviar_carga(self):
        """
        Envia a carga para as balanças e acompanha a transmissão até o fim.

        "Todas as balanças" e "Completa" já vêm marcadas por padrão na
        tela, então não precisamos selecioná-las — só disparar o envio.
        Depois de clicar em Enviar, um popup abre com o foco em
        "Acompanhar"; {LEFT}{ENTER} seleciona essa opção e abre a
        janela "Estado da transmissão" (frConsultarEstadoTransmissao),
        onde acompanhamos o status até as grids de pendências
        esvaziarem, e então fechamos tudo (transmissão e tela de carga).
        """
        self.abrir_carga()

        logger.info("Aguardando tela de solicitação de carga...")

        janela_carga = self._conectar_janela("frSolicitarCargaBalancas")
        janela_carga.set_focus()
        sleep(0.5)

        logger.info("Enviando solicitação de carga...")

        janela_carga.child_window(
            auto_id="btnSolicitaCarga",
            control_type="Button"
        ).wrapper_object().click_input()

        sleep(1.2)

        logger.info("Acionando 'Acompanhar'...")

        send_keys("{LEFT}", pause=0.2)
        send_keys("{ENTER}", pause=0.2)

        logger.info("Aguardando janela de estado da transmissão...")

        janela_transmissao = self._conectar_janela(
            "frConsultarEstadoTransmissao",
            escopos_extra=[janela_carga],
        )

        resultado, balancas_com_falha = self._aguardar_transmissao(janela_transmissao)

        if resultado == "TIMEOUT":
            raise RuntimeError("Timeout aguardando a finalização da transmissão da carga.")

        if resultado == "TERMINADO_COM_FALHA":
            raise FalhaTransmissaoBalanca(balancas_com_falha)

        logger.info("Fechando janela de transmissão...")

        try:
            janela_transmissao.child_window(
                auto_id="btnSair",
                control_type="Button"
            ).wrapper_object().click_input()
        except Exception:
            logger.warning("Não foi possível clicar em 'Sair' na janela de transmissão.")

        sleep(1.5)

        logger.info("Fechando tela de solicitação de carga...")

        try:
            janela_carga.child_window(
                auto_id="btnFechar",
                control_type="Button"
            ).wrapper_object().click_input()
        except Exception:
            logger.warning("Não foi possível fechar a tela de solicitação de carga.")

        logger.success("Carga enviada e transmissão concluída.")

time.sleep(1)

send_keys("%{F4}")  # fecha a janela principal do MGV7