/**
 * @type import('hardhat/config').HardhatUserConfig
 */

require("@nomiclabs/hardhat-ethers");
require("@nomiclabs/hardhat-waffle");
require("dotenv").config();

const privateKey = process.env.PRIVATE_KEY;
const rinkebyEndPoint = process.env.URL;
const velasTestNetEndPoint = process.env.VELAS_TEST_NET_URL;
console.log(velasTestNetEndPoint);

module.exports = {
  solidity: "0.8.8",
  networks: {
    rinkeby: {
      url: rinkebyEndPoint,
      accounts: [`0x${privateKey}`]
    },
    velas_test_net: {
      url: velasTestNetEndPoint,
      accounts: [`0x${privateKey}`]
    }
  }
};
