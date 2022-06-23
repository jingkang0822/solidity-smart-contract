// scripts/4.prepareV4.ts

const proxyAddress = '0x668565Bc69BDAAf87303f1a0A82084bBfE65759c'

async function main() {
  console.log(proxyAddress," original Box(proxy) address")

  const BoxV4 = await ethers.getContractFactory("BoxV4")
  console.log("Preparing upgrade to BoxV4...");
  const boxV4Address = await upgrades.prepareUpgrade(proxyAddress, BoxV4);
  console.log(boxV4Address, " BoxV4 implementation contract address")
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})