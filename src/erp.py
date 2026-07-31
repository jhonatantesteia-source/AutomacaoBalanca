from pywinauto.application import Application
from loguru import logger
import time


class ERP:

    def __init__(self):
        self.app = None
        self.janela_principal = None
        self.janela_exportacao = None

    def conectar_principal(self):

        logger.info("Conectando ao Ganso Gestão Empresarial...")

        self.app = Application(backend="win32").connect(
            title_re=".*Ganso Gestão Empresarial.*"
        )

        self.janela_principal = self.app.window(
            title_re=".*Ganso Gestão Empresarial.*"
        )

        self.janela_principal.set_focus()

        logger.success("Janela principal encontrada.")

    def abrir_gerador_balanca(self):

        logger.info("Abrindo Gerar Arquivo para Balança...")

        self.janela_principal.set_focus()

        time.sleep(1)

        # ALT + U
        self.janela_principal.type_keys("%u", pause=0.2)

        time.sleep(1)

        for _ in range(13):
            self.janela_principal.type_keys("{DOWN}")
            time.sleep(0.3)

        self.janela_principal.type_keys("{ENTER}")
        
        logger.success("Janela de exportação aberta.")

        time.sleep(1)

    def conectar_exportacao(self):

        logger.info("Conectando à janela de exportação...")

        self.app = Application(backend="win32").connect(
            title_re=".*Gerar Arquivo para Balança.*"
        )

        self.janela_exportacao = self.app.top_window()

        self.janela_exportacao.set_focus()

        logger.success("Janela localizada.")

    def gerar_arquivo_balanca(self):

        logger.info("Gerando arquivo...")

        self.janela_exportacao.child_window(
            title="&Confirma",
            class_name="TButton"
        ).click()

        logger.success("Arquivo gerado.")