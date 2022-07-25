// We require the Hardhat Runtime Environment explicitly here. This is optional
// but useful for running the script in a standalone fashion through `node <script>`.
//
// When running the script with `npx hardhat run <script>` you'll find the Hardhat
// Runtime Environment's members available in the global scope.
const hre = require("hardhat");

async function main() {
  // Hardhat always runs the compile task when running scripts with its command
  // line interface.
  //
  // If this script is run directly using `node` you may want to call compile
  // manually to make sure everything is compiled
  // await hre.run('compile');

  const vrf_coordinator = '0xb3dCcb4Cf7a26f6cf6B120Cf5A73875B7BBc655B'
  const link_token = '0x01be23585060835e02b77ef475b0cc51aa1e0709'
  const keyhash = '0x2ed0feb3e7fd2022120aa84fab1945545a9f2ffc9076fd6156fa96eaff4c1311'

  // We get the contract to deploy
  const contractFactory = await hre.ethers.getContractFactory("AdvancedCollectible");
  const contract = await contractFactory.deploy(vrf_coordinator, link_token, keyhash);

  await contract.deployed();

  console.log("AdvancedCollectible deployed to:", contract.address);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
