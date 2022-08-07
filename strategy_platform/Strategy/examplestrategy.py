import configsettings as cs
import strategybuilder as sb
import enumerator
import utildomain as ud
from datetime import datetime
from datetime import timedelta
import numpy
import logging
from logger import create_logger
create_logger(True, True, logging.INFO)


timer = ud.TimeWatch()


config_settings = cs.ConfigSettings(
    chain=enumerator.Chains.Ethereum,
    pool_address='0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8',
    dex=enumerator.DEX.UniV3,
    trading_mode=enumerator.TradingMode.BACKTEST,
    simulation_detail=enumerator.SimulationDetail.TRADE,
    from_dt=datetime(2022, 3, 10),
    to_dt=datetime(2022, 3, 29),
    data_mode=ud.DataSettings(if_need_kbars=True, kbars_interval=timedelta(minutes=60)),
)
config_settings.set_token_initial_amount('USDC', 100000)
config_settings.set_token_base('USDC')


# Define customized class inherit from sb.StrategyBuilder
class ExampleStrategy(sb.StrategyBuilder):

    # Will trigger once the k bar feed
    def strategy_k_bar_updated(self):

        # The history data include in this variable: self.k_bars
        if len(self.k_bars) >= self.parameters['look_back']:
            # catch the length of array with the close price
            arr = numpy.array(self.k_bars['close'][-self.parameters['look_back']:])

            # calculate moving average
            sma = numpy.mean(arr, axis=0)

            # calculate moving standard deviation
            std = numpy.std(arr, axis=0)

            # interval of bollinger band
            upper_bound = round((sma + self.parameters['std_multiply'] * std) / 200) * 200
            lower_bound = round((sma - self.parameters['std_multiply'] * std) / 200) * 200

            # if upper is not the same as lower and do not have lp, then provide liquidity
            if upper_bound != lower_bound:
                self.set_liquidity(lower_bound, upper_bound)

            # if upper is same as lower and do have lp, then remove liquidity
            elif upper_bound == lower_bound:
                self.set_liquidity(None)


example_strategy = ExampleStrategy(
    config_settings=config_settings,
    parameters={
        'look_back': 20,
        'std_multiply': 4,
    }
)
example_strategy.start()
example_strategy.generate_report(plot_performance=True, write_report=True)

timer.elapsed_time()
