from pywinauto import Desktop

print("=" * 60)
print("JANELAS ABERTAS (win32)")
print("=" * 60)

desktop = Desktop(backend="win32")

for janela in desktop.windows():
    try:
        titulo = janela.window_text()
        classe = janela.friendly_class_name()

        if titulo:
            print(f"Titulo: {titulo!r}  |  Classe: {classe}")
    except Exception:
        pass

print("=" * 60)
print("Fim da lista.")