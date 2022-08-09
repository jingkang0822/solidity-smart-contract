import configsettings as cs
import strategybuilder as sb
import enumerator
import utildomain as ud
from datetime import datetime
from datetime import timedelta


timer = ud.TimeWatch()

config_settings = cs.ConfigSettings(
    chain=enumerator.Chains.Ethereum,
    pool_address='0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8',
    dex=enumerator.DEX.UniV3,
    trading_mode=enumerator.TradingMode.BACKTEST,
    from_dt=datetime(2021, 9, 1),
    to_dt=datetime(2021, 11, 1),
    data_mode=ud.DataSettings(if_need_ticks=True, if_need_kbars=True, kbars_interval=timedelta(minutes=60)),
    trading_account=enumerator.TradingAccount.TeaVaultBanqiao
)
config_settings.set_token_initial_amount('USDC', 100000)
config_settings.set_token_base('USDC')


class RandomStrategy(sb.StrategyBuilder):

    def strategy_k_bar_updated(self):
        d1 = 1.3
        d2 = 1.05
        close = self.k_bars["close"].values[-1]

        upper_bound = close * d1
        lower_bound = close / d1

        change_upper_bound = close * d2
        change_lower_bound = close / d2

        if not self.do_have_lp():
            self.change_upper_bound = change_upper_bound
            self.change_lower_bound = change_lower_bound
            self.set_liquidity(lower_bound, upper_bound)

        elif (close > self.change_upper_bound or close < self.change_lower_bound) and self.do_have_lp():
            self.set_liquidity(None)


example_strategy = RandomStrategy(
    config_settings=config_settings,
    parameters={
        'look_back': 20,
        'std_multiply': 4,
    }
)
example_strategy.start()
example_strategy.generate_report(plot_performance=True, write_report=True)

timer.elapsed_time()
