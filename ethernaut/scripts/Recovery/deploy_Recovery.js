const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("HackRecovery");
    hack = await hack_contract.deploy("0xFd788888f79Ae3Ada3358DD89a872D7c9955f50B");
    await hack.deployed();

    console.log("hack address:", hack.address);
}


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
