from pywinauto import Desktop

print("=" * 60)
print("JANELAS ABERTAS")
print("=" * 60)

desktop = Desktop(backend="uia")

for janela in desktop.windows():
    try:
        titulo = janela.window_text()

        if titulo:
            print(f"\nJanela: {titulo}")
            print("-" * 60)

            try:
                janela.print_control_identifiers()
            except Exception as e:
                print("Não foi possível listar os controles:", e)

    except Exception:
        pass