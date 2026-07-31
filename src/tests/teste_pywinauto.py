from pywinauto.application import Application
import subprocess
import time

# Abre o Bloco de Notas
subprocess.Popen("notepad.exe")

time.sleep(2)

# Conecta ao programa
app = Application(backend="uia").connect(title_re=".*Bloco de Notas.*|.*Notepad.*")

janela = app.top_window()

print(f"Título encontrado: {janela.window_text()}")