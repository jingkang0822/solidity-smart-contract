// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract My1155 is ERC1155, Ownable {

    uint64 public constant CAPTAIN_AMERICA = 0;
    uint64 public constant THOR = 1;
    uint64 public constant IRON_MAN = 2;
    uint64 public constant SPIDER_MAN = 3;

    constructor() ERC1155("https://api.frank.hk/api/nft/demo/1155/marvel/{id}.json") {
        _mint(msg.sender, CAPTAIN_AMERICA, 10 ** 18, "");
        _mint(msg.sender, THOR, 1, "");
        _mint(msg.sender, IRON_MAN, 5, "");
        _mint(msg.sender, SPIDER_MAN, 10, "");
    }

    function setURI(string memory newuri) public onlyOwner {
        _setURI(newuri);
    }
}