/**
 * @type import('hardhat/config').HardhatUserConfig
 */

require("@nomiclabs/hardhat-ethers");
require("@nomiclabs/hardhat-waffle");
require('@openzeppelin/hardhat-upgrades');
require("dotenv").config();

const privateKey = process.env.PRIVATE_KEY;
const rinkebyEndPoint = process.env.URL;

module.exports = {
  solidity: {
    version: "0.8.8"
  },
  networks: {
    rinkeby: {
      url: rinkebyEndPoint,
      accounts: [`0x${privateKey}`]
    }
  }
};
