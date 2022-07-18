// SPDX-License-Identifier: MIT
pragma solidity ^0.8.1;
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "./UTO8.sol";

contract Vendor is Ownable {
    UTO8 uto8;
    AggregatorV3Interface internal priceFeed;

    constructor(address tokenAddress, address feedAddress) {
        uto8 = UTO8(tokenAddress);
        priceFeed = AggregatorV3Interface(feedAddress);
    }

    function buyUTO8(uint256 amount) public payable {
        //require(amount * 100 <= msg.value);
        (int256 price, uint8 decimal) = getLatestPrice();

        uint256 requireWei = ((10**decimal) / uint256(price)) * (10**18) * amount;
        require(requireWei <= msg.value, "Pay value is not enough");
        address ownerAddress = owner();
        payable(ownerAddress).transfer(msg.value);
        bool tokenSent = uto8.transferFrom(ownerAddress, msg.sender, amount);
        require(tokenSent, "Failed to buy UTO8");
    }

    function getLatestPrice() public view returns (int256, uint8) {
        (
            ,
            /*uint80 roundID*/
            int256 price, /*uint startedAt*/ /*uint timeStamp*/
            ,
            ,

        ) = /*uint80 answeredInRound*/
            priceFeed.latestRoundData();
        uint8 decimal = priceFeed.decimals();
        return (price, decimal);
    }
}
