import subprocess

from pywinauto.application import Application
from pywinauto import Desktop
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
                class_name="TFrmPrincipalGanso"
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
            self._fechar_aviso_atencao()

            if self.esta_aberto():
                logger.success("Ganso abriu.")
                self._fazer_login()
                return

            time.sleep(intervalo)

        raise TimeoutError(f"Ganso não abriu em {timeout}s.")

    def _fechar_aviso_atencao(self):
        """
        Fecha a janela de aviso 'ATENÇÃO' (classe Dialog) que costuma
        aparecer antes da tela de login, se ela estiver na tela.
        Não faz nada (e não levanta exceção) se ela não existir.

        Usa Desktop(...).windows() em vez de Application.connect(),
        porque esse último não estava conseguindo localizar essa
        janela de forma confiável nesta máquina (provavelmente por
        haver várias outras janelas de classe 'Dialog' no sistema).
        """
        try:
            for janela in Desktop(backend="win32").windows():
                titulo = janela.window_text()

                if not titulo or not titulo.startswith("ATEN"):
                    continue

                if janela.friendly_class_name() != "Dialog":
                    continue

                if not janela.is_visible():
                    continue

                logger.info(f"Aviso detectado ('{titulo}'), fechando...")
                janela.set_focus()
                time.sleep(0.3)
                janela.type_keys("{ENTER}")
                time.sleep(0.5)
                logger.success("Aviso fechado.")
                return
        except Exception as e:
            logger.debug(f"Nenhum aviso encontrado ou erro ao fechar: {e}")

    def _fazer_login(self):
        """
        Preenche usuário e senha na tela de login do Ganso.
        Só é chamado depois que a janela do Ganso foi detectada
        (ou seja, dentro de abrir(), nunca no import do módulo).

        A tela de login é uma janela própria, separada da janela
        principal (TFrmPrincipalGanso): título 'Acesso ao Sistema',
        classe 'TFrmAcesso'.
        """
        logger.info("Realizando login no Ganso...")

        # Espera a tela 'Acesso ao Sistema' aparecer (pode levar um
        # instante depois do aviso 'ATENÇÃO' fechar). Continua tentando
        # fechar o aviso aqui também, porque ele pode surgir só agora
        # (depois que a janela principal já foi detectada em abrir()).
        janela_login = None
        inicio = time.time()

        while (time.time() - inicio) < 10:
            self._fechar_aviso_atencao()

            try:
                app_login = Application(backend="win32").connect(
                    class_name="TFrmAcesso"
                )
                candidata = app_login.window(class_name="TFrmAcesso")
                if candidata.exists():
                    janela_login = candidata
                    break
            except Exception:
                pass

            time.sleep(0.5)

        if janela_login is None:
            logger.warning(
                "Tela 'Acesso ao Sistema' não encontrada; "
                "login pode já ter sido feito ou o fluxo mudou."
            )
            return

        janela_login.wait("visible", timeout=10)
        janela_login.set_focus()

        # Dá tempo da janela terminar de ganhar foco de fato
        time.sleep(1)

        janela_login.type_keys(LOGIN_GANSO, with_spaces=True)  # digita usuario
        time.sleep(0.3)
        janela_login.type_keys("{TAB}")                        # navega para o campo de senha
        time.sleep(0.3)
        janela_login.type_keys(SENHA_GANSO, with_spaces=True)  # digita senha
        time.sleep(0.3)
        janela_login.type_keys("{ENTER}{ENTER}")                # envia o formulário

        logger.success("Login enviado.")

    def conectar_principal(self):

        logger.info("Conectando à janela principal do Ganso...")

        self.app = Application(backend="win32").connect(
            class_name="TFrmPrincipalGanso"
        )

        self.janela_principal = self.app.window(
            class_name="TFrmPrincipalGanso"
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
        # (usa só o prefixo sem acento para evitar problemas de encoding
        # na comparação do título — ver correção em _fechar_aviso_atencao)
        msg = self.app.window(title_re="ATEN.*")
        msg.wait("visible", timeout=10)

        logger.success("Mensagem de confirmação encontrada.")

        # Da o foco na janela
        msg.set_focus()

        time.sleep(0.5)

        # Clica no botão "ENTER" (botão padrao da janela)
        msg.type_keys("{ENTER}")

        time.sleep(2)

        logger.success("Arquivo gerado e confirmado.")

        time.sleep(1)

        send_keys("{ESC}")  # fecha a janela de exportação

        send_keys("^{F11}")  # fecha a janela principal do Ganso
        