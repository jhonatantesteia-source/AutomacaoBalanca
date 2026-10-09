from pywinauto import Desktop

print("Janelas encontradas:\n")

desktop = Desktop(backend="win32")

for w in desktop.windows():
    try:
        titulo = w.window_text()
        if titulo.strip():
            print("=" * 80)
            print(titulo)
    except Exception:
        pass