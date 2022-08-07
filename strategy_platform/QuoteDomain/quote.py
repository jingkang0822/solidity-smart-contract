import configsettings as cs
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
import pytz
from dataclasses import dataclass
from typing import Callable
import enumerator
from tickscollector import TicksCollector
import utildomain as ud
import threading
from logger import AppLog


@dataclass
class Quote:
    config_settings: cs.ConfigSettings
    k_bar_callback_handler: Callable[[pd.Series], None]
    is_hist_complete_callback_handler: Callable[[], None]
    df_k_bars: pd.DataFrame = None
    ticks_collector: TicksCollector = None
    data_feed_thread: threading.Thread = None
    lock = threading.Lock()

    def __post_init__(self):
        self.ticks_collector = TicksCollector(self.config_settings)

    def start(self):

        self.historical_data()

        if self.config_settings.trading_mode == enumerator.TradingMode.LIVE:
            self.data_feed_thread = threading.Thread(target=self.update_real_time_k_bar)
            self.data_feed_thread.name = 'Thread-quote'
            self.data_feed_thread.start()

    def historical_data(self):
        start_t = ud.dt_to_unix(self.config_settings.from_dt)
        end_t = ud.dt_to_unix(self.config_settings.to_dt)

        df_ticks = self.ticks_collector.get_ticks(start_t, end_t)
        self.df_k_bars = self.ticks_to_kbars(df_ticks)

        self.k_bar_callback(self.df_k_bars)
        self.is_hist_complete_callback_handler()

    def k_bar_callback(self, df_k_bars):
        self.lock.acquire()

        for index, row in df_k_bars.iterrows():
            self.k_bar_callback_handler(row)

        self.lock.release()

    def update_real_time_k_bar(self):

        try:
            min_interval = self.config_settings.get_k_bar_interval()

            last_bar_close = self.df_k_bars['timestamp_utc'].iloc[-1]
            next_bar_close = ud.last_k_bar_close(last_bar_close, min_interval) + timedelta(minutes=min_interval)

            while True:
                check_time = pytz.UTC.localize(datetime.utcnow())

                if check_time >= next_bar_close and self.wait_for_block_time(next_bar_close):

                    AppLog.logger().info(f'Triggering k bar updating.')
                    updated_ticks = self.ticks_collector.get_ticks(
                        ud.dt_to_unix(last_bar_close) + 1,
                        ud.dt_to_unix(next_bar_close)
                    )

                    if not updated_ticks.empty:
                        updated_k_bars = self.ticks_to_kbars(updated_ticks, len(self.df_k_bars))
                        self.df_k_bars = pd.concat([self.df_k_bars, updated_k_bars], ignore_index=False, axis=0)
                        self.k_bar_callback(updated_k_bars)
                        last_bar_close = self.df_k_bars['timestamp_utc'].iloc[-1]

                    next_bar_close = ud.last_k_bar_close(next_bar_close, min_interval) + timedelta(minutes=min_interval)
                    AppLog.logger().debug(f'Next bar close: {next_bar_close}')

                else:
                    time.sleep(5)

        except Exception as e:
            AppLog.logger().error(f'Exception: {e}')
            AppLog.logger().error(f'Stop real-time ticks updating.')

    def wait_for_block_time(self, target_time):
        while not self.if_device_time_meet_block_time(target_time):
            AppLog.logger().info(f'Waiting block time to {target_time}.')
            time.sleep(5)

        return True

    def if_device_time_meet_block_time(self, check_time):
        last_block_time = self.ticks_collector.swap_api.last_block_time()
        check_timestamp = ud.dt_to_unix(check_time)

        AppLog.logger().info(f'Block time: {datetime.fromtimestamp(last_block_time, pytz.timezone("UTC"))}, '
                             f'Check time: {datetime.fromtimestamp(check_timestamp, pytz.timezone("UTC"))}')

        if last_block_time >= check_timestamp:
            return True
        else:
            AppLog.logger().debug(f'Block time smaller than now.')
            return False

    @staticmethod
    def ticks_to_kbars(df_ticks, last_bar_number=0):

        df_kbars = df_ticks.groupby('timestamp_utc').last().reset_index()
        df_kbars['timestamp_unix'] = (pd.DatetimeIndex(df_kbars['timestamp_utc'])
                                      .astype(np.int64) / 1e9).values.astype(np.int64)
        df_kbars.rename(columns={'blockNumber': 'block_number'}, inplace=True)

        df_kbars['open'] = df_ticks.groupby('timestamp_utc').first().reset_index()['mid_price'].values
        df_kbars['high'] = df_ticks.groupby('timestamp_utc').agg({'mid_price': 'max'})['mid_price'].values
        df_kbars['low'] = df_ticks.groupby('timestamp_utc').agg({'mid_price': 'min'})['mid_price'].values
        df_kbars.rename(columns={'mid_price': 'close'}, inplace=True)

        df_kbars['up_volume'] = df_ticks.groupby('timestamp_utc').agg({'buy_amount': 'sum'})['buy_amount'].values
        df_kbars['down_volume'] = df_ticks.groupby('timestamp_utc').agg({'sell_amount': 'sum'})['sell_amount'].values
        df_kbars['volume'] = df_kbars.eval('up_volume+down_volume')

        df_kbars['bar_number'] = df_kbars.index + last_bar_number

        cols = ['timestamp_unix', 'timestamp_utc', 'block_number', 'bar_number', 'tick',
                'open', 'high', 'low', 'close', 'volume', 'up_volume', 'down_volume']

        return df_kbars[cols]
