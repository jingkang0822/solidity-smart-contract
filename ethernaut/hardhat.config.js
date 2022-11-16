require('@nomiclabs/hardhat-waffle');
require("@nomiclabs/hardhat-etherscan");
require("hardhat-gas-reporter");
require('dotenv').config({
  path: `../../../BlockChain/environment/.env.develop`
});


module.exports = {
  solidity: {
    version: '0.8.6',
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    matic: {
      url: `${process.env.MATIC_RPC}`,
      accounts: [ 
        `0x6fdd56d3187dbe430f9b10a58f3843bbf201072e6821823cf68bd945dec208bc`,
        `0x988f4142d72a8e28219885a10cb83f8f105c8a823e5ac7812a9c6d0598309cdf`
      ],
    },
    mumbai: {
      url: `${process.env.MUMBAI_RPC}`,
      accounts: [ 
        `0x6fdd56d3187dbe430f9b10a58f3843bbf201072e6821823cf68bd945dec208bc`,
        `0x988f4142d72a8e28219885a10cb83f8f105c8a823e5ac7812a9c6d0598309cdf`
      ],
    }
  },
  gasReporter: {
    enabled: true,
    currency: "USD",
    // gasPrice: 21
  },
  etherscan: {
    apiKey: process.env.POLYGONSCAN_API_KEY,
  }
};
