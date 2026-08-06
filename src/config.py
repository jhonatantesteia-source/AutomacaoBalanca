"""
Configuracoes do ambiente - caminhos dos executaveis usados quando os
programas precisam ser abertos do zero (execucao agendada, sem
ninguem para abrir manualmente).

TODO: ajustar os caminhos abaixo para os caminhos reais nesta maquina.
"""


CAMINHO_GANSO = r"C:\Ganso\Ganso.exe"
CAMINHO_MGV = r"C:\Program Files (x86)\Toledo do Brasil\MGV 7\MGV7Central.exe"

# Tempo maximo de espera (segundos) para cada programa terminar de abrir.
TIMEOUT_ABERTURA_GANSO = 15
TIMEOUT_ABERTURA_MGV = 20

LOGIN_GANSO = "jhonatan"
SENHA_GANSO = "5466"

# --- Aviso via WhatsApp (CallMeBot) ---
# Cada numero que vai RECEBER avisos precisa se ativar SEPARADAMENTE
# no proprio WhatsApp (a API Key e unica por numero):
#   1. Adicione o contato +34 644 78 13 70
#      (confira o numero atual em
#       https://www.callmebot.com/blog/free-api-whatsapp-messages/)
#   2. Envie a mensagem: "I allow callmebot to send me messages"
#   3. Anote a API Key que ESSE numero recebeu.
# Repita para cada numero da lista abaixo.
CALLMEBOT_DESTINATARIOS = [
    # {"telefone": "5511999999999", "apikey": "123456"},
    # {"telefone": "5511888888888", "apikey": "654321"},
]

# --- Aviso via E-mail (Gmail / SMTP) ---
# EMAIL_REMETENTE: a conta Gmail que vai ENVIAR o aviso.
# EMAIL_SENHA_APP: senha de app gerada em
#   https://myaccount.google.com/apppasswords
#   (exige verificacao em duas etapas ativada na conta).
#   NAO e a senha normal da conta Gmail.
# EMAIL_DESTINATARIO: quem vai RECEBER o aviso (pode ser o mesmo e-mail
#   do remetente, ou o e-mail do responsavel).
EMAIL_REMETENTE = "jhonatan.teste.ia@gmail.com"
EMAIL_SENHA_APP = "hbzmuomzgrnozndh"
EMAIL_DESTINATARIO = "nelsonramon1395@gmail.com"