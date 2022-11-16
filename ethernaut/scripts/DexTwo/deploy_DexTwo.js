const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("HackDex2");
    hack = await hack_contract.deploy();
    await hack.deployed();

    console.log("hack address:", hack.address);
}


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
