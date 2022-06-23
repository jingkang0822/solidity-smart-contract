// We import Chai to use its asserting functions here.
const { expect } = require("chai");

describe("ERC20 function check", function () {
  let totalSupply = '10000000000000000000000'; // 10000 * 1e18
  let Token;
  let tokenContract;
  let owner;
  let addr1;
  let addr2;
  let addrs;

  beforeEach(async function () {
    // Get the ContractFactory and Signers here.
    Token = await ethers.getContractFactory("StakingToken");
    [owner, addr1, addr2, ...addrs] = await ethers.getSigners();

    tokenContract = await Token.deploy(totalSupply);
  });

  // You can nest describe calls to create subsections.
  describe("Deployment", function () {

    it("Should assign the total supply of tokens to the owner", async function () {
      const ownerBalance = await tokenContract.balanceOf(owner.address);
      expect(await tokenContract.totalSupply()).to.equal(ownerBalance);
    });
  });

  describe("Transactions", function () {

    it("Should transfer tokens between accounts", async function () {
        const ownerBalance = await tokenContract.balanceOf(owner.address);

      // Transfer 50 tokens from owner to addr1
      await tokenContract.transfer(addr1.address, 50);
      const addr1Balance = await tokenContract.balanceOf(addr1.address);
      expect(addr1Balance).to.equal(50);

      // Transfer 50 tokens from addr1 to addr2
      // We use .connect(signer) to send a transaction from another account
      await tokenContract.connect(addr1).transfer(addr2.address, 50);
      const addr2Balance = await tokenContract.balanceOf(addr2.address);
      expect(addr2Balance).to.equal(50);
    });

    it("Should fail if sender doesn’t have enough tokens", async function () {
      const initialOwnerBalance = await tokenContract.balanceOf(owner.address);

      // Try to send 1 token from addr1 (0 tokens) to owner (1000000 tokens).
      // `require` will evaluate false and revert the transaction.
      await expect(
        tokenContract.connect(addr1).transfer(owner.address, 1)
      ).to.be.revertedWith("ERC20: transfer amount exceeds balance");

      // Owner balance shouldn't have changed.
      expect(await tokenContract.balanceOf(owner.address)).to.equal(
        initialOwnerBalance
      );
    });

  });
});