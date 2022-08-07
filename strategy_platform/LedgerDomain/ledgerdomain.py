import copy
from typing import Callable
import pandas as pd
import numpy as np
import pytz
import enumerator
import feeapi
import ilCalculator
import math
from datetime import datetime
import tradesignal as ts
from logger import AppLog
from signalmanager import SignalManager
import configsettings as cs


class Ledger:

    config_settings: cs.ConfigSettings
    signals_hist: pd.DataFrame = pd.DataFrame(columns=[
        'timestamp', 'block', 'tick', 'lower_tick', 'upper_tick', 'event'
    ])
    signal_manager: SignalManager = None
    send_signal_handler: Callable[[], None] = None

    def __init__(self, config_settings, strategy_name, is_copy=False):
        self.config_settings = config_settings
        self.network = config_settings.chain.value
        self.pool_address = config_settings.pool_address
        self.strategy_name = strategy_name

        self.base_symbol = None

        if config_settings.base_token == config_settings.token_0:
            self.target_token = config_settings.token_1.name
            self.base_token = config_settings.token_0.name
            self.initial_base_token_amount = config_settings.token_0.amount
        else:
            self.target_token = config_settings.token_0.name
            self.base_token = config_settings.token_1.name
            self.initial_base_token_amount = config_settings.token_1.amount

        self.S = None

        self.decimal_0 = None
        self.decimal_1 = None

        self.bars = 0
        self.trade_num = 0
        self.status = "off"
        self.trade_info = {}

        self.columns = ['timestamp', "block", 'tick', 'lower_tick', 'upper_tick', 'price', 'lower_price', 'upper_price'
            , 'event', "holder_value", "holder_diff", "holder_cum_pnl", 'lp_amount_0', 'lp_amount_1',
                        "lp_total_value", "lp_diff", "lp_cum_pnl", 'fee_0', 'fee_1', "fee_total_value", "fee_diff",
                        "cum_fee", "equity"]

        self.row = pd.Series(np.nan, index=self.columns)
        self.last_row = None
        self.df = pd.DataFrame(columns=self.columns)

        self.initial_set()

        if self.config_settings.trading_mode == enumerator.TradingMode.LIVE and not is_copy:
            self.signal_manager = SignalManager(copy.deepcopy(self.config_settings))

            # vault_balances = self.signal_manager.get_vault_balances()
            # self.signal_manager.manual_add_signal(1776, 1442.36, 1970.46, False)
            # self.signal_manager.tea_vault_api.unit_test()

    def initial_set(self):
        self.S = feeapi.simulator_api(
            network=self.network,
            base_url=self.config_settings.fee_api_domain,
            pool_address=self.pool_address
        )

        self.fee = self.config_settings.fee
        self.tick_spacing = self.config_settings.tick_spacing
        self.token_0 = self.config_settings.token_0.name
        self.token_1 = self.config_settings.token_1.name
        self.decimal_0 = self.config_settings.token_0.decimals
        self.decimal_1 = self.config_settings.token_1.decimals

        if self.base_token == self.token_0:
            self.base_symbol = "0"
        elif self.base_token == self.token_1:
            self.base_symbol = "1"

        if self.base_symbol == "0":
            self.row["lp_amount_0"] = self.initial_base_token_amount
            self.row["lp_amount_1"] = 0
        elif self.base_symbol == "1":
            self.row["lp_amount_0"] = 0
            self.row["lp_amount_1"] = self.initial_base_token_amount

    def register_signal_sender(self):
        self.send_signal_handler = self.signal_manager.send_signal

    def feed_signal(self, trade_signal):

        if self.signals_hist.empty or trade_signal.block_number > self.signals_hist.iloc[-1].block:

            if self.config_settings.simulation_detail == enumerator.SimulationDetail.TRADE:
                if not trade_signal.event:
                    return

            if self.send_signal_handler:
                self.send_signal_handler(trade_signal)

            self.signals_hist = pd.concat([self.signals_hist, pd.DataFrame.from_dict({
                'timestamp': trade_signal.time_stamp,
                'block': trade_signal.block_number,
                'tick': trade_signal.tick,
                'lower_tick': trade_signal.lower_tick,
                'upper_tick': trade_signal.upper_tick,
                'event': trade_signal.get_event_value()
            }, orient='index').T], ignore_index=True, axis=0)

            self.row["timestamp"] = trade_signal.time_stamp
            self.row["block"] = trade_signal.block_number
            self.row["tick"] = trade_signal.tick
            self.row["lower_tick"] = trade_signal.lower_tick
            self.row["upper_tick"] = trade_signal.upper_tick
            self.row["event"] = trade_signal.get_event_value()

            self.run()

            AppLog.logger().debug(f'Simulation: {datetime.fromtimestamp(trade_signal.time_stamp, pytz.timezone("UTC"))}')

    def check_status(self, mode):
        if mode == "on":
            if self.row["event"] == "add":
                self.status = "on"
        elif mode == "off":
            if self.last_row["event"] == "remove swap":
                self.status = "off"

    def update_trade_num_and_bars(self):
        if self.row["event"] == "add":
            self.trade_num += 1
        self.bars += 1

    def transfer(self):
        def tick_to_price(tick):
            token_0_price = 1.0001 ** tick * 10 ** (self.decimal_0 - self.decimal_1)
            if self.base_symbol == "0":
                price = 1 / token_0_price
            elif self.base_symbol == "1":
                price = token_0_price
            return price

        def price_to_tick(price):
            if self.base_symbol == "0":
                token_1_price = price
                token_0_price = 1 / token_1_price
                tick = math.log(token_0_price / 10 ** (self.decimal_0 - self.decimal_1), 1.0001)
            elif self.base_symbol == "1":
                token_0_price = price
                tick = math.log(token_0_price / 10 ** (self.decimal_0 - self.decimal_1), 1.0001)
            return tick

        self.row["price"] = tick_to_price(self.row["tick"])

        if self.base_symbol == "0":
            self.row["lower_price"] = tick_to_price(self.row["upper_tick"])
            self.row["upper_price"] = tick_to_price(self.row["lower_tick"])
        elif self.base_symbol == "1":
            self.row["lower_price"] = tick_to_price(self.row["lower_tick"])
            self.row["upper_price"] = tick_to_price(self.row["upper_tick"])

    def record_LP(self):
        row = self.row

        def cal_lp_total_value():
            if self.base_symbol == "0":
                self.row["lp_total_value"] = row["lp_amount_0"] + row["lp_amount_1"] * row["price"]
            elif self.base_symbol == "1":
                self.row["lp_total_value"] = row["lp_amount_1"] + row["lp_amount_0"] * row["price"]

        if self.bars == 1:
            cal_lp_total_value()

        elif self.bars > 1:
            if self.status == "on" and self.row["event"] != "add":
                info = self.trade_info[self.trade_num]
                target_token_remain_amount, base_token_remain_amount, holder_value, lp_value, IL, IL_percentage = ilCalculator.IL_CAL(
                    P_entry=info["entry_price"], P_exit=row["price"], P_lower=info["lower_price"],
                    P_upper=info["upper_price"], initial_base_token_amount=info["initial_LP"])

                if self.base_symbol == "0":
                    self.row["lp_amount_0"] = base_token_remain_amount
                    self.row["lp_amount_1"] = target_token_remain_amount

                elif self.base_symbol == "1":
                    self.row["lp_amount_0"] = target_token_remain_amount
                    self.row["lp_amount_1"] = base_token_remain_amount

            else:
                self.row["lp_amount_0"] = self.last_row["lp_amount_0"]
                self.row["lp_amount_1"] = self.last_row["lp_amount_1"]

            cal_lp_total_value()

    def record_holder_value(self):
        if self.status == "off":
            self.row["holder_value"] = np.nan
        elif self.status == "on":
            if self.bars == 1:
                self.row["holder_value"] = self.row["lp_total_value"]
            elif self.bars > 1:
                if self.row["event"] == "add":
                    self.row["holder_value"] = self.row["lp_total_value"]
                elif self.row["event"] != "add":
                    if self.base_symbol == "0":
                        self.row["holder_value"] = self.trade_info[self.trade_num]["initial_amount_0"] + \
                                                   self.trade_info[self.trade_num]["initial_amount_1"] * self.row[
                                                       "price"]
                    elif self.base_symbol == "1":
                        self.row["holder_value"] = self.trade_info[self.trade_num]["initial_amount_1"] + \
                                                   self.trade_info[self.trade_num]["initial_amount_0"] * self.row[
                                                       "price"]

    def record_fee(self):
        row = self.row

        if self.status == "off" or row["event"] == "add":
            self.row["fee_0"] = 0
            self.row["fee_1"] = 0

        elif self.status == "on" and row["event"] != "add":
            info = self.trade_info[self.trade_num]
            startblock = int(info["start_block"])
            endblock = int(row["block"])
            liquidity = int(info["liquidity"])
            lowertick = int(info["lower_tick"])
            uppertick = int(info["upper_tick"])
            fee = self.S.estimate_earned_fee(startblock=startblock, endblock=endblock, liquidity=liquidity,
                                             lowertick=lowertick, uppertick=uppertick)["data"]
            self.row["fee_0"] = fee["earned0"] * 10 ** -self.decimal_0
            self.row["fee_1"] = fee["earned1"] * 10 ** -self.decimal_1

    def calcualte(self):
        row = self.row

        def cal_fee_total_value():
            if self.base_symbol == "0":
                self.row["fee_total_value"] = row["fee_0"] + row["fee_1"] * row["price"]
            elif self.base_symbol == "1":
                self.row["fee_total_value"] = row["fee_1"] + row["fee_0"] * row["price"]

        def cal_equity():
            self.row["equity"] = self.row["lp_total_value"] + self.row["fee_total_value"]

        def cal_lp_diff():
            if self.bars == 1:
                self.row["lp_diff"] = 0
            elif self.bars > 1:
                if self.last_row["event"] == "remove swap":
                    self.row["lp_diff"] = 0
                else:
                    self.row["lp_diff"] = self.row["lp_total_value"] - self.last_row["lp_total_value"]

        def cal_fee_diff():
            if self.bars == 1:
                self.row["fee_diff"] = 0
            elif self.bars > 1:
                if self.last_row["event"] == "remove swap":
                    self.row["fee_diff"] = 0
                else:
                    self.row["fee_diff"] = self.row["fee_total_value"] - self.last_row["fee_total_value"]

        def cal_holder_diff():
            if self.bars == 1:
                self.row["holder_diff"] = 0
            elif self.bars > 1:
                if self.status == "off":
                    self.row["holder_diff"] = 0
                elif self.status == "on":
                    if self.row["event"] == "add":
                        self.row["holder_diff"] = 0
                    elif self.row["event"] != "add":
                        self.row["holder_diff"] = self.row["holder_value"] - self.last_row["holder_value"]

        def cal_lp_cum_pnl():
            if self.bars == 1:
                self.row["lp_cum_pnl"] = 0
            elif self.bars > 1:
                self.row["lp_cum_pnl"] = self.last_row["lp_cum_pnl"] + self.row["lp_diff"]

        def cal_holder_cum_pnl():
            if self.bars == 1:
                self.row["holder_cum_pnl"] = 0
            elif self.bars > 1:
                self.row["holder_cum_pnl"] = self.last_row["holder_cum_pnl"] + self.row["holder_diff"]

        def cal_cum_fee():
            if self.bars == 1:
                self.row["cum_fee"] = 0
            elif self.bars > 1:
                self.row["cum_fee"] = self.last_row["cum_fee"] + self.row["fee_diff"]

        cal_fee_total_value()
        cal_equity()
        cal_lp_diff()
        cal_fee_diff()
        cal_holder_diff()
        cal_lp_cum_pnl()
        cal_holder_cum_pnl()
        cal_cum_fee()

    def swap(self):
        if self.last_row["event"] == "add":
            self.row = self.last_row.copy()
            self.row["event"] = "add swap"

            base_token_amount, target_token_amount, target_token_in_base_token_amount = ilCalculator.Amount_CAL(
                P_entry=self.row["price"], P_lower=self.row["lower_price"], P_upper=self.row["upper_price"],
                initial_base_token_amount=self.row["lp_total_value"])

            if self.base_symbol == "0":
                self.row["lp_amount_0"] = base_token_amount
                self.row["lp_amount_1"] = target_token_amount

            elif self.base_symbol == "1":
                self.row["lp_amount_0"] = target_token_amount
                self.row["lp_amount_1"] = base_token_amount

        elif self.last_row["event"] == "remove":
            self.row = self.last_row.copy()
            self.row["event"] = "remove swap"

            if self.base_symbol == "0":
                self.row["lp_amount_0"] = self.row["equity"]
                self.row["lp_amount_1"] = 0
            elif self.base_symbol == "1":
                self.row["lp_amount_0"] = 0
                self.row["lp_amount_1"] = self.row["equity"]

            self.row["lp_total_value"] = self.row["equity"]

    def record_trade_info(self):
        if self.row["event"] == "add swap":
            row = self.row
            amount_0 = int(row["lp_amount_0"] * 10 ** self.decimal_0)
            amount_1 = int(row["lp_amount_1"] * 10 ** self.decimal_1)
            block = int(row["block"])
            lower_tick = int(row["lower_tick"])
            upper_tick = int(row["upper_tick"])
            tick = int(row["tick"])

            if tick <= lower_tick:
                liquidity = self.S.get_position_info_by_amount_0(block=block, amount_0=amount_0, lowertick=lower_tick,
                                                                 uppertick=upper_tick)["data"]["liquidity"]
            elif tick >= upper_tick:
                liquidity = self.S.get_position_info_by_amount_1(block=block, amount_1=amount_1, lowertick=lower_tick,
                                                                 uppertick=upper_tick)["data"]["liquidity"]
            else:
                liquidity = self.S.get_position_info_by_amount_0(block=block, amount_0=amount_0, lowertick=lower_tick,
                                                                 uppertick=upper_tick)["data"]["liquidity"]

            self.trade_info[self.trade_num] = {
                "start_datetime": datetime.fromtimestamp(row["timestamp"]),
                "end_datetime": np.nan,
                "start_timestamp": row["timestamp"],
                "end_timestamp": np.nan,
                "start_block": row["block"],
                "end_block": np.nan,
                "entry_price": row["price"],
                "exit_price": np.nan,
                "lower_price": row["lower_price"],
                "upper_price": row["upper_price"],
                "lower_tick": row["lower_tick"],
                "upper_tick": row["upper_tick"],
                "liquidity": liquidity,
                "fees": np.nan,
                "initial_holder": row["lp_total_value"],
                "last_holder": np.nan,
                "initial_amount_0": row["lp_amount_0"],
                "initial_amount_1": row["lp_amount_1"],
                "initial_LP": row["lp_total_value"],
                "last_amount_0": np.nan,
                "last_amount_1": np.nan,
                "last_LP": np.nan,
                "LP_PNL": np.nan,
                "IL": np.nan,
                "AMM_PNL": np.nan,
                "Fee-IL": np.nan
            }
        elif self.row["event"] == "remove swap":
            row = self.row
            last_row = self.last_row
            self.trade_info[self.trade_num].update(
                {
                    "end_datetime": datetime.fromtimestamp(row["timestamp"]),
                    "end_timestamp": row["timestamp"],
                    "end_block": row["block"],
                    "exit_price": row["price"],
                    "fees": row["fee_total_value"],
                    "last_holder": last_row["holder_value"],
                    "last_amount_0": last_row["lp_amount_0"],
                    "last_amount_1": last_row["lp_amount_1"],
                    "last_LP": last_row["lp_total_value"],
                }
            )
            self.trade_info[self.trade_num]["LP_PNL"] = self.trade_info[self.trade_num]["last_LP"] - \
                                                        self.trade_info[self.trade_num]["initial_LP"]
            self.trade_info[self.trade_num]["AMM_PNL"] = self.trade_info[self.trade_num]["LP_PNL"] + \
                                                         self.trade_info[self.trade_num]["fees"]
            self.trade_info[self.trade_num]["Holder_PNL"] = self.trade_info[self.trade_num]["last_holder"] - \
                                                            self.trade_info[self.trade_num]["initial_holder"]
            self.trade_info[self.trade_num]["IL"] = self.trade_info[self.trade_num]["Holder_PNL"] - \
                                                    self.trade_info[self.trade_num]["LP_PNL"]
            self.trade_info[self.trade_num]["Fee-IL"] = self.trade_info[self.trade_num]["fees"] - \
                                                        self.trade_info[self.trade_num]["IL"]

            for i in ["fees", "LP_PNL", "AMM_PNL", "Holder_PNL", "IL", "Fee-IL"]:
                self.trade_info[self.trade_num][f"{i}(%)"] = 100 * self.trade_info[self.trade_num][i] / self.initial_base_token_amount

    def add_series_and_reset(self, mode):
        def asar():
            new_df = pd.DataFrame([self.row.tolist()], columns=self.columns)
            self.df = pd.concat([self.df, new_df])
            self.last_row = self.row
            AppLog.logger().debug("-" * 100)
            AppLog.logger().debug(self.bars)
            AppLog.logger().debug("-" * 100)
            AppLog.logger().debug(self.last_row)
            self.row = pd.Series(np.nan, index=self.columns)

        if mode == "swap":
            if (self.row["event"] == "add swap") or (self.row["event"] == "remove swap"):
                asar()
        elif mode == "normal":
            asar()

    def df_ledger(self):
        self.df["datetime"] = self.df["timestamp"].apply(lambda x: datetime.fromtimestamp(x))

        self.df["holder_cum_pnl(%)"] = 100 * self.df["holder_cum_pnl"] / self.initial_base_token_amount
        self.df["lp_cum_pnl(%)"] = 100 * self.df["lp_cum_pnl"] / self.initial_base_token_amount
        self.df["cum_fee(%)"] = 100 * self.df["cum_fee"] / self.initial_base_token_amount
        self.df["amm_pnl(%)"] = 100 * ((self.df["equity"] / self.initial_base_token_amount) - 1)

        columns = ['datetime', 'timestamp', "block", 'tick', 'lower_tick', 'upper_tick', 'price', 'lower_price',
                   'upper_price', 'event', "holder_value", "holder_diff", "holder_cum_pnl", "holder_cum_pnl(%)",
                   'lp_amount_0', 'lp_amount_1', "lp_total_value", "lp_diff", "lp_cum_pnl", "lp_cum_pnl(%)",
                   'fee_0', 'fee_1', "fee_total_value", "fee_diff", "cum_fee", "cum_fee(%)", "equity", "amm_pnl(%)"]

        self.df = self.df[columns]
        return self.df

    def trade_list(self):
        columns = ["Trade_Num", "Timestamp", "Block", "Price", "Lower", "Upper", "Holder_PNL", "LP_PNL", "IL", "Fees",
                   "Fee-IL", "AMM_PNL"]
        df = pd.DataFrame(columns=columns)
        for i in self.trade_info:
            key = i
            value = self.trade_info[i]

            new_df = pd.DataFrame([[key, value["start_timestamp"], value["start_block"], value["entry_price"],
                                    value["lower_price"], value["upper_price"], np.nan, np.nan, np.nan, np.nan,
                                    np.nan, np.nan]], columns=columns)
            df = pd.concat([df, new_df])

            new_df = pd.DataFrame([[np.nan, value["end_timestamp"], value["end_block"], value["exit_price"],
                                    value["lower_price"], value["upper_price"], value["Holder_PNL"], value["LP_PNL"],
                                    value["IL"], value["fees"], value["Fee-IL"], value["AMM_PNL"]]], columns=columns)
            df = pd.concat([df, new_df])

        df["Datetime"] = df["Timestamp"].apply(lambda x: datetime.fromtimestamp(x))

        for i in ["Holder_PNL", "LP_PNL", "IL", "Fees", "Fee-IL", "AMM_PNL"]:
            df[f"{i}(%)"] = 100 * df[i] / self.initial_base_token_amount

        df = df[["Trade_Num", "Datetime", "Timestamp", "Block", "Price", "Lower", "Upper", "Holder_PNL", "LP_PNL", "IL",
                 "Fees", "Fee-IL", "AMM_PNL", "Holder_PNL(%)", "LP_PNL(%)", "IL(%)", "Fees(%)", "Fee-IL(%)",
                 "AMM_PNL(%)"]]

        return df

    def stats(self):
        pass

    def run(self):
        self.check_status("on")
        self.update_trade_num_and_bars()
        self.transfer()
        self.record_LP()
        self.record_holder_value()
        self.record_fee()
        self.calcualte()
        self.add_series_and_reset("normal")
        self.swap()
        self.record_trade_info()
        self.add_series_and_reset("swap")
        self.check_status("off")

    def add_remove_if_do_have_position(self, last_k_bar):
        if not np.isnan(self.signals_hist.iloc[-1].upper_tick):
            self.feed_signal(ts.TradeSignal(
                time_stamp=last_k_bar.timestamp_unix + 1,
                block_number=last_k_bar.block_number + 1,
                tick=last_k_bar.tick,
                lower_tick=self.signals_hist.iloc[-1].lower_tick,
                upper_tick=self.signals_hist.iloc[-1].upper_tick,
                event=ts.Liquidity.REMOVE,
            ))
            return True
        
        return False

    def __deepcopy__(self, memodict={}):
        cpyobj = type(self)(self.config_settings, self.strategy_name, True)

        for attr, value in vars(self).items():
            if attr != 'signal_manager' and attr != 'send_signal_handler':
                cpyobj.__dict__[attr] = copy.deepcopy(value, memodict)
            else:
                cpyobj.__dict__[attr] = None

        return cpyobj


'''
# ------------------------------------------------------------------------------------------------------------------------
strategy_name = "Banqiao"
pool_address = "0xCBCdF9626bC03E24f779434178A73a0B4bad62eD"
target_token = "WBTC"
base_token = "WETH"
initial_base_token_amount = 50
# ------------------------------------------------------------------------------------------------------------------------
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

Test = Ledger(pool_address=pool_address, initial_base_token_amount=initial_base_token_amount, strategy_name=strategy_name, target_token=target_token,base_token=base_token)

df = pd.read_csv("back_test_sample.csv", index_col=0)

for index, row in df.iterrows():
    Test.feed_siganl(timestamp= row["timestamp"], block=row["block"], tick= row["tick"], lower_tick= row["lower_tick"], upper_tick= row["upper_tick"], event= row["event"])
    Test.run()

trade_list = Test.trade_list()
print(trade_list)
# trade_list.to_csv("trade_list.csv",index=0)
#
print(Test.df)
# Test.df.to_csv("result.csv")
'''
