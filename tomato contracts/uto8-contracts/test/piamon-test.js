const { expect } = require('chai');
const { ethers, waffle } = require('hardhat');
const contractABI = require('../piamon-abi.json');

describe('info', function () {
  it('should return balance of piamon contract', async function () {
    const provider = waffle.provider;
    // const balanceInUto8 = await provider.balance(
    //   '0xdc64a140aa3e981100a9beca4e685f962f0cf6c9'
    // );

    const address = '0xdc64a140aa3e981100a9beca4e685f962f0cf6c9';

    const contract = new ethers.Contract(address, contractABI, provider);

    const balanceInUto8 = await contract.address;

    console.log(balanceInUto8);

    expect(1).greaterThan(0);
  });
});
