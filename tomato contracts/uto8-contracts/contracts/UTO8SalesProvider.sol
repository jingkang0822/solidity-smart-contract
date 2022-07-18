// SPDX-License-Identifier: MIT
pragma solidity ^0.8.1;

import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import {SafeMath} from "@openzeppelin/contracts/utils/math/SafeMath.sol";

//import "hardhat/console.sol";

contract UTO8SalesProvider is Ownable {
    UTO8Box[] public uto8Boxes;
    address public operator;

    //user address => (uto8BoxId => swaped quantity)
    mapping(address => mapping(uint256 => uint256)) public userSwapped;

    //uto8BoxId => total swapped quantity
    mapping(uint256 => uint256) public boxTotalSwapped;

    event SwapLog(
        uint256 indexed uto8BoxId,
        address userAddress,
        uint256 swapAmount
    );

    struct UTO8Box {
        uint256 availableQuantity;
        uint256 exchangeRate;
        uint256 singleLimit;
        uint256 minUnit;
        uint256 saleTimeStart;
        uint256 saleTimeEnd;
    }

    constructor(address _operatorAddress) {
        operator = _operatorAddress;
    }

    function addUTO8Box(UTO8Box memory _uto8Box) public onlyOwner {
        uto8Boxes.push(_uto8Box);
    }

    function checkIsUserCanSwap(
        address userAddress,
        uint256 uto8BoxId,
        uint256 swapQuantity
    ) public view returns (bool) {
        UTO8Box storage box = uto8Boxes[uto8BoxId];

        uint256 oriTotalSwapped = userSwapped[userAddress][uto8BoxId];
        uint256 newTotalSwapped = oriTotalSwapped + swapQuantity;

        return box.singleLimit >= newTotalSwapped;
    }

    function addUserSwapHistory(
        address userAddress,
        uint256 uto8BoxId,
        uint256 swapQuantity
    ) public returns (uint256 remainQuantity) {
        require(msg.sender == operator, "invalid operator");

        UTO8Box storage box = uto8Boxes[uto8BoxId];

        uint256 oriTotalSwapped = userSwapped[userAddress][uto8BoxId];
        uint256 oriBoxTotalSwapped = boxTotalSwapped[uto8BoxId];
        uint256 newTotalSwapped = oriTotalSwapped + swapQuantity;

        //update quantity
        userSwapped[userAddress][uto8BoxId] = newTotalSwapped;

        emit SwapLog(uto8BoxId, userAddress, swapQuantity);

        //update box total swap quantity
        boxTotalSwapped[uto8BoxId] = oriBoxTotalSwapped + swapQuantity;

        //return remains
        remainQuantity = box.singleLimit - newTotalSwapped;
    }

    function getUTO8BoxInfo(uint256 _uto8BoxId)
        public
        view
        returns (
            uint256 availableQuantity,
            uint256 exchangeRate,
            uint256 singleLimit,
            uint256 minUnit,
            uint256 saleTimeStart,
            uint256 saleTimeEnd
        )
    {
        UTO8Box storage box = uto8Boxes[_uto8BoxId];
        availableQuantity = box.availableQuantity;
        exchangeRate = box.exchangeRate;
        singleLimit = box.singleLimit;
        minUnit = box.minUnit;
        saleTimeStart = box.saleTimeStart;
        saleTimeEnd = box.saleTimeEnd;
    }
}
