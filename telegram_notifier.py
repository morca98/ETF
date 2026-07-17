"""
Módulo de Notificação via Telegram

Envia mensagens de sinais para o Telegram.
"""

import logging
from telegram import Bot
from telegram.error import TelegramError
import asyncio

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Classe responsável por enviar notificações via Telegram."""
    
    def __init__(self, bot_token, chat_id):
        """
        Inicializa o TelegramNotifier.
        
        Args:
            bot_token (str): Token de acesso do bot do Telegram
            chat_id (str): ID do chat ou canal para enviar mensagens
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
    
    async def send_signal_message(self, signal):
        """
        Envia uma mensagem de sinal para o Telegram.
        
        Args:
            signal (dict): Dicionário com informações do sinal
        
        Returns:
            bool: True se a mensagem foi enviada com sucesso, False caso contrário
        """
        try:
            message = self._format_signal_message(signal)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Mensagem de sinal enviada para {signal['ticker']}")
            return True
        except TelegramError as e:
            logger.error(f"Erro ao enviar mensagem para Telegram: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar mensagem: {str(e)}")
            return False
    
    def send_signal_message_sync(self, signal):
        \"\"\"
        Versão síncrona de send_signal_message.
        
        Args:
            signal (dict): Dicionário com informações do sinal
        
        Returns:
            bool: True se a mensagem foi enviada com sucesso, False caso contrário
        \"\"\"
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.send_signal_message(signal))
    
    def _format_signal_message(self, signal):
        """
        Formata a mensagem de sinal para o Telegram.
        
        Args:
            signal (dict): Dicionário com informações do sinal
        
        Returns:
            str: Mensagem formatada em HTML
        """
        ticker = signal['ticker']
        entry_price = signal['entry_price']
        target_price = signal['target_price']
        stop_loss = signal['stop_loss']
        upside = signal['upside_percentage']
        daily_low = signal['daily_low']
        
        message = f"""
<b>🚀 NOVO SINAL DE COMPRA</b>

<b>Ticker:</b> <code>{ticker}</code>
<b>Tipo:</b> BUY

<b>Preços:</b>
├ <b>Entrada:</b> ${entry_price:.2f}
├ <b>Alvo:</b> ${target_price:.2f}
├ <b>Stop-Loss:</b> ${stop_loss:.2f}
└ <b>Mínima do Dia:</b> ${daily_low:.2f}

<b>Análise:</b>
├ <b>Upside:</b> <b>{upside:.2f}%</b>
└ <b>Risk/Reward:</b> {self._calculate_rr(entry_price, target_price, stop_loss):.2f}

<b>Timestamp:</b> {signal['timestamp']}

⚠️ <i>Sempre use stop-loss e gerencie o risco adequadamente.</i>
"""
        return message.strip()
    
    def _calculate_rr(self, entry, target, stop_loss):
        """
        Calcula o rácio risco/recompensa.
        
        Args:
            entry (float): Preço de entrada
            target (float): Preço alvo
            stop_loss (float): Preço de stop-loss
        
        Returns:
            float: Rácio risco/recompensa
        """
        if entry == stop_loss:
            return 0
        
        reward = target - entry
        risk = entry - stop_loss
        
        if risk == 0:
            return 0
        
        return reward / risk
    
    async def send_test_message(self):
        """Envia uma mensagem de teste para verificar a conexão."""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text="✅ Bot do Telegram conectado com sucesso!"
            )
            logger.info("Mensagem de teste enviada com sucesso")
            return True
        except TelegramError as e:
            logger.error(f"Erro ao enviar mensagem de teste: {str(e)}")
            return False
    
    def send_test_message_sync(self):
        \"\"\"Versão síncrona de send_test_message.\"\"\"
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.send_test_message())


if __name__ == "__main__":
    # Teste do módulo
    import os
    from dotenv import load_dotenv
    
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Erro: TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados")
    else:
        notifier = TelegramNotifier(bot_token, chat_id)
        
        # Enviar mensagem de teste
        print("Enviando mensagem de teste...")
        success = notifier.send_test_message_sync()
        
        if success:
            print("✅ Mensagem de teste enviada com sucesso!")
        else:
            print("❌ Erro ao enviar mensagem de teste")
