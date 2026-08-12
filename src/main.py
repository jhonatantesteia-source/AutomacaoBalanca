from erp import ERP
from balanca import Balanca, FalhaTransmissaoBalanca
from logger import logger
from notificacao import enviar_whatsapp, enviar_email


def main():
    try:
        logger.info("Iniciando automação")

        erp = ERP()

        # Garante que não exista uma instância anterior do Ganso
        if not erp.garantir_ganso_fechado():
            raise RuntimeError(
                "Não foi possível garantir que o Ganso está fechado."
            )

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

        enviar_whatsapp(
            "✅ Automação da balança concluída com sucesso! "
            "Arquivo gerado e carga enviada para todas as balanças."
        )

        enviar_email(
            assunto="✅ Automação da balança concluída com sucesso",
            mensagem=(
                "O arquivo da balança foi gerado e a carga foi enviada "
                "com sucesso para todas as balanças."
            ),
        )

    except FalhaTransmissaoBalanca as e:
        logger.exception(f"Erro durante a automação: {e}")

        balancas = ", ".join(e.balancas_com_falha)

        enviar_whatsapp(
            f"⚠️ Falha na comunicação com a(s) balança(s): {balancas}.\n"
            "O restante do processo (arquivo gerado, carga enviada) "
            "ocorreu normalmente. Verifique/reinicie a(s) balança(s) indicada(s)."
        )

        enviar_email(
            assunto="⚠️ Falha de comunicação em balança(s)",
            mensagem=(
                f"A carga foi enviada, mas houve falha na comunicação com a(s) "
                f"seguinte(s) balança(s): {balancas}.\n\n"
                "O restante do processo ocorreu normalmente. Verifique/reinicie "
                "a(s) balança(s) indicada(s) e, se necessário, refaça o envio."
            ),
        )

    except Exception as e:
        logger.exception(f"Erro durante a automação: {e}")

        enviar_whatsapp(f"⚠️ Falha na automação da balança: {e}")

        enviar_email(
            assunto="⚠️ Falha na automação da balança",
            mensagem=(
                f"A automação da balança falhou com o seguinte erro:\n\n{e}"
            ),
        )


if __name__ == "__main__":
    main()