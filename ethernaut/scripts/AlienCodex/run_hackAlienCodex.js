const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hackflip_contract = await ethers.getContractFactory("HackAlienCodex");
    hackflip = await hackflip_contract.attach("0xf9de759cd9e096e8A3855D1D01f43A50B2ce9602");

    tx = await hackflip.claim();
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
