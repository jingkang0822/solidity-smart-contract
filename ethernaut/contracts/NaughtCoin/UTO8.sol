//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.1;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract UTO8 is ERC20 {
    uint8 constant decimal = 6;
    uint256 constant initial_supply = 1e9 * (10 ** decimal);

    constructor() ERC20("Utopia8", "UTO8") {
        _mint(msg.sender, initial_supply);
    }

    function decimals() public pure override returns (uint8) {
        return decimal;
    }
}
