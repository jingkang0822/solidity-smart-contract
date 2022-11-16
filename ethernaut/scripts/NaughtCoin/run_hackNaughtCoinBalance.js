const { assert } = require("chai");

async function main() {
    
    const [deployer, addr2] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    target_addr = "0xca00516AEdDF08aBc2051d8d261927Ea402FcDF7"
    target_amount = (BigInt(1000000000000000000000000)).toString()

    // Deploy
    hack_contract = await ethers.getContractFactory("ERC20");
    hack = await hack_contract.attach(target_addr);

    tx = await hack.approve(addr2.address, target_amount);
    console.log("================== tx ===================");
    console.log(tx);

    receipt = await tx.wait();
    console.log("================== receipt ===================");
    console.log(receipt);


    tx = await hack.connect(addr2).transferFrom(deployer.address, addr2.address, target_amount);;
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
