"""
Módulo de Recolha de Dados Financeiros

Utiliza yfinance para obter dados históricos e em tempo real dos ETFs.
"""

import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataFetcher:
    """Classe responsável por obter dados financeiros dos ETFs."""
    
    def __init__(self):
        """Inicializa o DataFetcher."""
        self.cache = {}
        self.cache_timestamp = {}
        self.cache_ttl_seconds = 300  # Cache válido por 5 minutos
    
    def _is_cache_valid(self, ticker):
        """Verifica se o cache para um ticker ainda é válido."""
        if ticker not in self.cache_timestamp:
            return False
        
        elapsed = (datetime.now() - self.cache_timestamp[ticker]).total_seconds()
        return elapsed < self.cache_ttl_seconds
    
    def get_historical_data(self, ticker, period="5d"):
        """
        Obtém dados históricos (OHLCV) para um dado ticker e período.
        
        Args:
            ticker (str): Ticker do ETF (ex: "SPY")
            period (str): Período de histórico (ex: "5d", "1mo")
        
        Returns:
            pd.DataFrame: DataFrame com dados OHLCV ou None se houver erro
        """
        try:
            etf = yf.Ticker(ticker)
            hist = etf.history(period=period)
            
            if hist.empty:
                logger.warning(f"Nenhum dado histórico obtido para {ticker}")
                return None
            
            return hist
        except Exception as e:
            logger.error(f"Erro ao obter dados históricos para {ticker}: {str(e)}")
            return None
    
    def get_daily_low(self, ticker):
        """
        Obtém a mínima do dia atual para um ETF.
        
        Args:
            ticker (str): Ticker do ETF
        
        Returns:
            float: Mínima do dia ou None se houver erro
        """
        try:
            hist = self.get_historical_data(ticker, period="5d")
            
            if hist is None or len(hist) == 0:
                return None
            
            # A última linha é o dia atual
            today_low = hist['Low'].iloc[-1]
            return float(today_low)
        except Exception as e:
            logger.error(f"Erro ao obter mínima do dia para {ticker}: {str(e)}")
            return None
    
    def get_current_price(self, ticker):
        """
        Obtém o preço atual (último preço de fecho disponível) de um ETF.
        
        Args:
            ticker (str): Ticker do ETF
        
        Returns:
            float: Preço atual ou None se houver erro
        """
        try:
            hist = self.get_historical_data(ticker, period="5d")
            
            if hist is None or len(hist) == 0:
                return None
            
            # A última linha é o dia atual
            current_price = hist['Close'].iloc[-1]
            return float(current_price)
        except Exception as e:
            logger.error(f"Erro ao obter preço atual para {ticker}: {str(e)}")
            return None
    
    def get_max_high_last_n_days(self, ticker, n_days=2):
        """
        Calcula a máxima dos últimos n_days (excluindo o dia atual).
        
        Args:
            ticker (str): Ticker do ETF
            n_days (int): Número de dias anteriores a considerar
        
        Returns:
            float: Máxima dos últimos n_days ou None se houver erro
        """
        try:
            # Obter dados suficientes (n_days + 1 para excluir hoje)
            hist = self.get_historical_data(ticker, period=f"{n_days + 2}d")
            
            if hist is None or len(hist) < n_days + 1:
                logger.warning(f"Dados insuficientes para {ticker} (esperado {n_days + 1}, obtido {len(hist) if hist is not None else 0})")
                return None
            
            # Pegar nos últimos n_days, excluindo o dia atual (iloc[-1])
            # Se n_days=2, queremos iloc[-3:-1] (dia -2 e dia -1, excluindo dia 0)
            max_high = hist['High'].iloc[-(n_days + 1):-1].max()
            return float(max_high)
        except Exception as e:
            logger.error(f"Erro ao obter máxima dos últimos {n_days} dias para {ticker}: {str(e)}")
            return None
    
    def get_etf_data(self, ticker):
        """
        Obtém todos os dados necessários para análise de um ETF.
        
        Args:
            ticker (str): Ticker do ETF
        
        Returns:
            dict: Dicionário com dados do ETF ou None se houver erro
        """
        try:
            current_price = self.get_current_price(ticker)
            today_low = self.get_daily_low(ticker)
            target = self.get_max_high_last_n_days(ticker, n_days=2)
            
            if any(x is None for x in [current_price, today_low, target]):
                logger.error(f"Não foi possível obter todos os dados para {ticker}")
                return None
            
            return {
                "ticker": ticker,
                "current_price": current_price,
                "today_low": today_low,
                "target": target,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter dados do ETF {ticker}: {str(e)}")
            return None


if __name__ == "__main__":
    # Teste do módulo
    logging.basicConfig(level=logging.INFO)
    
    fetcher = DataFetcher()
    data = fetcher.get_etf_data("SPY")
    
    if data:
        print(f"Ticker: {data['ticker']}")
        print(f"Preço Atual: ${data['current_price']:.2f}")
        print(f"Mínima de Hoje: ${data['today_low']:.2f}")
        print(f"Alvo (Máxima 2 dias): ${data['target']:.2f}")
        upside = (data['target'] - data['current_price']) / data['current_price'] * 100
        print(f"Upside: {upside:.2f}%")
