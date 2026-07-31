from pywinauto.application import Application
import time

# Conecta à janela "Gerar Arquivo para Balança"
app = Application(backend="win32").connect(
    title_re=".*Gerar Arquivo para Balança.*"
)

janela = app.top_window()

# Dá foco
janela.set_focus()

time.sleep(1)

# Clica em Confirma
janela.child_window(
    title="&Confirma",
    class_name="TButton"
).click()

print("Botão Confirma acionado.")