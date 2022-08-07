from enum import Enum


class TradingMode(Enum):
    LIVE = 1
    BACKTEST = 2
    OPTIMIZE = 3


class SimulationDetail(Enum):
    K_BAR = 1
    TRADE = 2


class Chains(Enum):
    Ethereum = 'eth_mainnet'
    ArbitrumL2 = 'arbitrum'
    Polygon = 'polygon'
    Optimism = 'optimism'


class DEX(Enum):
    UniV3 = 1
    Perpetual = 2


class TradingAccount(Enum):
    TeaVaultBanqiao = 1
