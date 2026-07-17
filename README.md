# ETF Signal Bot

Um bot de trading automatizado que monitora ETFs e envia sinais de compra via Telegram. O bot utiliza dados financeiros em tempo real do Yahoo Finance para identificar oportunidades de trading com base em critérios técnicos específicos.

## Características

- **Monitorização de Múltiplos ETFs**: Acompanha uma lista configurável de tickers.
- **Lógica de Sinais Inteligente**: Gera sinais apenas quando não há trades ativos e o potencial de upside é superior a 1%.
- **Integração com Telegram**: Envia notificações formatadas com detalhes completos do sinal.
- **Gestão de Estado**: Rastreia trades ativos para evitar sinais duplicados.
- **Logging Detalhado**: Regista todas as atividades para depuração e auditoria.

## Requisitos

- Python 3.8+
- Conexão com a Internet
- Token de um bot do Telegram
- ID do chat/canal do Telegram

## Instalação

### 1. Clonar o Repositório

```bash
git clone <url_do_repositorio>
cd etf_signal_bot
```

### 2. Criar um Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Copiar o ficheiro `.env.example` para `.env` e preenchê-lo com as suas configurações:

```bash
cp .env.example .env
```

Editar o ficheiro `.env`:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
ETF_TICKERS=["SPY", "QQQ", "IWM"]
MIN_UPSIDE_PERCENTAGE=1.0
CHECK_INTERVAL_MINUTES=5
```

## Configuração do Telegram

### Criar um Bot no Telegram

1. Abrir o Telegram e procurar por `@BotFather`.
2. Enviar o comando `/start`.
3. Enviar `/newbot` e seguir as instruções para criar um novo bot.
4. Copiar o **Token de Acesso** fornecido.

### Obter o Chat ID

1. Criar um chat privado ou grupo no Telegram.
2. Adicionar o bot ao chat/grupo.
3. Enviar uma mensagem qualquer.
4. Aceder a `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates` (substituir `<SEU_TOKEN>` pelo token do bot).
5. Procurar pelo `chat.id` na resposta JSON.

Alternativamente, usar um bot como `@userinfobot` para obter o seu ID de utilizador.

## Uso

### Executar o Bot

```bash
python main.py
```

O bot começará a monitorizar os ETFs configurados e enviará sinais via Telegram quando as condições forem satisfeitas.

### Testar a Configuração

Para testar se a configuração do Telegram está correta:

```bash
python -c "from telegram_notifier import TelegramNotifier; from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID; TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID).send_test_message_sync()"
```

## Estrutura do Projeto

```
etf_signal_bot/
├── main.py                 # Ficheiro principal do bot
├── config.py               # Carregamento de configurações
├── data_fetcher.py         # Recolha de dados financeiros
├── signal_generator.py     # Lógica de geração de sinais
├── telegram_notifier.py    # Envio de mensagens via Telegram
├── requirements.txt        # Dependências do projeto
├── .env.example            # Exemplo de configuração
├── .env                    # Configuração real (não fazer commit)
├── trades_state.json       # Estado dos trades ativos (gerado automaticamente)
├── bot.log                 # Ficheiro de log (gerado automaticamente)
└── README.md               # Este ficheiro
```

## Lógica de Sinais

O bot gera um sinal de compra quando as seguintes condições são satisfeitas:

1. **Sem Trade Ativo**: Não há nenhum trade aberto para o ETF.
2. **Potencial de Upside**: A diferença percentual entre o alvo (máxima dos últimos 2 dias) e o preço atual é superior a `MIN_UPSIDE_PERCENTAGE`.

### Cálculo do Sinal

- **Entrada**: Preço atual do ETF.
- **Alvo**: Máxima dos últimos 2 dias (excluindo o dia atual).
- **Stop-Loss**: 1% abaixo da mínima do dia.
- **Upside**: Percentagem de valorização esperada até ao alvo.

## Exemplo de Mensagem de Sinal

```
🚀 NOVO SINAL DE COMPRA

Ticker: SPY
Tipo: BUY

Preços:
├ Entrada: $450.00
├ Alvo: $456.00
├ Stop-Loss: $449.00
└ Mínima do Dia: $449.50

Análise:
├ Upside: 1.33%
└ Risk/Reward: 6.00

Timestamp: 2024-01-15T10:30:00

⚠️ Sempre use stop-loss e gerencie o risco adequadamente.
```

## Gestão de Trades

O bot mantém um registo de todos os trades ativos no ficheiro `trades_state.json`. Quando um sinal é gerado, o trade é marcado como ativo. Para fechar um trade manualmente:

1. Editar o ficheiro `trades_state.json`.
2. Alterar `"active": true` para `"active": false` para o ticker desejado.

## Logging

Todos os eventos do bot são registados no ficheiro `bot.log` e também exibidos na consola. Consulte o ficheiro de log para depuração e auditoria.

## Melhorias Futuras

- Suporte para múltiplos canais/chats do Telegram.
- Integração com brokers para execução automática de trades.
- Análise técnica mais avançada (RSI, MACD, etc.).
- Dashboard web para monitorização em tempo real.
- Gestão de risco avançada (posição sizing, correlação de ativos).

## Avisos Importantes

⚠️ **Este bot é fornecido como está, sem garantias**. O trading envolve risco significativo de perda financeira. Sempre:

- Use stop-loss para gerir o risco.
- Comece com pequenas posições.
- Teste o bot em ambiente de simulação antes de usar com dinheiro real.
- Não dependa exclusivamente do bot para decisões de trading.

## Suporte

Para problemas ou sugestões, abra uma issue no repositório do GitHub.

## Licença

Este projeto está licenciado sob a Licença MIT. Consulte o ficheiro LICENSE para detalhes.
