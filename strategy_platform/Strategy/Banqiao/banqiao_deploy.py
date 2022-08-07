import sys
sys.path.extend([
    'D:\\Teahouse Source Code\\tea_strategy_platform',
    'D:\\Teahouse Source Code\\tea_strategy_platform\\TradeSignal',
    'D:\\Teahouse Source Code\\tea_strategy_platform\\StrategyDomain',
    'D:\\Teahouse Source Code\\tea_strategy_platform\\PerformanceDomain',
    'D:\\Teahouse Source Code\\tea_strategy_platform\\API',
    'D:\\Teahouse Source Code\\tea_strategy_platform\\API\\TeaVaultAPI',
    'D:\\Teahouse Source Code\\tea_strategy_platform\\CommonUtil',
    'D:\\Teahouse Source Code\\tea_strategy_platform\\LedgerDomain',
    'D:\\Teahouse Source Code\\tea_strategy_platform\\QuoteDomain'
])
from Strategy.Banqiao.banqiao import Banqiao
from Strategy.Banqiao.hetgp import HetGP
import configsettings as cs
import enumerator
import utildomain as ud
from datetime import datetime
from datetime import timedelta
import logging
from logger import create_logger
create_logger(True, True, logging.DEBUG)


timer = ud.TimeWatch()

my_detection_freq = 24
my_sampling_interval = 4

config_settings = cs.ConfigSettings(
    chain=enumerator.Chains.Ethereum,
    pool_address='0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8',
    dex=enumerator.DEX.UniV3,
    trading_mode=enumerator.TradingMode.LIVE,
    simulation_detail=enumerator.SimulationDetail.TRADE,
    from_dt=datetime(2021, 6, 6, 8),
    to_dt=datetime(2023, 4, 6),
    data_mode=ud.DataSettings(if_need_kbars=True, kbars_interval=timedelta(hours=my_sampling_interval)),
)
config_settings.set_token_initial_amount('USDC', 100000)
config_settings.set_token_base('USDC')

my_max_tick_width = 5000
my_quoted_token = 'token1'
my_param = {
    'n': 37,
    'q_set': 0.997,
    'low_prob_set': 0.07,
    'high_prob_set': 1,
}
k_bars_length = int(my_param['n'] * 24 / my_sampling_interval)

trading_signals = HetGP(
    config_settings=config_settings,
    params=my_param,
    detection_freq=my_detection_freq,
    sampling_interval=my_sampling_interval,
    max_tick_width=my_max_tick_width,
    quoted_token=my_quoted_token
)


banqiao_strategy = Banqiao(
    config_settings=config_settings,
    parameters=my_param,
    trading_signals=trading_signals,
    k_bars_length=k_bars_length,
)
banqiao_strategy.start()
banqiao_strategy.generate_report(plot_performance=True, write_report=True)

timer.elapsed_time()
