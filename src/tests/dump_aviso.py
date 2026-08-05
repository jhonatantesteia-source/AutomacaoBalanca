from pywinauto import Desktop

encontrada = False

for janela in Desktop(backend="win32").windows():
    titulo = janela.window_text()

    if titulo and titulo.startswith("ATEN") and janela.friendly_class_name() == "Dialog":
        encontrada = True
        print("=" * 60)
        print(f"JANELA ENCONTRADA: {titulo!r}")
        print("=" * 60)

        print("\nTexto completo da janela:")
        print(janela.window_text())

        print("\nControles filhos:")
        for filho in janela.children():
            try:
                print(f"  Texto: {filho.window_text()!r}  |  Classe: {filho.friendly_class_name()}")
            except Exception as e:
                print(f"  (erro ao ler um controle: {e})")
        break

if not encontrada:
    print("Nenhuma janela com titulo iniciando em 'ATEN' e classe 'Dialog' foi encontrada.")
    print("Confirme se ela esta aberta e visivel no momento em que este script roda.")