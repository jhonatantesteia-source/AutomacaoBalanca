from pywinauto.application import Application
from loguru import logger
import time


class ERP:

    def __init__(self):
        self.app = None
        self.janela = None

    def conectar_exportacao(self):
        logger.info("Conectando à janela de exportação.")

        self.app = Application(backend="win32").connect(
            title_re=".*Gerar Arquivo para Balança.*"
        )

        self.janela = self.app.top_window()

        self.janela.set_focus()

        logger.success("Janela encontrada.")

    def gerar_arquivo_balanca(self):

        logger.info("Gerando arquivo da balança...")

        self.janela.child_window(
            title="&Confirma",
            class_name="TButton"
        ).click()

        logger.success("Comando enviado.")

        time.sleep(2)