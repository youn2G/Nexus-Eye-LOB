"""
Order Book Data Generator
Génère des données simulées pour le carnet d'ordres (LOB)
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple
import random


@dataclass
class OrderBookData:
    """Structure de données pour le carnet d'ordres"""
    bids: pd.DataFrame  # Prix et volumes des ordres d'achat
    asks: pd.DataFrame  # Prix et volumes des ordres de vente
    mid_price: float    # Prix mid (moyenne bid/ask)


def generate_order_book(
    mid_price: float = 100.0,
    spread_bps: float = 10.0,
    n_levels: int = 20,
    base_volume: float = 1000.0,
    volatility: float = 0.02
) -> OrderBookData:
    """
    Génère un carnet d'ordres simulé avec bids et asks.
    
    Args:
        mid_price: Prix central de référence
        spread_bps: Spread bid-ask en basis points
        n_levels: Nombre de niveaux de prix de chaque côté
        base_volume: Volume de base par niveau
        volatility: Volatilité des volumes
    
    Returns:
        OrderBookData contenant bids, asks et mid_price
    """
    spread = mid_price * (spread_bps / 10000)
    
    # Générer les prix bid (décroissants depuis mid - spread/2)
    bid_prices = np.array([
        mid_price - spread/2 - (i * spread * 0.5) 
        for i in range(n_levels)
    ])
    
    # Générer les prix ask (croissants depuis mid + spread/2)
    ask_prices = np.array([
        mid_price + spread/2 + (i * spread * 0.5) 
        for i in range(n_levels)
    ])
    
    # Générer les volumes avec distribution exponentielle décroissante
    # Plus on s'éloigne du mid, moins il y a de volume (réaliste)
    bid_volumes = base_volume * np.exp(-0.1 * np.arange(n_levels)) * (1 + volatility * np.random.randn(n_levels))
    ask_volumes = base_volume * np.exp(-0.1 * np.arange(n_levels)) * (1 + volatility * np.random.randn(n_levels))
    
    # S'assurer que les volumes sont positifs
    bid_volumes = np.maximum(bid_volumes, 10)
    ask_volumes = np.maximum(ask_volumes, 10)
    
    # Calculer les volumes cumulés pour le depth chart
    bid_cumulative = np.cumsum(bid_volumes)
    ask_cumulative = np.cumsum(ask_volumes)
    
    bids = pd.DataFrame({
        'price': bid_prices,
        'volume': bid_volumes,
        'cumulative': bid_cumulative
    })
    
    asks = pd.DataFrame({
        'price': ask_prices,
        'volume': ask_volumes,
        'cumulative': ask_cumulative
    })
    
    return OrderBookData(bids=bids, asks=asks, mid_price=mid_price)


def generate_trade_history(
    mid_price: float = 100.0,
    n_trades: int = 10,
    volatility: float = 0.001
) -> pd.DataFrame:
    """
    Génère un historique de trades simulé.
    
    Args:
        mid_price: Prix de référence
        n_trades: Nombre de trades à générer
        volatility: Volatilité des prix
    
    Returns:
        DataFrame avec colonnes: time, side, price, volume, value
    """
    now = datetime.now()
    
    trades = []
    for i in range(n_trades):
        # Timestamp décroissant (plus récent en premier)
        timestamp = now - timedelta(seconds=i * random.uniform(0.5, 3.0))
        
        # Side aléatoire (BUY/SELL)
        side = random.choice(['BUY', 'SELL'])
        
        # Prix autour du mid avec volatilité
        price = mid_price * (1 + volatility * np.random.randn())
        
        # Volume aléatoire
        volume = round(random.uniform(10, 500), 2)
        
        # Valeur totale
        value = round(price * volume, 2)
        
        trades.append({
            'time': timestamp.strftime('%H:%M:%S.%f')[:-3],
            'side': side,
            'price': round(price, 4),
            'volume': volume,
            'value': value
        })
    
    return pd.DataFrame(trades)


def update_mid_price(current_mid: float, volatility: float = 0.0005) -> float:
    """
    Met à jour le prix mid avec un mouvement brownien.
    
    Args:
        current_mid: Prix mid actuel
        volatility: Volatilité du mouvement
    
    Returns:
        Nouveau prix mid
    """
    return current_mid * (1 + volatility * np.random.randn())
