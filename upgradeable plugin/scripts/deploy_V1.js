// scripts/deploy.js
async function main() {
    const Box = await ethers.getContractFactory("Box");
    console.log("Deploying Box...");
    const box = await upgrades.deployProxy(Box, [42], { initializer: 'store' });
    
    console.log("Box deployed to:", box.address);
    console.log(box.address," box(proxy) address")
    console.log(await upgrades.erc1967.getImplementationAddress(box.address)," getImplementationAddress")
    console.log(await upgrades.erc1967.getAdminAddress(box.address)," getAdminAddress")
  }
  
  main()
    .then(() => process.exit(0))
    .catch(error => {
      console.error(error);
      process.exit(1);
    });