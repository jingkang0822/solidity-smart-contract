const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Contract deployed", function () {

  it("Deployed normally", async function () {
    const Greeter = await ethers.getContractFactory("UpgradeableToken");
    const greeter = await Greeter.deploy();
    
    await greeter.deployed();
    console.log("UpgradeableToken deployed to:", greeter.address);
  });
});
