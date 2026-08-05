import subprocess

from pywinauto.application import Application
from loguru import logger
import time
from pywinauto.keyboard import send_keys


from config import CAMINHO_GANSO, TIMEOUT_ABERTURA_GANSO, LOGIN_GANSO, SENHA_GANSO


class ERP:

    def __init__(self, caminho_executavel=CAMINHO_GANSO):
        self.app = None
        self.janela_principal = None
        self.janela_exportacao = None
        self.caminho_executavel = caminho_executavel

    def esta_aberto(self) -> bool:
        """Verifica se o Ganso já está rodando, sem levantar exceção se não estiver."""
        try:
            Application(backend="win32").connect(
                title_re=".*Ganso Gestão Empresarial.*"
            )
            return True
        except Exception:
            return False

    def abrir(self, timeout=TIMEOUT_ABERTURA_GANSO, intervalo=2):
        """
        Garante que o Ganso está aberto, iniciando o executável se
        necessário. Não faz nada se já estiver rodando (permite rodar
        o fluxo tanto agendado, com tudo fechado, quanto manualmente,
        com os programas já abertos).
        """
        if self.esta_aberto():
            logger.info("Ganso já está aberto.")
            return

        logger.info(f"Abrindo o Ganso ({self.caminho_executavel})...")

        subprocess.Popen(self.caminho_executavel)

        inicio = time.time()

        while (time.time() - inicio) < timeout:
            if self.esta_aberto():
                logger.success("Ganso abriu.")
                return

            time.sleep(intervalo)

        raise TimeoutError(f"Ganso não abriu em {timeout}s.")

    send_keys("{ENTER}")  # Fecha janela backup
   # send_keys("{2}{7}")  # digita usuario
    send_keys(LOGIN_GANSO)  # digita usuario
    send_keys("{TAB}")  # navega para o campo de senha
   # send_keys("{5}{4}{6}{6}")  # digita senha
    send_keys(SENHA_GANSO)  # digita senha
    send_keys("{ENTER}{ENTER}")  # envia o formulário

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

        time.sleep(2)

        # Localiza a janela da mensagem de sucesso
        msg = self.app.window(title_re=".*ATENÇÃO.*")
        msg.wait("visible", timeout=10)

        logger.success("Mensagem de confirmação encontrada.")

        #Da o foco na janela
        msg.set_focus()
         
        time.sleep(0.5)    

        # Clica no botão "ENTER" (botão padrao da janela)
        msg.type_keys("{ENTER}")

        time.sleep(2)
        
        logger.success("Arquivo gerado e confirmado.")