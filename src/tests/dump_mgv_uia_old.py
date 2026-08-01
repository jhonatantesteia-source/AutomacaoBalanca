from pywinauto import Desktop

#app = Application(backend="uia").connect(
#    title_re=r".*MGV 7 (Standard) - Loja 0001 - MERCADO PAULISTANO.*"
#    )

for w in Desktop(backend="uia").windows():
    print(repr(w.window_text()))

#janela = app.top_window()

#janela.print_control_identifiers()