const { ethers } = require('hardhat');

async function main() {
    contractFactory = await ethers.getContractFactory("UTO8");
    contract = await contractFactory.attach("0x81525c6c2cdC108e2e1135237b66D5A518eEf83c");
    console.log(`Get token name: ${await contract.name()}`);

    balanceOfOwner = await contract.balanceOf("0x37100698B013ce6097453dEf91986EabA6570Ea2");
    console.log(`Owner uto8 balance: ${balanceOfOwner}`);

    balanceOfAddr1 = await contract.balanceOf("0x4E38d13515f79da1F9850A5263Ca3998ccDf44FA");
    console.log(`Addr1 uto8 balance: ${balanceOfAddr1}`);
}



main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
});