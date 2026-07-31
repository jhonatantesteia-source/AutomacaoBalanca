from erp import ERP
from logger import logger

logger.info("Iniciando automação")

erp = ERP()

erp.conectar_exportacao()

erp.gerar_arquivo_balanca()

logger.success("Processo finalizado")