from pywinauto.application import Application

app = Application(backend="uia").connect(
    title_re=".*MGV 7 (Standard) - Loja 0001 - MERCADO PAULISTANO.*"
    )

janela = app.top_window()

for ctrl in janela.descendants():
    try:
        print(
            ctrl.window_text(),
            "|",
            ctrl.friendly_class_name(),
            "|",
            ctrl.rectangle(),
        )
    except:
        pass