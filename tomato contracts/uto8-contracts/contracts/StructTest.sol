// SPDX-License-Identifier: MIT
pragma solidity ^0.8.1;

import "hardhat/console.sol";

contract StructTest {

    struct ST {
        string name;
        string symbol;
        uint256 id;
    }

    constructor() {
    }

    function in_struct(ST memory input) public view {
        console.log("Input ST:");
        console.log(input.name);
        console.log(input.symbol);
        console.log(input.id);
    }
}
