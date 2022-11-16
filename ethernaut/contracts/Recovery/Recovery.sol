// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Recovery {

function setSecondTime(address _addr) public returns(address) {
    // return address(keccak256(abi.encodePacked('0xd6', '0x94', _addr, '0x01')));
    return _addr;
  }
}
