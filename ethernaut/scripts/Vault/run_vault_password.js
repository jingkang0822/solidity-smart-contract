const { assert } = require("chai");
const { ethers, provider } = require('hardhat');

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("Vault");

    storage = await ethers.provider.getStorageAt("0x4B37f8bc5996e1DF43E8Ed09DEE347934f7B4bB7", 1)
    console.log(storage);

    console.log(ethers.utils.parseBytes32String(storage));
}   


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
