// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SelfDestruct {

    function collect() public payable returns(uint) {
        return address(this).balance;
    }

    function selfDestroy() public {
        address payable addr = payable(address(0x0854679c5bdeC27799a2e821ee00a9b1ad066c62));
        selfdestruct(addr);
    }
}
