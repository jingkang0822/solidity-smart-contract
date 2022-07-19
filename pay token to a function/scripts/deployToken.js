// scripts/GLDToken_deploy.js

const hre = require("hardhat");

async function main() {

  const contract = await hre.ethers.getContractFactory("PayEth");
  console.log('Deploying PayEth contract...');
  const contractDeployed = await contract.deploy();

  await contractDeployed.deployed();
  console.log("PayEth contract deployed to:", contractDeployed.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });