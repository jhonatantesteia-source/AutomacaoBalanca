"""Configuração única de logs para execução manual ou agendada."""
from loguru import logger

from src.config import ROOT_DIR

LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(
    LOG_DIR / "automacao.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
    encoding="utf-8",
    enqueue=True,
    backtrace=False,
    diagnose=False,
)
logger.add(lambda message: print(message, end=""), level="INFO", backtrace=False, diagnose=False)
