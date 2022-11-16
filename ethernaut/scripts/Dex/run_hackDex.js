const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("HackDex");
    hack = await hack_contract.attach("0x0e7cf36168BBff1B25479096BEf447992C29b792");

    tx = await hack.run();
    console.log("================== tx ===================");
    console.log(tx);

    receipt = await tx.wait();
    console.log("================== receipt ===================");
    console.log(receipt);
}


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
