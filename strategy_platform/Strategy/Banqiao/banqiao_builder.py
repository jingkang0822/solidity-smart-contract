from dataclasses import dataclass
import configsettings as cs
from Strategy.Banqiao.banqiao import Banqiao
from Strategy.Banqiao.hetgp import HetGP


@dataclass
class BanqiaoBuilder:
    config_settings: cs.ConfigSettings
    low_prob_set: float
    strategy: Banqiao = None

    def __post_init__(self):
        my_max_tick_width = 5000
        my_quoted_token = 'token1'
        my_detection_freq = 24
        my_sampling_interval = 4
        my_param = {
            'n': 37,
            'q_set': 0.97,
            'low_prob_set': self.low_prob_set,
            'high_prob_set': 1,
        }
        k_bars_length = int(my_param['n'] * (24 / my_sampling_interval))

        trading_signals = HetGP(
            config_settings=self.config_settings,
            params=my_param,
            detection_freq=my_detection_freq,
            sampling_interval=my_sampling_interval,
            max_tick_width=my_max_tick_width,
            quoted_token=my_quoted_token
        )
        self.strategy = Banqiao(
            config_settings=self.config_settings,
            parameters=my_param,
            trading_signals=trading_signals,
            k_bars_length=k_bars_length,
        )

    def start(self):
        self.strategy.start()
        self.strategy.generate_report(plot_performance=False, write_report=False)

    def pnl(self):
        return self.strategy.total_pnl
