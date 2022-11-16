// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HackPrivacy {

  constructor() public {
  }
  
  function convert(bytes32 data) public pure returns (bytes16) {
    return bytes16(data);
  }
}
