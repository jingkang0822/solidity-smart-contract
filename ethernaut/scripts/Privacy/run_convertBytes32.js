const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("HackPrivacy");
    hack = await hack_contract.attach("0x4e282961D2cF19999A114feDb0732114B26cD059");

    tx = await hack.convert("0x69b701437dba616b8aef2043984847efbe9e6d076d3671cefb8faaaf9e797ae7");
    console.log("================== tx ===================");
    console.log(tx);
}


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
