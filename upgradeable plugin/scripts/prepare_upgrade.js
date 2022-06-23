// scripts/prepare_upgrade.js

// When calling upgrades.upgradeProxy(), two jobs are done:
// an implementation contract is deployed
// ProxyAdmin upgrade() is called to link Proxy and implementation contract.

async function main() {
    const proxyAddress = '0x668565Bc69BDAAf87303f1a0A82084bBfE65759c';
   
    const BoxV2 = await ethers.getContractFactory("BoxV2");
    console.log("Preparing upgrade...");
    const boxV2Address = await upgrades.prepareUpgrade(proxyAddress, BoxV2);
    console.log("BoxV2 at:", boxV2Address);
  }
   
  main()
    .then(() => process.exit(0))
    .catch(error => {
      console.error(error);
      process.exit(1);
    });