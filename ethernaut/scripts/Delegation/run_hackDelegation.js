const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("HackDelegation");
    hack = await hack_contract.attach("0x2257817792263Adb248D419DD1848DF91F5c519B");

    console.log("================== getsig ===================");
    console.log(await hack.getsig());
}


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
