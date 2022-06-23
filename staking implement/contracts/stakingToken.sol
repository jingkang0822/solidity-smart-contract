// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";


/**
* @title Staking Token (STK)
* @author Alberto Cuesta Canada
* @notice Implements a basic ERC20 staking token with incentive distribution.
*/
contract StakingToken is ERC20, Ownable {

    /**
    * @notice We usually require to know who are all the stakeholders.
    */
    address[] internal stakeHolders;

    /**
    * @notice The stakes for each stakeholder.
    */
    mapping(address => uint256) internal stakes;

    /**
    * @notice The accumulated rewards for each stakeholder.
    */
    mapping(address => uint256) internal rewards;


    constructor(uint256 _initialSupply) ERC20("StakedToken", "JKT") {
        _mint(msg.sender, _initialSupply);
    }

    /**
    * @notice A method to check if an address is a stakeholder.
    * @param _address The address to verify.
    * @return bool, uint256 Whether the address is a stakeholder,
    * and if so its position in the stakeholders array.
    */
    function isStakeHolder(address _address)
        public
        view
        returns(bool, uint256)
    {
        for (uint256 s = 0; s < stakeHolders.length; s += 1){
            if (_address == stakeHolders[s]) return (true, s);
        }
        return (false, 0);
    }

    /**
    * @notice A method to add a stakeholder.
    * @param _stakeHolder The stakeholder to add.
    */
    function addStakeHolder(address _stakeHolder)
        public
    {
        (bool _isStakeHolder, ) = isStakeHolder(_stakeHolder);
        if(!_isStakeHolder) stakeHolders.push(_stakeHolder);
    }

    /**
    * @notice A method to remove a stakeholder.
    * @param _stakeHolder The stakeholder to remove.
    */
    function removeStakeHolder(address _stakeHolder)
        public
    {
        (bool _isStakeHolder, uint256 s) = isStakeHolder(_stakeHolder);
        if(_isStakeHolder){
            stakeHolders[s] = stakeHolders[stakeHolders.length - 1];
            stakeHolders.pop();
        }
    }

    /**
    * @notice A method to retrieve the stake for a stakeholder.
    * @param _stakeholder The stakeholder to retrieve the stake for.
    * @return uint256 The amount of wei staked.
    */
    function stakeOf(address _stakeholder)
        public
        view
        returns(uint256)
    {
        return stakes[_stakeholder];
    }

    /**
    * @notice A method to the aggregated stakes from all stakeholders.
    * @return uint256 The aggregated stakes from all stakeholders.
    */
    function totalStakes()
        public
        view
        returns(uint256)
    {
        uint256 _totalStakes = 0;
        for (uint256 s = 0; s < stakeHolders.length; s += 1){
            _totalStakes += stakes[stakeHolders[s]];
        }
        return _totalStakes;
    }

    /**
    * @notice A method for a stakeholder to create a stake.
    * @param _stake The size of the stake to be created.
    */
    function createStake(uint256 _stake)
        public
    {
        _burn(msg.sender, _stake);
        if(stakes[msg.sender] == 0) addStakeHolder(msg.sender);
        stakes[msg.sender] += _stake;
    }

    /**
    * @notice A method for a stakeholder to remove a stake.
    * @param _stake The size of the stake to be removed.
    */
    function removeStake(uint256 _stake)
        public
    {
        stakes[msg.sender] -= _stake;
        if(stakes[msg.sender] == 0) removeStakeHolder(msg.sender);
        _mint(msg.sender, _stake);
    }

    /**
    * @notice A method to allow a stakeholder to check his rewards.
    * @param _stakeholder The stakeholder to check rewards for.
    */
    function rewardOf(address _stakeholder)
        public
        view
        returns(uint256)
    {
        return rewards[_stakeholder];
    }

    /**
    * @notice A method to the aggregated rewards from all stakeholders.
    * @return uint256 The aggregated rewards from all stakeholders.
    */
    function totalRewards()
        public
        view
        returns(uint256)
    {
        uint256 _totalRewards = 0;
        for (uint256 s = 0; s < stakeHolders.length; s += 1){
            _totalRewards += rewards[stakeHolders[s]];
        }
        return _totalRewards;
    }

    /**
    * @notice A simple method that calculates the rewards for each stakeholder.
    * @param _stakeholder The stakeholder to calculate rewards for.
    */
    function calculateReward(address _stakeholder)
        public
        view
        returns(uint256)
    {
        return stakes[_stakeholder] / 100;
    }

    /**
    * @notice A method to distribute rewards to all stakeholders.
    */
    function distributeRewards()
        public
        onlyOwner
    {
        for (uint256 s = 0; s < stakeHolders.length; s += 1){
            address stakeholder = stakeHolders[s];
            uint256 reward = calculateReward(stakeholder);
            rewards[stakeholder] += reward;
        }
    }

    /**
    * @notice A method to allow a stakeholder to withdraw his rewards.
    */
    function withdrawReward()
        public
    {
        uint256 reward = rewards[msg.sender];
        rewards[msg.sender] = 0;
        _mint(msg.sender, reward);
    }
}