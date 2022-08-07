import copy
import os
from multiprocessing import Pool
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pytz
from Strategy.banqiao_builder import BanqiaoBuilder
import utildomain as ud
import configsettings as cs
import enumerator
import logging
from logger import create_logger
from tqdm import tqdm


if __name__ == '__main__':

    create_logger(True, False, logging.INFO)
    timer = ud.TimeWatch()

    config_settings = cs.ConfigSettings(
        chain=enumerator.Chains.Ethereum,
        pool_address='0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8',
        dex=enumerator.DEX.UniV3,
        trading_mode=enumerator.TradingMode.BACKTEST,
        simulation_detail=enumerator.SimulationDetail.TRADE,
        from_dt=datetime(2022, 1, 1),
        to_dt=datetime(2022, 4, 6),
        fee_api_domain='http://office.teahouse.finance:10001',
        data_mode=ud.DataSettings(if_need_kbars=True, kbars_interval=timedelta(hours=4)),
    )
    config_settings.set_token_initial_amount('USDC', 100000)
    config_settings.set_token_base('USDC')

    parallel_objs = []

    i = 0
    date_list = list(ud.date_range(datetime(2021, 6, 1, 4), datetime(2021, 6, 3, 5), timedelta(hours=4)))
    low_prob_arr = [0.03]
    df = pd.DataFrame(index=low_prob_arr, columns=date_list)

    for date_from in tqdm(date_list, desc='Initial Date'):
        pnl_in_date = []
        for low_prob in low_prob_arr:
            i += 1
            config_settings.from_dt = pytz.utc.localize(date_from)
            config_settings.fee_api_domain = f'http://office.teahouse.finance:1000{i%8+1}'
            banqiao_builder = BanqiaoBuilder(
                config_settings=copy.deepcopy(config_settings),
                low_prob_set=low_prob,
            )
            parallel_objs.append(banqiao_builder)
            banqiao_builder.start()
            pnl_in_date.append(banqiao_builder.pnl())

        df[date_from] = pnl_in_date

    config_settings.set_report_path('BanqiaoOptimize')
    df.to_csv(
        os.path.join(
            config_settings.report_folder,
            f'grid_search_{config_settings.to_dt.strftime("%Y%m%d")}.csv'),
        index=True
    )

    # pool = Pool(9)
    # pool.map(BanqiaoBuilder.start, parallel_objs)

    timer.elapsed_time()
