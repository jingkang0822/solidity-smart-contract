// SPDX-License-Identifier: MIT
pragma solidity ^0.8.1;
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./UTO8SalesProvider.sol";

contract UTO8Vendor is Ownable {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;
    IERC20 uto8;
    IERC20 usdt;
    UTO8SalesProvider uto8SalesProvider;

    event USDTReceived(address _from, uint256 _amount);

    constructor(address uto8TokenAddress, address ustdTokenAddress) {
        uto8 = IERC20(uto8TokenAddress);
        usdt = IERC20(ustdTokenAddress);
    }

    function setUTO8SalesProvider(address contractAddress) public onlyOwner {
        uto8SalesProvider = UTO8SalesProvider(contractAddress);
    }

    function swapUTO8(uint256 uto8BoxId, uint256 amount) public payable {
        require(
            uto8SalesProvider.checkIsUserCanSwap(msg.sender, uto8BoxId, amount),
            "Exceed single limitation"
        );

        (, uint256 exchangeRate, , uint256 minUint, , ) = uto8SalesProvider
            .getUTO8BoxInfo(uto8BoxId);

        //check minUint
        uint256 remains = amount % minUint;
        require(remains == 0, "Swap amount should be a multiple of minUnit");

        //get rate and calculate require usdt
        uint256 requiredUsdt = exchangeRate * (10**4) * amount;

        //check if user have enough USDT
        uint256 userUsdtBalance = usdt.balanceOf(msg.sender);
        require(
            userUsdtBalance > requiredUsdt,
            "Don't have enough USDT to swap"
        );

        address ownerAddress = owner();

        //check if contract owner has enough UTO8
        uint256 contractOwnerUTO8Balance = uto8.balanceOf(ownerAddress);
        require(
            contractOwnerUTO8Balance >= amount,
            "Contract owner does not have enough UTO8"
        );

        usdt.safeTransferFrom(msg.sender, ownerAddress, requiredUsdt);
        //require(usdtTokenSent, "Failed to send USDT to contract owenr");

        emit USDTReceived(msg.sender, requiredUsdt);

        uto8.safeTransferFrom(ownerAddress, msg.sender, amount * (10**18));
        //require(tokenSent, "Failed to send UTO8 to user");

        //add user swap record
        uto8SalesProvider.addUserSwapHistory(msg.sender, uto8BoxId, amount);
    }
}
