import copy
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math
import time
import pandas as pd
import pytz


@dataclass
class DataSettings:
    if_need_ticks: bool = False
    if_need_kbars: bool = False
    kbars_interval: timedelta = timedelta(minutes=1)


@dataclass
class TokenSettings:
    name: str = ''
    address: str = ''
    decimals: int = None
    amount: float = 0

    def long_int_amount(self):
        return int(self.amount * 10 ** self.decimals)

    def new_instance_by_amount(self, amount):
        instance = copy.deepcopy(self)
        instance.amount = amount
        return instance


@dataclass
class KBar:
    timestamp_unix: int
    timestamp_utc: datetime
    block_number: int
    bar_number: int

    # price_0: token1 / token0
    open_0: float
    high_0: float
    low_0: float
    close_0: float
    volume_0: float
    up_volume_0: float
    down_volume_0: float

    # price_1: token0 / token1
    open_1: float
    high_1: float
    low_1: float
    close_1: float
    volume_1: float
    up_volume_1: float
    down_volume_1: float


class TimeWatch:
    def __init__(self):
        self.start_time = time.time()

    def elapsed_time(self):
        time_lapsed = time.time() - self.start_time

        minutes = time_lapsed // 60
        seconds = time_lapsed % 60
        hours = minutes // 60
        minutes = minutes % 60
        print('Time elapsed = {0}:{1:02d}:{2:06.3f}'.format(int(hours), int(minutes), seconds))


def price_to_tick_base(config_settings, price):
    return round_tick_by_tick_base(
        price_to_tick(config_settings, price), config_settings.tick_spacing
    )


def price_to_tick(config_settings, price):
    if config_settings.token_reverse():
        price = 1 / price

    return int(math.log(price / 10 ** config_settings.token_ten_base(), 1.0001))


def tick_to_price(config_settings, tick):
    if config_settings.token_reverse():
        return 1 / (1.0001 ** tick * 10 ** config_settings.token_ten_base())
    else:
        return 1.0001 ** tick * 10 ** config_settings.token_ten_base()


def round_tick_by_tick_base(tick, tick_spacing):
    return round(tick / tick_spacing) * tick_spacing


def ordering_lower_upper(lower, upper):
    if lower > upper:
        return upper, lower
    else:
        return lower, upper


def folder_exists_or_create(folder):
    if not os.path.exists(folder):
        # Create a new directory if it does not exist
        os.makedirs(folder)


def dt_to_unix(dt):
    return int((dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())


def get_last_k_bar_close_by_initial(initial_time, min_interval):
    first_close = first_k_bar_close(initial_time, min_interval)
    last_close = last_k_bar_close(first_close, min_interval)

    return last_close


def first_k_bar_close(first_time, min_interval):
    frequency = '{}min'.format(min_interval)
    df = pd.DataFrame({'dt_obj': [first_time]})
    return df.dt_obj.dt.ceil(frequency).iloc[0]


def last_k_bar_close(last_time, min_interval):
    checked_time = pytz.UTC.localize(datetime.utcnow())
    while last_time + timedelta(minutes=min_interval) < checked_time:
        last_time += timedelta(minutes=min_interval)

    return last_time


def date_range(start, end, step):
    while start < end:
        yield start
        start += step
