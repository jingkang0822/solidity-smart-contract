// SPDX-License-Identifier: MIT
pragma solidity ^0.8.1;

import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";
import {SafeMath} from "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "hardhat/console.sol";

contract SalesProvider is VRFConsumerBase, Ownable {
    using SafeMath for uint256;
    bytes32 internal keyHash;
    uint256 internal fee;
    uint256 public randomResult;
    address public operator;

    BlindBox[] public blindBoxes;
    PiamonTemplate[] public piamonTemplates;
    //keep white list for a blindbox
    mapping(uint256 => WhiteList[]) public blindBoxWhiteList;
    //requestId => blindBoxId
    mapping(bytes32 => uint256) vrfRequestsForBlindBox;
    //user address => (blindboxId => minted quantity)
    mapping(address => mapping(uint256 => uint256))
        public blindboxUserMintQuantity;
    //blindbox Id => blindBoxSetting
    mapping(uint256 => BlindBoxSetting) public blindBoxSettings;

    event UnboxLog(uint256 indexed blindboxId, uint256 vrfNumber);

    struct BlindBox {
        string name;
        string imageUrl;
        uint256 tokenIdStart;
        string description;
        string piamonMetadataUrl;
        uint256 price;
        uint256 saleTimeStart;
        uint256 saleTimeEnd;
        bool isSaleOpen;
        uint256 totalQuantity;
        uint256 unboxTime;
        uint256 vrfNumber;
    }

    struct BlindBoxSetting {
        uint256 blindBoxId;
        uint256 purchaseLimit;
    }

    struct WhiteList {
        address minterAddress;
        uint256 price;
        uint256 availableQuantity;
    }

    struct PiamonTemplate {
        uint256 templateId;
        uint256 tokenIdStart;
        string metadataURI;
        uint256 price;
        uint256 totalQuantity;
    }

    constructor(address _operatorAddress)
        VRFConsumerBase(
            0x8C7382F9D8f56b33781fE506E897a4F1e2d17255, //VRF coordinator
            0x326C977E6efc84E512bB9C30f76E30c160eD06FB //LINK token address
        )
    {
        keyHash = 0x6e75b569a01ef56d18cab6a8e71e6600d6ce853834d4a5748b720d06f878b3a4;
        fee = 0.0001 * 10**18; // 0.1 LINK

        operator = _operatorAddress;
    }

    function getRandomNumberForBlindBox(uint256 blindBoxId)
        public
        onlyOwner
        returns (bytes32 requestId)
    {
        require(
            LINK.balanceOf(address(this)) > fee,
            "Not enough LINK in contract"
        );
        requestId = requestRandomness(keyHash, fee);
        vrfRequestsForBlindBox[requestId] = blindBoxId;
        //return requestRandomness(keyHash, fee);
    }

    function fulfillRandomness(bytes32 requestId, uint256 randomness)
        internal
        override
    {
        //get blindbox by referring the requestId
        uint256 totalQty = blindBoxes[vrfRequestsForBlindBox[requestId]]
            .totalQuantity;
        //uint256 totalQty = 8000;
        randomResult = randomness.mod(totalQty).add(1);
        //update vrfNumber in blindbox
        blindBoxes[vrfRequestsForBlindBox[requestId]].vrfNumber = randomResult;
        //blindBoxes[0].vrfNumber = randomResult;

        emit UnboxLog(vrfRequestsForBlindBox[requestId], randomResult);
    }

    function addBlindBox(BlindBox memory _blindBox) public onlyOwner {
        blindBoxes.push(_blindBox);
    }

    function addBlindBoxSetting(
        uint256 _blindBoxId,
        BlindBoxSetting memory _blindBoxSetting
    ) public onlyOwner {
        blindBoxSettings[_blindBoxId] = _blindBoxSetting;
    }

    function addWhiteListStruct(
        uint256 _blindBoxId,
        WhiteList memory _whiteList
    ) public onlyOwner {
        blindBoxWhiteList[_blindBoxId].push(_whiteList);
    }

    function addPiamonTemplateStruct(PiamonTemplate memory _template)
        public
        onlyOwner
    {
        piamonTemplates.push(_template);
    }

    function checkIsBlindBoxIdExist(uint256 _blindBoxId) public view returns (bool) {
        return _blindBoxId >= 0 && _blindBoxId < blindBoxes.length;
    }

    function checkIsSaleOpen(uint256 _blindBoxId) public view returns (bool) {
        return blindBoxes[_blindBoxId].isSaleOpen;
    }

    function checkIsSaleStart(uint256 _blindBoxId) public view returns (bool) {
        return blindBoxes[_blindBoxId].saleTimeStart <= block.timestamp;
    }

    function checkIsSaleEnd(uint256 _blindBoxId) public view returns (bool) {
        return blindBoxes[_blindBoxId].saleTimeEnd > block.timestamp;
    }

    function getSaleTotalQuantity(uint256 _blindBoxId)
        public
        view
        returns (uint256)
    {
        return blindBoxes[_blindBoxId].totalQuantity;
    }

    function getSalePrice(uint256 _blindBoxId) public view returns (uint256) {
        return blindBoxes[_blindBoxId].price;
    }

    function getBlindBoxTokenIdStart(uint256 _blindBoxId)
        public
        view
        returns (uint256 tokenIdStart)
    {
        BlindBox storage blindBox = blindBoxes[_blindBoxId];
        tokenIdStart = blindBox.tokenIdStart;
    }

    function getBlindBoxInfo(uint256 _blindBoxId)
        public
        view
        returns (
            string memory name,
            string memory imageUrl,
            string memory description,
            string memory piamonMetadataUrl,
            uint256 totalQuantity,
            uint256 vrfNumber
        )
    {
        BlindBox storage blindBox = blindBoxes[_blindBoxId];
        name = blindBox.name;
        imageUrl = blindBox.imageUrl;
        description = blindBox.description;
        piamonMetadataUrl = blindBox.piamonMetadataUrl;
        totalQuantity = blindBox.totalQuantity;
        vrfNumber = blindBox.vrfNumber;
    }

    function getTemplate(uint256 _templateId)
        public
        view
        returns (
            string memory metadataURI,
            uint256 tokenIdStart,
            uint256 price,
            uint256 totalQuantity
        )
    {
        PiamonTemplate storage template = piamonTemplates[_templateId];
        metadataURI = template.metadataURI;
        price = template.price;
        totalQuantity = template.totalQuantity;
        tokenIdStart = template.tokenIdStart;
    }

    function checkIsWhiteListed(uint256 _blindBoxId, address _address)
        public
        view
        returns (bool)
    {
        bool isInWhiteList = false;

        WhiteList[] storage lists = blindBoxWhiteList[_blindBoxId];
        for (uint256 i = 0; i < lists.length; i++) {
            WhiteList storage whiteList = lists[i];
            if (whiteList.minterAddress == _address) {
                isInWhiteList = true;
                break;
            }
        }

        return isInWhiteList;
    }

    function getWhiteList(uint256 _blindBoxId, address _address)
        public
        view
        returns (uint256 availableQuantity, uint256 price)
    {
        WhiteList[] storage lists = blindBoxWhiteList[_blindBoxId];
        for (uint256 i = 0; i < lists.length; i++) {
            WhiteList storage whiteList = lists[i];
            if (whiteList.minterAddress == _address) {
                availableQuantity = whiteList.availableQuantity;
                price = whiteList.price;
                break;
            }
        }
    }

    function decreaseWhiteListAvailableQuantity(
        uint256 _blindBoxId,
        address _address
    ) public returns (uint256 remainQuantity) {
        require(msg.sender == operator, "invalid operator");
        //console.log("Operator", operator);
        //console.log("msg.sender", msg.sender);
        WhiteList[] storage lists = blindBoxWhiteList[_blindBoxId];
        for (uint256 i = 0; i < lists.length; i++) {
            WhiteList storage whiteList = lists[i];
            if (whiteList.minterAddress == _address) {
                if (whiteList.availableQuantity > 0) {
                    whiteList.availableQuantity--;
                }
                remainQuantity = whiteList.availableQuantity;
                break;
            }
        }
    }

    function getUserBlindboxTotalMintedCount(
        uint256 _blindBoxId,
        address _address
    ) public view returns (uint256 totlMintedCount) {
        totlMintedCount = blindboxUserMintQuantity[_address][_blindBoxId];
    }

    function checkIfUserUnderBlindBoxMintLimit(
        uint256 _blindBoxId,
        address _address
    ) public view returns (bool) {
        return
            blindboxUserMintQuantity[_address][_blindBoxId] <
            blindBoxSettings[_blindBoxId].purchaseLimit;
    }

    function increaseUserBlindboxTotalMintedCount(
        uint256 _blindBoxId,
        address _address
    ) public returns (uint256 totalMintedCount) {
        require(msg.sender == operator, "invalid operator");
        //console.log("Operator", operator);
        //console.log("msg.sender", msg.sender);
        uint256 mintedQty = blindboxUserMintQuantity[_address][_blindBoxId];
        blindboxUserMintQuantity[_address][_blindBoxId] = mintedQty + 1;
        totalMintedCount = blindboxUserMintQuantity[_address][_blindBoxId];
    }
}
