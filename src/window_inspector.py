from pywinauto import Desktop
print("Janelas abertas:\n")
for window in Desktop(backend="uia").windows():
    try:
        titulo = janela.window_text()
        if titulo.strip():
            print(f"- {titulo}")
    except Exception:
        pass