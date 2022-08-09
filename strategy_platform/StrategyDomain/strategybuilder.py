import os
import enumerator
import quote as qd
import configsettings as cs
import ledgerdomain as ld
import utildomain as ud
from TradeSignal import tradesignal as ts
from dataclasses import dataclass
import pandas as pd
import performancechart
import copy
from logger import AppLog


@dataclass
class StrategyBuilder:
    config_settings: cs.ConfigSettings
    parameters: {} = None
    quote_domain: qd.Quote = None
    ledger: ld.Ledger = None
    ticks: pd.DataFrame = pd.DataFrame()
    k_bars: pd.DataFrame = pd.DataFrame()
    trade_signal: ts.TradeSignal = None
    is_hist_complete: bool = False
    total_pnl: float = 0

    def __post_init__(self):
        self.quote_domain = qd.Quote(
            config_settings=self.config_settings,
            k_bar_callback_handler=self.k_bar_callback,
            is_hist_complete_callback_handler=self.is_hist_complete_callback
        )
        self.ledger = ld.Ledger(
            config_settings=self.config_settings,
            strategy_name=self.__class__.__name__
        )
        self.trade_signal = ts.TradeSignal(
            time_stamp=0,
            block_number=0,
            tick=0,
            config_settings=self.config_settings
        )

    def start(self):
        self.quote_domain.start()

        if self.config_settings.trading_mode == enumerator.TradingMode.LIVE:
            self.console_gen_report()

    def k_bar_callback(self, k_bar):
        self.trade_signal.reset_signal(k_bar)
        self.k_bars = self.quote_domain.df_k_bars[:k_bar['bar_number']+1]
        self.strategy_k_bar_updated()
        self.ledger.feed_signal(self.trade_signal)

    def ticks_callback(self, tick):
        pass

    def strategy_k_bar_updated(self):
        pass

    def strategy_ticks_updated(self):
        pass

    def is_hist_complete_callback(self):
        AppLog.logger().info('Simulating in historical data complete.')
        self.is_hist_complete = True

        if self.config_settings.trading_mode == enumerator.TradingMode.LIVE:
            self.ledger.register_signal_sender()

    def set_liquidity(self, lower_price=None, upper_price=None):
        if lower_price and upper_price:
            if not self.do_have_lp():
                self._add_liquidity(lower_price, upper_price)

            elif not self.is_same_range(lower_price, upper_price):
                self._remove_liquidity()
                self.trade_signal.time_stamp += 1
                self.trade_signal.block_number += 1
                self._add_liquidity(lower_price, upper_price)

        else:
            if self.do_have_lp():
                self._remove_liquidity()

    def _add_liquidity(self, lower_price, upper_price):
        lower_tick, upper_tick = self.get_range_tick(lower_price, upper_price)

        if lower_tick != upper_tick:
            self.trade_signal.lower_tick = lower_tick
            self.trade_signal.upper_tick = upper_tick
            self.trade_signal.event = ts.Liquidity.ADD
            self.ledger.feed_signal(self.trade_signal)

    def _remove_liquidity(self):
        self.trade_signal.event = ts.Liquidity.REMOVE
        self.ledger.feed_signal(self.trade_signal)

    def do_have_lp(self):
        if self.trade_signal and self.trade_signal.lower_tick:
            return True
        else:
            return False

    def is_same_range(self, lower_price, upper_price):
        if self.trade_signal.upper_tick and self.trade_signal.lower_tick:
            lower_tick, upper_tick = self.get_range_tick(lower_price, upper_price)
            if lower_tick == self.trade_signal.lower_tick and upper_tick == self.trade_signal.upper_tick:
                return True
        else:
            return False

    def get_range_tick(self, lower_price, upper_price):
        lower_tick = ud.price_to_tick_base(self.config_settings, lower_price)
        upper_tick = ud.price_to_tick_base(self.config_settings, upper_price)

        return ud.ordering_lower_upper(lower_tick, upper_tick)

    def console_gen_report(self):
        while True:
            if input('Generate report? (Y/N)').lower() == 'y':
                self.generate_report(True, True)
                AppLog.logger().info('Generate report success.')

    def generate_report(self, plot_performance=False, write_report=False):
        self.config_settings.set_report_path(self.__class__.__name__)

        instant_ledger = copy.deepcopy(self.ledger)
        instant_ledger.add_remove_if_do_have_position(self.k_bars.iloc[-1])
        self.total_pnl = instant_ledger.df_ledger()['amm_pnl(%)'].iloc[-1]

        if plot_performance:
            performancechart.plot(ledger=instant_ledger)

        if write_report:
            instant_ledger.df_ledger().to_csv(
                os.path.join(self.config_settings.report_folder, 'df_ledger.csv'), index=0
            )
            instant_ledger.trade_list().to_csv(
                os.path.join(self.config_settings.report_folder, 'trade_list.csv'), index=0
            )
