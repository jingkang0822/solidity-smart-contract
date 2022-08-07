import threading
from dataclasses import dataclass
import numpy as np
import configsettings as cs
from datetime import datetime
import pandas as pd
from enumerator import TradingMode
from swapapi import SwapAPI
import pytz
from logger import AppLog


class TickStorage:
    ticks: dict = {}


@dataclass
class TicksCollector:

    config_settings: cs.ConfigSettings
    specific_pool_address: str = None
    swap_api: SwapAPI = None
    lock = threading.Lock()

    def __post_init__(self):
        self.swap_api = SwapAPI(
            config_settings=self.config_settings,
            pool_address=self.config_settings.pool_address
            if not self.specific_pool_address else self.specific_pool_address
        )

    def get_ticks(self, start_t, end_t):
        AppLog.logger().info(f'get ticks data: {datetime.fromtimestamp(start_t, pytz.timezone("UTC"))} - '
                             f'{datetime.fromtimestamp(end_t, pytz.timezone("UTC"))}')

        self.check_stored_ticks(start_t, end_t)

        ticks = TickStorage.ticks[self.config_settings.ticks_storage_key()]
        ticks = ticks.loc[(ticks['timestamp'] >= start_t) & (ticks['timestamp'] <= end_t)]

        return self.format_swap_data(ticks)

    def check_stored_ticks(self, start_t, end_t):
        self.lock.acquire()

        if self.config_settings.trading_mode == TradingMode.LIVE or \
                self.config_settings.ticks_storage_key() not in TickStorage.ticks:
            TickStorage.ticks[self.config_settings.ticks_storage_key()] = self.swap_api.fetch_dex_tx(start_t, end_t)

        self.lock.release()

    def format_swap_data(self, df_ticks):

        if self.config_settings and not df_ticks.empty:

            # Filter data
            df_ticks = df_ticks.query('event=="Swap"').drop_duplicates(subset='txID')

            if not df_ticks.empty:

                # Fix amount float number
                token0_base = 10 ** self.config_settings.token_0.decimals
                token1_base = 10 ** self.config_settings.token_1.decimals
                ten_base = self.config_settings.token_ten_base()

                df_ticks = df_ticks.infer_objects()

                df_ticks.loc[:, 'amount0'] = df_ticks.loc[:, 'amount0'].astype(float) / token0_base
                df_ticks.loc[:, 'amount1'] = df_ticks.loc[:, 'amount1'].astype(float) / token1_base

                # Calculate price
                df_ticks['tick'] = df_ticks['tick'].values.astype(np.int64)

                if self.config_settings.token_reverse():
                    df_ticks['mid_price'] = df_ticks['sqrtPriceX96']\
                        .apply(lambda x: 1 / (((float(x) / 2 ** 96) ** 2) * 10 ** ten_base))
                else:
                    df_ticks['mid_price'] = df_ticks['sqrtPriceX96']\
                        .apply(lambda x: ((float(x) / 2 ** 96) ** 2) * 10 ** ten_base)

                # Calculate volume
                if self.config_settings.token_reverse():
                    col_volume = 'amount1'
                else:
                    col_volume = 'amount0'

                df_ticks['buy_amount'] = df_ticks[col_volume].apply(lambda x: x if x > 0 else 0)
                df_ticks['sell_amount'] = df_ticks[col_volume].apply(lambda x: -x if x < 0 else 0)

                # Format datetime
                frequency = f'{self.config_settings.get_k_bar_interval()}min'
                df_ticks['format_timestamp'] = df_ticks['timestamp'].apply(
                    lambda x: datetime.fromtimestamp(x, pytz.timezone('UTC'))
                )
                df_ticks['timestamp_utc'] = df_ticks['format_timestamp'].dt.ceil(frequency)

                df_ticks.reset_index(drop=True, inplace=True)
                return df_ticks
            else:
                AppLog.logger().info('No swap data after filter.')

        return pd.DataFrame()

    '''
    def save_dex_data(self, start_time, end_time, update):

        info = self.get_pool_info(self.config_settings.pool_address)
        if np.isnan(info['chain_id']) or info is None:
            file_path = None
        else:
            folder_name = '{}_{}'.format(info['token0_symbol'], info['token1_symbol'])
            base_path = os.path.join(os.getcwd(), 'pool_swap_data')
            folder_path = os.path.join(base_path, folder_name)
            if not os.path.exists(base_path):
                os.mkdir(base_path)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
            if start_time.date() != end_time.date():
                file_name = 'swap_data_' + str(start_time.date()) + '_' + str(end_time.date()) + '.ftr'
            else:
                file_name = 'swap_data_' + str(end_time.date()) + '.ftr'
            file_path = os.path.join(folder_path, file_name)

        cond1 = file_path is not None  # check if the pool data can be fetched
        cond2 = not os.path.isfile(file_path)  # check if the pool data has been saved

        # if update is True, then replace the original file.
        # if update is False, then first check if the file exists. if the file doesn't exist, then fetch the data and save the file
        if (update and cond1) or (cond1 and cond2):
            df = self.fetch_dex_tx_from_api(start_time, end_time)
            if df is None or len(df) == 0:
                print('Data fetching fails')
            else:
                dates = df['format_timestamp'].dt.date.unique()
                if dates[0] != start_time.date() or dates[-1] != end_time.date():
                    if dates[0] != dates[-1]:
                        update_file_name = 'swap_data_' + str(dates[0]) + '_' + str(dates[-1]) + '.ftr'
                    else:
                        update_file_name = 'swap_data_' + '_' + str(dates[-1]) + '.ftr'
                    update_file_path = os.path.join(folder_path, update_file_name)
                    df.to_feather(update_file_path)
                    return update_file_path
                else:
                    df.to_feather(file_path)
                    return file_path
        else:
            print('The file already exists.')

    def get_pool_info(self):

        url = 'http://office.teahouse.finance:8181/pools/info?network=eth_mainnet&pool={}'.format(
            self.config_settings.pool_address)
        response = requests.get(url)
        try:
            raw_data = response.json()
            if raw_data['success'] is True:
                return raw_data['data']
            else:
                return {'chain_id': np.nan, 'pool_address': self.config_settings.pool_address, 'fee': np.nan,
                        'tick_spacing': np.nan,
                        'token0_address': '', 'token1_address': '', 'token0_symbol': '', 'token0_decimals': np.nan,
                        'token1_decimals': np.nan}

        except Exception as e:
            print(e)
    '''
