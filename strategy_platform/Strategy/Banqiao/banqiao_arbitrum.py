import configsettings as cs
import enumerator
import utildomain as ud
from datetime import datetime
from datetime import timedelta
from Banqiao.hetgp import HetGP
import logging
from Strategy.banqiao import Banqiao
from logger import create_logger
create_logger(True, True, logging.DEBUG)


timer = ud.TimeWatch()

config_settings = cs.ConfigSettings(
    chain=enumerator.Chains.ArbitrumL2,
    # pool_address='0x17c14D2c404D167802b16C450d3c99F88F2c4F4d', # 0.3%
    pool_address='0xC31E54c7a869B9FcBEcc14363CF510d1c41fa443', # 0.05%
    dex=enumerator.DEX.UniV3,
    trading_mode=enumerator.TradingMode.BACKTEST,
    simulation_detail=enumerator.SimulationDetail.TRADE,
    from_dt=datetime(2021, 9, 15, 4),
    to_dt=datetime(2022, 4, 13),
    data_mode=ud.DataSettings(if_need_kbars=True, kbars_interval=timedelta(hours=4)),
)
config_settings.set_token_initial_amount('USDC', 100000)
config_settings.set_token_base('USDC')

my_max_tick_width = 5000
my_quoted_token = 'token1'
my_detection_freq = 24
my_sampling_interval = 4
my_param = {
    'n': 70,
    'q_set': 0.999999,
    'low_prob_set': 0.09,
    'high_prob_set': 1,
}
k_bars_length = int(my_param['n'] * (24 / my_sampling_interval))

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
