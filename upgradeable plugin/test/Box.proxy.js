// test/Box.proxy.js
// Load dependencies
const { expect } = require('chai');
 
let Box;
let box;
 
// Start test block
describe('Box (proxy)', function () {
  beforeEach(async function () {
    Box = await ethers.getContractFactory("Box");
    box = await upgrades.deployProxy(Box, [42], {initializer: 'store'});

    console.log(box.address," box(proxy) address")
    console.log(await upgrades.erc1967.getImplementationAddress(box.address)," getImplementationAddress")
    console.log(await upgrades.erc1967.getAdminAddress(box.address)," getAdminAddress")    
  });
 
  // Test case
  it('retrieve returns a value previously initialized', async function () {
    // Test if the returned value is the same one
    // Note that we need to use strings to compare the 256 bit integers
    expect((await box.retrieve()).toString()).to.equal('42');
  });
});