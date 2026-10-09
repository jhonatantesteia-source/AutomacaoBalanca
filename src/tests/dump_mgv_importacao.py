from pywinauto import Desktop
from loguru import logger
import time

janela = Desktop(backend="uia").window(
    title_re=".*MGV 7.*"
)

janela.wait("ready")

botao = janela.child_window(
    title="Importação",
    control_type="Button"
)

botao2 = janela.child_window(
    title="btnSalvar",
    control_type="Button"
)

print(botao)

try:
    botao.invoke()
    print("Invoke OK")

    #time.sleep(1)

    botao2.invoke()
    print("Invoke 2 OK")

    time.sleep(1)

    # Clica no botão "ENTER" (botão padrao da janela)
   #  msg.type_keys("{ENTER}")

except Exception as e:
    print("Invoke falhou:", e)

#try:
    botao.click_input()
    print("Click OK")
#except Exception as e:
    print("Click falhou:", e)