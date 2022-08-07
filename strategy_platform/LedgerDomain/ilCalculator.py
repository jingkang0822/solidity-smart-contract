def Amount_CAL(P_entry, P_lower, P_upper, initial_base_token_amount):
    P_entry_ = P_entry
    if P_entry_ > P_upper:
        P_entry_ = P_upper
    elif P_entry_ < P_lower:
        P_entry_ = P_lower
    base_token_ratio = (P_entry_ ** (1 / 2) - P_lower ** (1 / 2)) / (P_entry_ * (P_upper ** (1 / 2) - P_entry_ ** (1 / 2)) / (P_entry_ ** (1 / 2) * P_upper ** (1 / 2)) + (P_entry_ ** (1 / 2) - P_lower ** (1 / 2)))
    target_token_ratio = (P_entry_ * (P_upper ** (1 / 2) - P_entry_ ** (1 / 2)) / (P_entry_ ** (1 / 2) * P_upper ** (1 / 2))) / (P_entry_ * (P_upper ** (1 / 2) - P_entry_ ** (1 / 2)) / (P_entry_ ** (1 / 2) * P_upper ** (1 / 2)) + (P_entry_ ** (1 / 2) - P_lower ** (1 / 2)))
    base_token_amount = initial_base_token_amount * base_token_ratio
    target_token_in_base_token_amount = initial_base_token_amount * target_token_ratio
    target_token_amount = target_token_in_base_token_amount / P_entry
    return base_token_amount, target_token_amount, target_token_in_base_token_amount

def IL_CAL(P_entry, P_exit, P_lower, P_upper, initial_base_token_amount):
    base_token_amount, target_token_amount, target_token_in_base_token_amount = Amount_CAL(P_entry, P_lower, P_upper, initial_base_token_amount)

    if P_entry < P_lower:
        L = target_token_amount / (1/P_lower**(1/2)-1/P_upper**(1/2))
    elif P_entry > P_upper:
        L = base_token_amount / (P_upper**(1/2)-P_lower**(1/2))
    else:
        L = base_token_amount / (P_entry ** (1 / 2) - P_lower ** (1 / 2))

    base_token_virtual_amount = L * P_lower**(1/2)
    target_token_virtual_amount = L / P_upper**(1/2)

    if P_lower <= P_exit <= P_upper:
        target_token_remain_amount = L / P_exit ** (1 / 2) - target_token_virtual_amount
        base_token_remain_amount = L * P_exit ** (1 / 2) - base_token_virtual_amount

    elif P_exit < P_lower:
        target_token_remain_amount = L/P_lower**(1/2) -  target_token_virtual_amount
        base_token_remain_amount = L*P_lower**(1/2) - base_token_virtual_amount

    elif P_exit > P_upper:
        target_token_remain_amount = L/P_upper**(1/2) - target_token_virtual_amount
        base_token_remain_amount = L*P_upper**(1/2) - base_token_virtual_amount

    holder_value = base_token_amount + target_token_amount * P_exit
    lp_value = base_token_remain_amount + target_token_remain_amount * P_exit

    IL = holder_value - lp_value
    IL_percentage = IL / holder_value

    return target_token_remain_amount, base_token_remain_amount, holder_value, lp_value, IL, IL_percentage

if __name__ == '__main__':
    ## initial amount
    P_0 = 3000
    P_lower = 1500
    P_upper = 6000
    Initial_USDC = 100000
    print(f"current price: {P_0}")
    print(f"Price_Range: {P_lower}~{P_upper}")

    USDC_Amount, ETH_Amount, ETH_Amount_USDC = Amount_CAL(P_entry=P_0, P_lower=P_lower, P_upper=P_upper, initial_base_token_amount=Initial_USDC)
    print(f"Initial_USDC: {Initial_USDC}")
    print(f"Add_USDC_Amount: {USDC_Amount}")
    print(f"Add_ETH_Amount: {ETH_Amount}")
    print(f"Add_ETH_Amount_USDC: {ETH_Amount_USDC}")
    print("-"*100)

    ## amount after price change
    P_1 = 3100
    print(f"last price: {P_1}")
    ETH_Remain_Amount, USDC_Remain_Amount, holder_value, lp_value, IL, IL_percentage = IL_CAL(P_entry=P_0, P_exit=P_1, P_lower=P_lower, P_upper=P_upper, initial_base_token_amount=Initial_USDC)
    print(f"USDC_Remain_Amount: {USDC_Remain_Amount}")
    print(f"ETH_Remain_Amount: {ETH_Remain_Amount}")
    print(f"holder_value: {holder_value}")
    print(f"lp_value: {lp_value}")
    print(f"IL: {IL}({IL_percentage*100}%)")

