const { assert } = require("chai");
const { ethers, provider } = require('hardhat');

async function main() {
    
    const [deployer] = await ethers.getSigners();
    
    console.log("Deploying contracts with the account:", deployer.address);
    console.log("Account balance:", (await deployer.getBalance()).toString());

    storage = await ethers.provider.getStorageAt("0xfefEc0dFC896b10B447F8ad629CD246F75f1f56b", 5)
    console.log(storage);

    // console.log(ethers.utils.parseBytes32String(storage));
}   


main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
});
