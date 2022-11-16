// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IGatekeeperTwo {
    function enter(bytes8 _gateKey) external returns (bool);
}

contract HackGateKeeperTwo {
    address levelInstance = address(0x131793146acD18A6B939f6911194d4a54C36BB1B);
    
    constructor() {
      unchecked {
          bytes8 key = bytes8(uint64(bytes8(keccak256(abi.encodePacked(address(this))))) ^ (uint64(0) - 1));
          IGatekeeperTwo(levelInstance).enter(key);
      }
    }
}
