import configparser
from logger import AppLog


class EnvironmentVariable:
    tea_vault_api_url: str
    api_key: str
    tea_vault_address: str

    def __init__(self):

        with open('environment_path.txt', 'r') as file:

            config = configparser.ConfigParser()
            config.read(file.read().rstrip())

            self.tea_vault_api_url = config['default']['tea_vault_api_url']
            self.api_key = config['default']['api_key']
            self.tea_vault_address = config['default']['tea_vault_address']

            AppLog.logger().info('Load environment variable success.')
