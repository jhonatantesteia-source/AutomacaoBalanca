from time import sleep

from pywinauto import Desktop
from pywinauto.keyboard import send_keys

from logger import logger


class Balanca:
    def __init__(self):
        self.app = None
        self.janela = None

    def conectar(self):
        """Conecta na janela principal do MGV."""

        logger.info("Conectando ao MGV...")

        self.janela = Desktop(backend="uia").window(
            auto_id="frPrincipal"
        )

        self.janela.wait("visible", timeout=20)
        self.janela.set_focus()

        logger.success("MGV conectado.")

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

    def enviar_carga(self):
        """
        Ainda será implementado após mapearmos
        a tela de carga.
        """
        self.abrir_carga()