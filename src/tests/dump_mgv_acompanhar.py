from time import sleep
from pywinauto import Desktop
from loguru import logger

desktop = Desktop(backend="uia")

logger.info("Aguardando o diálogo aparecer...")
sleep(2)

for janela in desktop.windows():
    print("=" * 100)
    print("Título:", repr(janela.window_text()))
    print("AutomationId:", janela.element_info.automation_id)
    print("Classe:", janela.class_name())

    try:
        janela.print_control_identifiers()
    except Exception as e:
        print("Erro:", e)