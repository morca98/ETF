"""
ETF Signal Bot - Ficheiro Principal

Bot de trading para ETFs que envia sinais via Telegram.
"""

import logging
import schedule
import time
from datetime import datetime
from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    ETF_TICKERS,
    CHECK_INTERVAL_MINUTES,
    LOG_FILE,
    validate_config
)
from signal_generator import SignalGenerator
from telegram_notifier import TelegramNotifier

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ETFSignalBot:
    """Classe principal do bot de sinais de ETFs."""
    
    def __init__(self):
        """Inicializa o bot."""
        logger.info("Inicializando ETF Signal Bot...")
        
        # Validar configurações
        try:
            validate_config()
        except ValueError as e:
            logger.error(f"Erro de configuração: {str(e)}")
            raise
        
        # Inicializar componentes
        self.signal_generator = SignalGenerator()
        self.telegram_notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        self.is_running = False
        
        logger.info(f"Bot inicializado com sucesso")
        logger.info(f"Tickers a monitorizar: {ETF_TICKERS}")
        logger.info(f"Intervalo de verificação: {CHECK_INTERVAL_MINUTES} minutos")
    
    def check_signals(self):
        """Verifica sinais para todos os ETFs configurados."""
        logger.info(f"Verificando sinais para {len(ETF_TICKERS)} ETFs...")
        
        signals = self.signal_generator.check_all_signals(ETF_TICKERS)
        
        if signals:
            logger.info(f"Encontrados {len(signals)} sinais")
            for signal in signals:
                self._send_signal(signal)
        else:
            logger.debug("Nenhum sinal encontrado")
    
    def _send_signal(self, signal):
        """
        Envia um sinal via Telegram.
        
        Args:
            signal (dict): Dicionário com informações do sinal
        """
        try:
            success = self.telegram_notifier.send_signal_message_sync(signal)
            if success:
                logger.info(f"Sinal enviado para {signal['ticker']}")
            else:
                logger.error(f"Falha ao enviar sinal para {signal['ticker']}")
        except Exception as e:
            logger.error(f"Erro ao enviar sinal para {signal['ticker']}: {str(e)}")
    
    def schedule_checks(self):
        """Agenda as verificações periódicas de sinais."""
        schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(self.check_signals)
        logger.info(f"Verificações agendadas a cada {CHECK_INTERVAL_MINUTES} minutos")
    
    def run(self):
        """Executa o bot em loop contínuo."""
        logger.info("Iniciando loop de execução do bot...")
        self.is_running = True
        
        # Agendar verificações
        self.schedule_checks()
        
        # Executar verificação inicial
        logger.info("Executando verificação inicial...")
        self.check_signals()
        
        # Loop principal
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot interrompido pelo utilizador")
            self.stop()
        except Exception as e:
            logger.error(f"Erro no loop principal: {str(e)}")
            self.stop()
    
    def stop(self):
        """Para o bot."""
        logger.info("Parando o bot...")
        self.is_running = False
        logger.info("Bot parado com sucesso")
    
    def test_telegram_connection(self):
        """Testa a conexão com o Telegram."""
        logger.info("Testando conexão com Telegram...")
        success = self.telegram_notifier.send_test_message_sync()
        
        if success:
            logger.info("✅ Conexão com Telegram bem-sucedida")
        else:
            logger.error("❌ Falha na conexão com Telegram")
        
        return success


def main():
    """Função principal."""
    try:
        # Criar e inicializar o bot
        bot = ETFSignalBot()
        
        # Testar conexão com Telegram
        if not bot.test_telegram_connection():
            logger.warning("Aviso: Não foi possível conectar ao Telegram, mas o bot continuará em execução")
        
        # Executar o bot
        bot.run()
    
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        raise


if __name__ == "__main__":
    main()
