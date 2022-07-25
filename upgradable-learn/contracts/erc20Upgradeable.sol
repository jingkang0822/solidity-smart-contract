// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "../openzeppelin-contracts-upgradeable/contracts/token/ERC20/ERC20Upgradeable.sol";
import "../openzeppelin-contracts-upgradeable/contracts/access/OwnableUpgradeable.sol";
import "../openzeppelin-contracts-upgradeable/contracts/proxy/utils/Initializable.sol";

contract UpgradeableToken is Initializable, ERC20Upgradeable, OwnableUpgradeable {
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize() initializer public {
        __ERC20_init("UpgradeableToken", "UDT");
        __Ownable_init();
    }

    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}