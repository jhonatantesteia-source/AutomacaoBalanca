from pywinauto import Desktop

janela = Desktop(backend="win32").window(
    title_re=".*MGV 7.*"
)

janela.set_focus()

print("=" * 80)
print(janela.window_text())
print("=" * 80)

for ctrl in janela.descendants():
    try:
        print(
            ctrl.window_text(),
            "|",
            ctrl.friendly_class_name(),
            "|",
            ctrl.rectangle()
        )
    except Exception:
        pass