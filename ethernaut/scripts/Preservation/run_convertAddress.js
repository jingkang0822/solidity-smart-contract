const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("HackPreservation");
    hack = await hack_contract.attach("0x6500Db00d6c29F859569367C4933eA42A2d6536D");

    tx = await hack.convertAddressToUnit("0x6500Db00d6c29F859569367C4933eA42A2d6536D");
    console.log("================== tx ===================");
    console.log(tx);
}


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
