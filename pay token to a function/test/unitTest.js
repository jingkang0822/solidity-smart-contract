// We import Chai to use its asserting functions here.
const { expect } = require("chai");

describe("PayEth contract", function () {
  let contract;
  let contractDeployed;
  let contractAddress;
  let ethAmount = 588;
  let owner;
  let addr1;
  let addr2;
  let addrs;

  beforeEach(async function () {
    // Get the ContractFactory and Signers here.
    contract = await ethers.getContractFactory("PayEth");
    [owner, addr1, addr2, ...addrs] = await ethers.getSigners();

    contractDeployed = await contract.deploy();
    contractAddress = contractDeployed.address;
  });

  // You can nest describe calls to create subsections.
  describe("Deployment", function () {

    it("Check initial ETH balance", async function () {
      expect(await contractDeployed.getBalance()).to.equal(0);
    });

    it(`Send ${ethAmount} ETH and check balance`, async function () {

      await contractDeployed.connect(addr1).deposit(ethAmount, {value: ethAmount});
      expect(await contractDeployed.getBalance()).to.equal(ethAmount);
    });

  });
});