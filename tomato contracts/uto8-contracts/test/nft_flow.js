const { expect } = require("chai");
const {
  constants,
  expectRevert,
} = require('@openzeppelin/test-helpers');

describe("Piya minting flow", function () {
  let uto8;
  let piya;
  let owner;
  let addr1;
  let addr2;
  let addrs;

  before(async function () {
    
    // Get all operate wallet
    [owner, addr1, addr2, ...addrs] = await ethers.getSigners();


    // Deploy UTO8 contract for buying NFT
    uto8_contract = await ethers.getContractFactory("UTO8");
    uto8 = await uto8_contract.deploy();
    await uto8.deployed();

    // Deploy Piya NFT
    piya_contract = await ethers.getContractFactory("Piamon");
    piya = await piya_contract.deploy(uto8.address);
    await piya.deployed();

    // Deploy NFT Sales Provider
    sales_contract = await ethers.getContractFactory("SalesProvider");
    sale_provider = await sales_contract.deploy(piya.address);
    await sale_provider.deployed();

    
    // Test struct input
    // struct_contract = await ethers.getContractFactory("StructTest");
    // struct_deployed = await struct_contract.deploy();
    // await struct_deployed.deployed();
    
    // struct_obj = {
    //   name: 'Sales Event 1',
    //   symbol: 'Etws',
    //   id: 1658211978
    // }

    // await struct_deployed.in_struct(struct_obj);

  });
  beforeEach(async function () {
    
  });

  describe("Set Sales Provider in Piya", function () {
    
    it("ERC20 checker", async function () {
      // await uto8.totalSupply(sale_provider.address);
      // await expect(await uto8.totalSupply());
      // console.log("Total supply:", await uto8.totalSupply())

      const ownerBalance = await uto8.balanceOf(owner.address);
      expect(await uto8.totalSupply()).to.equal(ownerBalance);
    });

    it("Only owner can set Sales Provider", async function () {
      await piya.setSalesProvider(sale_provider.address);
      await expect(
        piya.connect(addr1).setSalesProvider(sale_provider.address)
      ).to.be.revertedWith(
        "Ownable: caller is not the owner"
      );
    });

    it("Create blindbox sales event", async function () {
      
      blindboxEvent = {
        name: 'Sales Event 1',
        imageUrl: '',
        tokenIdStart: 0,
        description: 'The dragon creature named PIYA is an origin pet from Utopia No.8, it was born with an affinity to light elements. Although their appearances are adorkable, they seem to have incredible potential for growth.',
        piamonMetadataUrl: 'https://testnet.uto8.io/metadata/',
        price: 100,
        saleTimeStart: 1658369988,
        saleTimeEnd:   1658402388,
        isSaleOpen: true,
        totalQuantity: 10,
        unboxTime: 1658402388,
        vrfNumber: 0,
      }
      await sale_provider.addBlindBox(blindboxEvent);

      blindboxSetting = {
        blindBoxId: 0,
        purchaseLimit: 5,
      }
      await sale_provider.addBlindBoxSetting(0, blindboxSetting);

    });

    it("Only whitelist can mint", async function () {
      
      // Check the NFT's balance of owner 
      expect(
        await piya.balanceOf(owner.address)
      ).to.be.equal(0);

      // Should approve sales contract can transfer UTO8
      await uto8.approve(piya.address, 9999999);
      // console.log(await uto8.allowance(owner.address, piya.address));
      
      // Still no in the whitelist
      // Need to double check again, this should not pass the minting function
      // Should return error message "not in the whitelist"
      productType = 1;
      blindBoxId = 0;
      await expect(piya.mintTo(
        owner.address,
        productType,
        blindBoxId
      ))
      .to.emit(piya, "Transfer")
      .withArgs(constants.ZERO_ADDRESS, owner.address, 0);

      // Check the NFT's balance of addr1 
      expect(
        await piya.balanceOf(owner.address)
      ).to.be.equal(1);
      
      // Should approve sales contract can transfer UTO8 from addr1
      await uto8.connect(addr1).approve(piya.address, 9999999);
      // Send tokens to addr1
      await expect(uto8.transfer(addr1.address, 1000))
        .to.emit(uto8, "Transfer")
        .withArgs(owner.address, addr1.address, 1000);
      
      // addr1 not in the whitelist, so can not mint.
      // Should return error message "not in the whitelist"
      await expect(piya.connect(addr1).mintTo(
        addr1.address,
        productType,
        blindBoxId
      ))
      .to.emit(piya, "Transfer")
      .withArgs(constants.ZERO_ADDRESS, addr1.address, 1);
      
      // Check the NFT's balance of owner 
      expect(
        await piya.balanceOf(addr1.address)
      ).to.be.equal(1);

      // Check if address in the whitelist
      expect(
        await sale_provider.checkIsWhiteListed(blindBoxId, owner.address)
      ).to.be.equal(false);
      
      whiteListedInfo = {
        minterAddress: owner.address,
        price: 100,
        availableQuantity: 3,
      }

      // Add whitelist address
      await sale_provider.addWhiteListStruct(blindBoxId, whiteListedInfo);

      // Address should be in the whitelist
      expect(
        await sale_provider.checkIsWhiteListed(blindBoxId, owner.address)
      ).to.be.equal(true);
      
      // Minting NFT
      await expect(piya.mintTo(
        owner.address,
        productType,
        blindBoxId
      ))
      .to.emit(piya, "Transfer")
      .withArgs(constants.ZERO_ADDRESS, owner.address, 2);

      // After minting, check the NFT's balance of owner 
      expect(
        await piya.balanceOf(owner.address)
      ).to.be.equal(2);

    });

    it("Check token uri", async function () {
      
      console.log(await piya.tokenURI(0));

      // Check the NFT's balance of owner 
      // expect(
      //   await piya.tokenURI(0)
      // ).to.be.equal(0);
    });

    it("Check user total minted count", async function () {
      
      // Before mint, should equal none of NFT in addr2
      expect(
        await sale_provider.getUserBlindboxTotalMintedCount(blindBoxId, addr2.address)
      ).to.be.equal(0);
      
      // Send tokens to addr2 and approve to NFT contract
      await expect(uto8.transfer(addr2.address, 1000))
        .to.emit(uto8, "Transfer")
        .withArgs(owner.address, addr2.address, 1000);
      await uto8.connect(addr2).approve(piya.address, 9999999);
      
      tokenId = 3;
      // Mint again
      await expect(piya.connect(addr2).mintTo(
        addr2.address,
        productType,
        blindBoxId
      ))
      .to.emit(piya, "Transfer")
      .withArgs(constants.ZERO_ADDRESS, addr2.address, tokenId++);
      
      // After mint, should have 1 counting in sale_provider
      expect(
        await sale_provider.getUserBlindboxTotalMintedCount(blindBoxId, addr2.address)
      ).to.be.equal(1);

      // Mint second time
      await expect(piya.connect(addr2).mintTo(
        addr2.address,
        productType,
        blindBoxId
      ))
      .to.emit(piya, "Transfer")
      .withArgs(constants.ZERO_ADDRESS, addr2.address, tokenId++);
      
      // After mint, should have 2 counting in sale_provider
      expect(
        await sale_provider.getUserBlindboxTotalMintedCount(blindBoxId, addr2.address)
      ).to.be.equal(2);
    });

  });
});
