import requests
import time
from logger import AppLog


class simulator_api():
    def __init__(self, network, base_url, pool_address):
        self.base_url = base_url
        self.network = network
        self.pool_address = pool_address

    def request(self, url, params=None):
        r = requests.get(url=url, params=params)
        AppLog.logger().debug(r.url)
        data = r.json()
        AppLog.logger().debug(data)

        n = 5
        while "error" in data.keys():
            AppLog.logger().info(f"retry {6-n}")
            r = requests.get(url=url, params=params)
            AppLog.logger().debug(data)
            data = r.json()
            n = n - 1
            time.sleep(1)
            if n < 0:
                break

        return data

    def check_alive(self):
        get_url = "/"
        url = self.base_url + get_url
        return self.request(url)

    def get_list_of_net_works(self):
        get_url = "/networks/list"
        url = self.base_url + get_url
        return self.request(url)

    def get_list_of_pools(self):
        get_url = "/pools/list"
        url = self.base_url + get_url
        params = {
            "network" : self.network
        }
        return self.request(url, params)

    def get_pool_info(self, config_settings):
        get_url = "/pools/info"
        url = self.base_url + get_url
        params = {
            "network": config_settings.chain.value,
            "pool": self.pool_address
        }

        return self.request(url, params)

    def get_priceby_block(self,block=None):
        get_url = "/pools/price"
        url = self.base_url + get_url
        params = {
            "network" : self.network,
            "pool" : self.pool_address,
            "block" : block
        }
        return self.request(url,params)

    def get_batch_price_by_block(self,start,end,step):
        get_url = "/pools/price/batch/by_block"
        url = self.base_url + get_url
        params = {
            "network" : self.network,
            "pool" : self.pool_address,
            "start" : start,
            "end" : end,
            "step" : step
        }
        return self.request(url,params)

    def get_batch_price_by_time(self,start,end,step):
        get_url = "/pools/price/batch/by_time"
        url = self.base_url + get_url
        params = {
            "network" : self.network,
            "pool" : self.pool_address,
            "start" : start,
            "end" : end,
            "step" : step
        }
        return self.request(url,params)

    def get_position_info_by_amount_0(self,block,amount_0,lowertick,uppertick):
        get_url = "/pools/estimate/position_info/by_amount0"
        url = self.base_url + get_url
        params = {
            "network" : self.network,
            "pool" : self.pool_address,
            "block": block,
            "amount0" : amount_0,
            "lowerTick" : lowertick,
            "upperTick" : uppertick
        }
        return self.request(url,params)

    def get_position_info_by_amount_1(self,block,amount_1,lowertick,uppertick):
        get_url = "/pools/estimate/position_info/by_amount1"
        url = self.base_url + get_url
        params = {
            "network" : self.network,
            "pool" : self.pool_address,
            "block": block,
            "amount1" : amount_1,
            "lowerTick" : lowertick,
            "upperTick" : uppertick
        }
        return self.request(url,params)

    def get_position_info_by_liquidity(self,block,liquidity,lowertick,uppertick):
        get_url = "/pools/estimate/position_info/by_liquidity"
        url = self.base_url + get_url
        params = {
            "network" : self.network,
            "pool" : self.pool_address,
            "block": block,
            "liquidity" : liquidity,
            "lowerTick" : lowertick,
            "upperTick" : uppertick
        }
        return self.request(url,params)

    def estimate_earned_fee(self,startblock,endblock,liquidity,lowertick,uppertick):
        get_url = "/pools/estimate/fee"
        url = self.base_url + get_url
        params = {
            "network" : self.network,
            "pool" : self.pool_address,
            "startBlock" : startblock,
            "endBlock" : endblock,
            "liquidity" : liquidity,
            "lowerTick" : lowertick,
            "upperTick" : uppertick
        }
        return self.request(url,params)

    def initialized_ticks_and_liquidity(self,block):
        get_url = "/pools/liquidity"
        url = self.base_url + get_url
        params = {
            "network" : self.network,
            "pool" : self.pool_address,
            "block" : block
        }
        return self.request(url,params)

    def get_ethereum_block_id_by_timestamp(self,timestamp):
        get_url = "/eth/block/by_timestamp"
        url = self.base_url + get_url
        params = {
            "timestamp" : timestamp
        }
        return self.request(url,params)

    def get_ethereum_timestamp_by_block_id(self,block):
        get_url = "/eth/block/by_block"
        url = self.base_url + get_url
        params = {
            "block" : block
        }
        return self.request(url,params)

    def get_ethereum_latest_block(self,):
        get_url = "/eth/block/latest"
        url = self.base_url + get_url
        return self.request(url)

if __name__ == '__main__':
    network = "eth_mainnet"
    pool_address = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"  # ETH/USDC

    S = simulator_api(network=network, base_url='http://office.teahouse.finance:8181', pool_address=pool_address)

    # result = S.check_alive()
    # result = S.get_list_of_net_works()
    # result = S.get_list_of_pools()
    # result = S.get_pool_info()

    # result = S.get_priceby_block(block=14067965) # default=None
    # result = S.get_batch_price_by_block(start=14067965,end=14077965,step=1000)
    # result = S.get_batch_price_by_time(start=1643022221,end=1643156155,step=13393)
    result = S.get_position_info_by_amount_0(block=14067965, amount_0=463998416246, lowertick=193740, uppertick=200820)
    # result = S.get_position_info_by_amount_1(block=14067965, amount_1=716436838751467864064, lowertick=193740, uppertick=200820)
    # result = S.get_position_info_by_liquidity(block=14067965, liquidity=137919288535059408, lowertick=193740, uppertick=200820)
    result = S.estimate_earned_fee(startblock=14067964, endblock=14068499, liquidity=137919288535059408, lowertick=193740, uppertick=200820)
    # result = S.initialized_ticks_and_liquidity(block=14146832)

    # result = S.get_ethereum_block_id_by_timestamp(timestamp=1643022221)
    # result = S.get_ethereum_timestamp_by_block_id(block=13136637)
    # result = S.get_ethereum_latest_block()


