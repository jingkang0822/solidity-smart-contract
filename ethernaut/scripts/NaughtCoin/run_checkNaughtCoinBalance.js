const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("ERC20");
    hack = await hack_contract.attach("0xca00516AEdDF08aBc2051d8d261927Ea402FcDF7");

    tx = await hack.balanceOf(deployer.address);
    console.log("================== tx ===================");
    console.log(tx);
}


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
