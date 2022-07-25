
const hre = require("hardhat");

async function main() {
  // We get the contract to deploy
  const contractFactory = await hre.ethers.getContractFactory("UpgradeableToken");
  const contract = await contractFactory.deploy();

  await contract.deployed();
  console.log("UpgradeableToken deployed to:", contract.address);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
