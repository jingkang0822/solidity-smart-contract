// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract ZombieToken is ERC20 {
    
    constructor() ERC20("ZombieToken", "ZTN") public {
        _mint(msg.sender, 1e6);
    }
}
