// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PayEth {
    function withdraw(address payable withdrawer) public {
        withdrawer.transfer(address(this).balance);
    }

    function deposit(uint256 amount) payable public {
        require(msg.value == amount, "Need to send excat amount.");
        // nothing else to do!
    }

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}