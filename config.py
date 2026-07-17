"""
Módulo de Configuração do ETF Signal Bot

Carrega as configurações do bot a partir de variáveis de ambiente.
"""

import os
from dotenv import load_dotenv
import json

# Carregar variáveis de ambiente do ficheiro .env
load_dotenv()

# Configurações do Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Configurações de Trading
ETF_TICKERS = json.loads(os.getenv('ETF_TICKERS', '["SPY", "QQQ"]'))
MIN_UPSIDE_PERCENTAGE = float(os.getenv('MIN_UPSIDE_PERCENTAGE', '1.0'))
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '5'))

# Configurações de Ficheiros
TRADES_STATE_FILE = os.getenv('TRADES_STATE_FILE', 'trades_state.json')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# Validar configurações críticas
def validate_config():
    """Valida as configurações críticas do bot."""
    errors = []
    
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN não está configurado")
    
    if not TELEGRAM_CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID não está configurado")
    
    if not ETF_TICKERS or len(ETF_TICKERS) == 0:
        errors.append("ETF_TICKERS está vazio")
    
    if errors:
        raise ValueError(f"Erros de configuração:\n" + "\n".join(errors))
    
    return True

if __name__ == "__main__":
    print("Configurações do ETF Signal Bot:")
    print(f"Telegram Bot Token: {'***' if TELEGRAM_BOT_TOKEN else 'NÃO CONFIGURADO'}")
    print(f"Telegram Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"ETF Tickers: {ETF_TICKERS}")
    print(f"Upside Mínimo: {MIN_UPSIDE_PERCENTAGE}%")
    print(f"Intervalo de Verificação: {CHECK_INTERVAL_MINUTES} minutos")
