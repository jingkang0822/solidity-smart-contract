const hre = require("hardhat");

async function main() {

  const GLDToken = await hre.ethers.getContractFactory("My1155");
  console.log('Deploying My1155...');
  const token = await GLDToken.deploy();

  await token.deployed();
  console.log("My1155 deployed to:", token.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });