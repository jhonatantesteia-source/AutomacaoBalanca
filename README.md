# AutomacaoBalanca

Automação desktop para exportar a lista de produtos do ERP Ganso e importar/transmitir a carga no MGV.

## Requisitos
- Windows com acesso às aplicações Ganso e MGV instaladas.
- Python 3.11+ recomendado (compatibilidade depende das versões de `pywinauto` e dos drivers do Windows).

## Instalação
1. Abra o PowerShell na pasta do projeto.
2. Crie o ambiente e instale dependências:
   ```powershell
   py -m venv .venv
   .venv\Scripts\python -m pip install --upgrade pip
   .venv\Scripts\python -m pip install -r requirements.txt
   ```
3. Copie `.env.example` para `.env` e configure caminhos, login e notificações.
4. Execute primeiro manualmente:
   ```powershell
   .venv\Scripts\python -m src.main
   ```
5. Depois de validar o fluxo, configure `AutomacaoBalanca.bat` no Agendador de Tarefas.

## Estrutura
- `src/main.py`: orquestração do caso de uso.
- `src/erp.py`: integração com a interface do Ganso.
- `src/balanca.py`: integração com a interface do MGV.
- `src/notificacao.py`: canais de notificação.
- `src/config.py`: leitura e validação de configuração local.
- `src/logger.py`: configuração de logs.

## Segurança
- Nunca compartilhe nem versione `.env`.
- Se credenciais foram compartilhadas, revogue-as e gere novas.
- Os logs podem conter nomes de telas e mensagens de erro; revise-os antes de compartilhar.

## Testes
Execute os testes unitários sem abrir o ERP ou o MGV:
```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```

## Limitações atuais
A integração com Ganso/MGV continua baseada em automação de interface gráfica. Mudanças de tela, foco ou permissões do Windows podem exigir ajustes. Antes de integrar módulos adicionais, extraia regras de negócio para serviços independentes da interface e cubra-as com testes unitários.
