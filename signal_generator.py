"""
Módulo de Geração de Sinais

Implementa a lógica central de geração de sinais de trading.
"""

import json
import os
from datetime import datetime
import logging
from data_fetcher import DataFetcher
from config import MIN_UPSIDE_PERCENTAGE, TRADES_STATE_FILE

logger = logging.getLogger(__name__)

class SignalGenerator:
    """Classe responsável por gerar sinais de trading."""
    
    def __init__(self, trades_state_file=TRADES_STATE_FILE):
        """
        Inicializa o SignalGenerator.
        
        Args:
            trades_state_file (str): Caminho para o ficheiro de estado dos trades
        """
        self.trades_state_file = trades_state_file
        self.data_fetcher = DataFetcher()
        self.trades_state = self._load_trades_state()
    
    def _load_trades_state(self):
        """Carrega o estado dos trades ativos a partir do ficheiro."""
        if os.path.exists(self.trades_state_file):
            try:
                with open(self.trades_state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar estado dos trades: {str(e)}")
                return {}
        return {}
    
    def _save_trades_state(self):
        """Guarda o estado dos trades ativos no ficheiro."""
        try:
            with open(self.trades_state_file, 'w') as f:
                json.dump(self.trades_state, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao guardar estado dos trades: {str(e)}")
    
    def has_active_trade(self, ticker):
        """
        Verifica se há um trade ativo para um dado ticker.
        
        Args:
            ticker (str): Ticker do ETF
        
        Returns:
            bool: True se há trade ativo, False caso contrário
        """
        return ticker in self.trades_state and self.trades_state[ticker].get('active', False)
    
    def set_active_trade(self, ticker, entry_price, target_price, stop_loss=None):
        """
        Marca um trade como ativo para um dado ticker.
        
        Args:
            ticker (str): Ticker do ETF
            entry_price (float): Preço de entrada
            target_price (float): Preço alvo
            stop_loss (float): Preço de stop-loss (opcional)
        """
        self.trades_state[ticker] = {
            'active': True,
            'entry_price': entry_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'signal_timestamp': datetime.now().isoformat()
        }
        self._save_trades_state()
        logger.info(f"Trade ativo registado para {ticker}: Entrada={entry_price}, Alvo={target_price}")
    
    def close_trade(self, ticker):
        """
        Marca um trade como fechado para um dado ticker.
        
        Args:
            ticker (str): Ticker do ETF
        """
        if ticker in self.trades_state:
            self.trades_state[ticker]['active'] = False
            self._save_trades_state()
            logger.info(f"Trade fechado para {ticker}")
    
    def check_signal(self, ticker):
        """
        Verifica se há um sinal de compra para um dado ticker.
        
        Args:
            ticker (str): Ticker do ETF
        
        Returns:
            dict: Dicionário com informações do sinal ou None se não há sinal
        """
        # Verificar se há trade ativo
        if self.has_active_trade(ticker):
            logger.debug(f"Trade ativo já existe para {ticker}, ignorando")
            return None
        
        # Obter dados do ETF
        etf_data = self.data_fetcher.get_etf_data(ticker)
        if etf_data is None:
            logger.warning(f"Não foi possível obter dados para {ticker}")
            return None
        
        current_price = etf_data['current_price']
        today_low = etf_data['today_low']
        target = etf_data['target']
        
        # Calcular upside percentual
        upside_percentage = ((target - current_price) / current_price) * 100
        
        logger.debug(f"{ticker}: Preço={current_price:.2f}, Mínima={today_low:.2f}, Alvo={target:.2f}, Upside={upside_percentage:.2f}%")
        
        # Verificar se o upside é maior que o mínimo requerido
        if upside_percentage > MIN_UPSIDE_PERCENTAGE:
            # Calcular stop-loss (abaixo da mínima do dia)
            stop_loss = today_low * 0.99  # 1% abaixo da mínima
            
            signal = {
                'ticker': ticker,
                'type': 'BUY',
                'entry_price': current_price,
                'target_price': target,
                'stop_loss': stop_loss,
                'upside_percentage': upside_percentage,
                'daily_low': today_low,
                'timestamp': datetime.now().isoformat()
            }
            
            # Registar o trade como ativo
            self.set_active_trade(ticker, current_price, target, stop_loss)
            
            logger.info(f"Sinal gerado para {ticker}: Entrada={current_price:.2f}, Alvo={target:.2f}, Upside={upside_percentage:.2f}%")
            return signal
        
        return None
    
    def check_all_signals(self, tickers):
        """
        Verifica sinais para todos os tickers na lista.
        
        Args:
            tickers (list): Lista de tickers a verificar
        
        Returns:
            list: Lista de sinais gerados
        """
        signals = []
        for ticker in tickers:
            signal = self.check_signal(ticker)
            if signal:
                signals.append(signal)
        
        return signals


if __name__ == "__main__":
    # Teste do módulo
    logging.basicConfig(level=logging.INFO)
    
    generator = SignalGenerator()
    
    # Testar verificação de sinal para SPY
    signal = generator.check_signal("SPY")
    
    if signal:
        print("\n=== SINAL GERADO ===")
        print(f"Ticker: {signal['ticker']}")
        print(f"Tipo: {signal['type']}")
        print(f"Entrada: ${signal['entry_price']:.2f}")
        print(f"Alvo: ${signal['target_price']:.2f}")
        print(f"Stop-Loss: ${signal['stop_loss']:.2f}")
        print(f"Upside: {signal['upside_percentage']:.2f}%")
    else:
        print("Nenhum sinal gerado para SPY")
