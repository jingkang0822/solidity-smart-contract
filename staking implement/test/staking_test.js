// We import Chai to use its asserting functions here.
const { expect } = require("chai");
const { BigNumber } = require('ethers');

describe("Staking function check", function () {
  let tokenTotal = 10000;
  let totalSupply = BigNumber.from('10').pow(18).mul(tokenTotal); // 10000 * 1e18
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

  describe("Staking", function () {

    it('createStake creates a stake.', async () => {

        // Transfer 3 tokens from owner to addr1
        await tokenContract.transfer(addr1.address, 3);

        await tokenContract.connect(addr1).createStake(1);

        expect(await tokenContract.balanceOf(addr1.address)).to.equal(2);
        expect(await tokenContract.stakeOf(addr1.address)).to.equal(1);

        // Total amount of token should minus 1, after staking 1 token.
        // ethers.utils.parseEther("10")
        expect(await tokenContract.totalSupply()).to.equal(totalSupply.sub(1));

        // Check total stake
        expect(await tokenContract.totalStakes()).to.equal(1);
    });

    it('rewards are distributed.', async () => {
        // Transfer 100 tokens from owner to addr1
        await tokenContract.transfer(addr1.address, 100);
        await tokenContract.connect(addr1).createStake(100);
        await tokenContract.distributeRewards();

        expect(await tokenContract.connect(addr1).rewardOf(addr1.address)).to.equal(1);
        expect(await tokenContract.totalRewards()).to.equal(1);
    });

    it('rewards can be withdrawn.', async () => {

        await tokenContract.transfer(addr1.address, 100);
        expect(await tokenContract.balanceOf(addr1.address)).to.equal(100);

        await tokenContract.connect(addr1).createStake(100);
        expect(await tokenContract.balanceOf(addr1.address)).to.equal(0);

        await tokenContract.distributeRewards();
        await tokenContract.connect(addr1).withdrawReward();
        expect(await tokenContract.balanceOf(addr1.address)).to.equal(1);

        await tokenContract.connect(addr1).removeStake(50);
        expect(await tokenContract.balanceOf(addr1.address)).to.equal(51);
        expect(await tokenContract.stakeOf(addr1.address)).to.equal(50);
    });
  });

});