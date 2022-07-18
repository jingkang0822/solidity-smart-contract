//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.1;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract UTO8 is ERC20 {
    uint256 constant _initial_supply = 100000000 * (10**18);

    constructor() ERC20("UTO8", "UTO8") {
        _mint(msg.sender, _initial_supply);
    }
}
