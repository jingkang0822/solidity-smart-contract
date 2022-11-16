const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("ForeverKing");
    hack = await hack_contract.attach("0xF90C861319807C9E387FD4dA3AfdF3896AFc9FDa");

    tx = await hack.give({value: ethers.utils.parseEther("0.01"), gasPrice: 100000});
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
