const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hackflip_contract = await ethers.getContractFactory("hackflip");
    hackflip = await hackflip_contract.attach("0x4EA08D512D2E016726Df36676bc87beF953C11C2");

    tx = await hackflip.hackFlip(true);
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
