import subprocess
import time 

import pyautogui
from loguru import logger

def testar_bloco_notas():
    logger.info("Abrindo bloco de notas")

    subprocess.Popen("notepad.exe")

    time.sleep(2)

    pyautogui.write(
        "Primeiro teste de automacao em python",
        interval=0.03
    )

    logger.info("Texto digitado")