// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HackPreservation {

  // public library contracts 
  address public timeZone1Library;
  address public timeZone2Library;
  address public owner; 

  constructor() public {
    owner = msg.sender;
  }
 
  // set the time for timezone 1
  function setFirstTime(uint256 player) public {
    owner = msg.sender;
  }

  function convertAddressToUnit(address _addr) public pure returns (uint256) {
    return uint256(bytes32(abi.encodePacked(_addr)));
  }
}