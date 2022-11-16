const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("Dex");
    hack = await hack_contract.attach("0x7231827A0c3fEaFe9C2BC5fc5D3f91932648Ec24");

    tx = await hack.approve("0x7231827A0c3fEaFe9C2BC5fc5D3f91932648Ec24", 500);
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
