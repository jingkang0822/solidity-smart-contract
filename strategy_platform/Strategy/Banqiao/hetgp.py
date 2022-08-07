import os
import rpy2.robjects as r_obj
from rpy2.robjects.packages import STAP
from rpy2.robjects import pandas2ri
from dataclasses import dataclass, field
import configsettings as cs


class RConnector:
    r_agent: r_obj.packages.SignatureTranslatedAnonymousPackage = None


@dataclass
class HetGP:

    config_settings: cs.ConfigSettings
    detection_freq: int
    sampling_interval: int
    max_tick_width: int
    quoted_token: str
    params: dict = field(default_factory=dict)
    r_agent: r_obj.packages.SignatureTranslatedAnonymousPackage = None
    t0: str = None
    t1: str = None
    lower_price: int = 0
    upper_price: int = 0

    def __post_init__(self):
        pandas2ri.activate()
        if not RConnector.r_agent:
            with open('r_hetGP/live_trading.R', 'r') as f:
                rlib_str = f.read()
                r_obj.r(rlib_str)
                RConnector.r_agent = STAP(rlib_str, 'orz')
                RConnector.r_agent.set_working_env(os.path.join(os.getcwd()))

        self.r_agent = RConnector.r_agent
        self.t = str(self.config_settings.to_dt)
        self.params = pandas2ri.DataFrame(self.params)

    def get_price_range(self, k_bar_data):

        df_r = pandas2ri.DataFrame(k_bar_data)

        lp_range = self.r_agent.live_trading_signals(
            self.t, df_r, self.params, self.detection_freq,
            self.sampling_interval, self.config_settings.tick_spacing, self.max_tick_width,
            self.config_settings.token_0.decimals, self.config_settings.token_1.decimals, self.quoted_token,
            self.lower_price, self.upper_price
        )
        self.lower_price, self.upper_price = lp_range[0], lp_range[1]
        return self.lower_price, self.upper_price
