from erp import ERP
from balanca import Balanca
from logger import logger

def main():
    try:
        logger.info("Iniciando automação")

        erp = ERP()

        erp.abrir()
        erp.conectar_principal()
        erp.abrir_gerador_balanca()
        erp.conectar_exportacao()
        erp.gerar_arquivo_balanca()

        balanca = Balanca()

        balanca.abrir()
        balanca.conectar()
        balanca.importar_arquivo()
        balanca.enviar_carga()

        logger.success("Processo concluído com sucesso!")

    except Exception as e:
        logger.exception(f"Erro durante a automação: {e}")


if __name__ == "__main__":
    main()