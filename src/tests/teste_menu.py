from pywinauto.application import Application
import time

app = Application(backend="win32").connect(
    title_re=".*Ganso Gestão Empresarial.*"
)

janela = app.top_window()
janela.set_focus()

time.sleep(1)

# ALT + U (Utilitários)
janela.type_keys("%u", pause=0.2)

time.sleep(1)

# Desce até a opção
janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)

janela.type_keys("{DOWN}")
time.sleep(0.3)


janela.type_keys("{ENTER}")