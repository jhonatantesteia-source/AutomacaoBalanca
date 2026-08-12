import subprocess
import time

from pywinauto.application import Application
from pywinauto import Desktop
from loguru import logger

from pywinauto.keyboard import send_keys

from config import (
    CAMINHO_GANSO,
    TIMEOUT_ABERTURA_GANSO,
    LOGIN_GANSO,
    SENHA_GANSO
)


class ERP:

    def __init__(self, caminho_executavel=CAMINHO_GANSO):
        self.app = None
        self.janela_principal = None
        self.janela_exportacao = None
        self.caminho_executavel = caminho_executavel

    def esta_aberto(self) -> bool:
        """
        Verifica se a janela principal do Ganso está aberta.
        """

        try:
            Application(backend="win32").connect(
                class_name="TFrmPrincipalGanso"
            )
            return True

        except Exception:
            return False

    def ganso_esta_aberto(self) -> bool:
        """
        Verifica diretamente se o processo Ganso.exe está em execução.
        """

        resultado = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Ganso.exe"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return "Ganso.exe" in resultado.stdout

    def garantir_ganso_fechado(self) -> bool:
        """
        Garante que nenhuma instância do Ganso.exe esteja em execução
        antes de iniciar uma nova automação.

        Primeiro tenta encerrar normalmente.
        Se não encerrar em até 5 segundos, força o encerramento.
        """

        if not self.ganso_esta_aberto():
            logger.info("Ganso já está fechado.")
            return True

        logger.warning("Ganso está aberto. Encerrando processo...")

        # Tenta encerrar normalmente
        resultado = subprocess.run(
            ["taskkill", "/IM", "Ganso.exe"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if resultado.returncode == 0:
            logger.info("Comando de encerramento enviado ao Ganso.")
        else:
            logger.warning(
                f"Não foi possível encerrar normalmente: "
                f"{resultado.stderr.strip()}"
            )

        # Aguarda até 5 segundos pelo encerramento
        for _ in range(10):

            time.sleep(0.5)

            if not self.ganso_esta_aberto():
                logger.success("Ganso fechado com sucesso.")
                return True

        # Se ainda estiver aberto, força o encerramento
        logger.warning(
            "Ganso não encerrou normalmente. "
            "Forçando encerramento..."
        )

        subprocess.run(
            ["taskkill", "/F", "/IM", "Ganso.exe"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        # Aguarda o Windows finalizar completamente o processo
        time.sleep(2)

        # Confirma novamente
        if self.ganso_esta_aberto():
            logger.error(
                "Não foi possível fechar o Ganso.exe."
            )
            return False

        logger.success("Ganso encerrado com sucesso.")

        return True

    def abrir(
        self,
        timeout=TIMEOUT_ABERTURA_GANSO,
        intervalo=2
    ):
        """
        Garante que o Ganso está aberto, iniciando o executável
        se necessário.
        """

        if self.esta_aberto():
            logger.info("Ganso já está aberto.")
            return

        logger.info(
            f"Abrindo o Ganso ({self.caminho_executavel})..."
        )

        subprocess.Popen(self.caminho_executavel)

        inicio = time.time()

        while (time.time() - inicio) < timeout:

            self._fechar_aviso_atencao()

            if self.esta_aberto():
                logger.success("Ganso abriu.")

                self._fazer_login()

                return

            time.sleep(intervalo)

        raise TimeoutError(
            f"Ganso não abriu em {timeout}s."
        )

    def _fechar_aviso_atencao(self):
        """
        Fecha a janela de aviso 'ATENÇÃO' que costuma aparecer
        antes da tela de login, se ela estiver na tela.
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

                logger.info(
                    f"Aviso detectado ('{titulo}'), fechando..."
                )

                botao_ok = None

                for filho in janela.children():

                    if (
                        filho.window_text() == "OK"
                        and filho.friendly_class_name() == "Button"
                    ):
                        botao_ok = filho
                        break

                if botao_ok is not None:

                    botao_ok.click()

                else:

                    # Fallback: não achou o botão OK
                    # tenta pelo teclado
                    janela.set_focus()

                    time.sleep(0.3)

                    janela.type_keys("{ENTER}")

                time.sleep(0.5)

                logger.success("Aviso fechado.")

                return

        except Exception as e:

            logger.debug(
                f"Nenhum aviso encontrado ou erro ao fechar: {e}"
            )

    def _fazer_login(self):
        """
        Preenche usuário e senha na tela de login do Ganso.
        """

        logger.info("Realizando login no Ganso...")

        janela_login = None

        inicio = time.time()

        while (time.time() - inicio) < 10:

            self._fechar_aviso_atencao()

            try:

                app_login = Application(
                    backend="win32"
                ).connect(
                    class_name="TFrmAcesso"
                )

                candidata = app_login.window(
                    class_name="TFrmAcesso"
                )

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

        janela_login.wait(
            "visible",
            timeout=10
        )

        janela_login.set_focus()

        # Dá tempo da janela terminar de ganhar foco
        time.sleep(1)

        # Usuário
        janela_login.type_keys(
            LOGIN_GANSO,
            with_spaces=True
        )

        time.sleep(0.3)

        # Campo de senha
        janela_login.type_keys("{TAB}")

        time.sleep(0.3)

        # Senha
        janela_login.type_keys(
            SENHA_GANSO,
            with_spaces=True
        )

        time.sleep(0.3)

        # Envia formulário
        janela_login.type_keys(
            "{ENTER}{ENTER}"
        )

        logger.success("Login enviado.")

    def conectar_principal(self):

        logger.info(
            "Conectando à janela principal do Ganso..."
        )

        self.app = Application(
            backend="win32"
        ).connect(
            class_name="TFrmPrincipalGanso"
        )

        self.janela_principal = self.app.window(
            class_name="TFrmPrincipalGanso"
        )

        self.janela_principal.set_focus()

        logger.success(
            "Janela principal encontrada."
        )

    def abrir_gerador_balanca(self):

        logger.info(
            "Abrindo Gerar Arquivo para Balança..."
        )

        self.janela_principal.set_focus()

        time.sleep(1)

        try:

            # ALT + U
            self.janela_principal.type_keys(
                "%u",
                pause=0.2
            )

        finally:

            # Garante que o Alt seja solto
            send_keys("{VK_MENU up}")

        time.sleep(1)

        # Navegação já testada:
        # 13 DOWN
        for _ in range(13):

            self.janela_principal.type_keys(
                "{DOWN}"
            )

            time.sleep(0.3)

        self.janela_principal.type_keys(
            "{ENTER}"
        )

        logger.success(
            "Janela de exportação aberta."
        )

        time.sleep(1)

    def conectar_exportacao(self):

        logger.info(
            "Conectando à janela de exportação..."
        )

        self.app = Application(
            backend="win32"
        ).connect(
            title_re=".*Gerar Arquivo para Balança.*"
        )

        self.janela_exportacao = self.app.top_window()

        self.janela_exportacao.set_focus()

        logger.success(
            "Janela localizada."
        )

    def gerar_arquivo_balanca(self):

        logger.info("Gerando arquivo...")

        self.janela_exportacao.child_window(
            title="&Confirma",
            class_name="TButton"
        ).click()

        time.sleep(2)

        # Localiza a janela da mensagem de sucesso
        msg = self.app.window(
            title_re="ATEN.*"
        )

        msg.wait(
            "visible",
            timeout=10
        )

        logger.success(
            "Mensagem de confirmação encontrada."
        )

        # Dá foco na janela
        msg.set_focus()

        time.sleep(0.5)

        # Confirma a mensagem
        msg.type_keys("{ENTER}")

        time.sleep(2)

        logger.success(
            "Arquivo gerado e confirmado."
        )

        # Fecha janela de exportação
        send_keys("{ESC}")

        # Fecha janela principal do Ganso
        send_keys("^{F11}")

        logger.success(
            "Janela de exportação e janela principal "
            "fechadas."
        )