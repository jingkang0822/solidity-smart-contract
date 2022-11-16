const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hackflip_contract = await ethers.getContractFactory("HackAlienCodex");
    hackflip = await hackflip_contract.deploy();
    await hackflip.deployed();

    console.log("HackAlienCodex address:", hackflip.address);
}


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
