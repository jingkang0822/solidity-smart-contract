const { ethers } = require('hardhat');

async function main() {

    console.log("------------ NFT contract onchain testing -------------------------")
    contractFactory = await ethers.getContractFactory("Piamon");
    contract = await contractFactory.attach("0x6b193027B742E1A1D7Bbf81F9eF321c2B8804EE1");
    nameOfContract = await contract.name();
    console.log(`Get NFT name: ${nameOfContract}`);

    symbolOfContract = await contract.symbol();
    console.log(`Get NFT symbol: ${symbolOfContract}`);

    //totalSupply = await contract.totalSupply();
    //console.log(`Get totalSupply: ${totalSupply}`);

    balanceOfOwner = await contract.balanceOf("0x37100698B013ce6097453dEf91986EabA6570Ea2");
    console.log(`Owner ${nameOfContract} balance: ${balanceOfOwner}`);

    balanceOfAddr1 = await contract.balanceOf("0x4E38d13515f79da1F9850A5263Ca3998ccDf44FA");
    console.log(`Addr1 ${nameOfContract} balance: ${balanceOfAddr1}`);

    console.log("------------ Token URI testing -------------------------")
    tokenId = 10045001;
    console.log(`TokenId: ${tokenId} tokenURI: ${await contract.tokenURI(tokenId)}`);
    
    //tokenId = 9;
    //console.log(`TokenId: ${tokenId} tokenURI: ${await contract.tokenURI(tokenId)}`);
    
    tokenId = 100001000007;
    console.log(`TokenId: ${tokenId} tokenURI: ${await contract.tokenURI(tokenId)}`);

    tokenId = 100001000022;
    console.log(`TokenId: ${tokenId} tokenURI: ${await contract.tokenURI(tokenId)}`);

    tokenId = 100001000008;
    console.log(`Egg TokenId: ${tokenId} tokenURI: ${await contract.tokenURI(tokenId)}`);
}



main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
});