from pywinauto import Application

app = Application(backend="win32").connect(title_re=".*Gerar Arquivo para Balança.*")

janela = app.top_window()

print("=" * 80)
print("JANELA ENCONTRADA")
print("=" * 80)

print(janela.window_text())

print("\n")
print("=" * 80)
print("CONTROLES")
print("=" * 80)

janela.print_control_identifiers()