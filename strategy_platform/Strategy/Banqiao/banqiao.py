from dataclasses import dataclass
import configsettings as cs
import strategybuilder as sb
import enumerator
import utildomain as ud
from datetime import datetime
from datetime import timedelta
import logging
from Strategy.Banqiao.hetgp import HetGP
from logger import create_logger


# Define customized class inherit from sb.StrategyBuilder
@dataclass
class Banqiao(sb.StrategyBuilder):
    trading_signals: HetGP = None
    k_bars_length: int = None
    trigger_interval: int = None

    # Will trigger once the k bar feed
    def strategy_k_bar_updated(self):

        # The history data include in this variable: self.k_bars
        if len(self.k_bars) >= self.k_bars_length and len(self.k_bars) % self._trigger_interval() == 0:
            # catch the length of array with the close price
            df = self.k_bars[-self.k_bars_length:]
            lower_bound, upper_bound = self.trading_signals.get_price_range(df)
            self.set_liquidity(lower_bound, upper_bound)

    def _trigger_interval(self):
        if not self.trigger_interval:
            self.trigger_interval = int(24 / (self.config_settings.get_k_bar_interval() / 60))

        return self.trigger_interval


if __name__ == '__main__':
    create_logger(True, False, logging.DEBUG)
    timer = ud.TimeWatch()

    my_detection_freq = 24
    my_sampling_interval = 4

    config_settings = cs.ConfigSettings(
        chain=enumerator.Chains.Ethereum,
        pool_address='0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8',
        dex=enumerator.DEX.UniV3,
        trading_mode=enumerator.TradingMode.BACKTEST,
        simulation_detail=enumerator.SimulationDetail.TRADE,
        from_dt=datetime(2021, 6, 1),
        to_dt=datetime(2022, 4, 6),
        data_mode=ud.DataSettings(if_need_kbars=True, kbars_interval=timedelta(minutes=60 * my_sampling_interval)),
    )
    config_settings.set_token_initial_amount('USDC', 100000)
    config_settings.set_token_base('USDC')

    my_max_tick_width = 5000
    my_quoted_token = 'token1'
    my_param = {
        'n': 37,
        'q_set': 0.95,
        'low_prob_set': 0.02,
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
