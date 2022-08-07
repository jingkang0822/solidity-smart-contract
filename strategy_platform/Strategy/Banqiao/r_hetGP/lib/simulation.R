source("price_range_prediction.R")

get_pool_info <- function(pool){#8181
  
  base_url = "http://office.teahouse.finance:5927/pools/info?network=eth_mainnet&pool="
  url = paste(base_url,pool, sep="")
  
  t = 10
  while(1){
    tryCatch({
      
      res = GET(url, timeout(t))
      raw_data = rawToChar(res$content)
      out = fromJSON(raw_data)
      break
      
    }, error = function(e) {
      print(e)
      t = t + 5
    })
    
    if (t > 20){
      break
    }
    
  }
  
  for (i in 1:10){
    if (!out$success) {
      res = RETRY("GET", url )
      raw_data = rawToChar(res$content)
      out = fromJSON(raw_data)
      Sys.sleep(2)
    } else{
      break
    }
  }
  out$data
}

get_position_info <- function(pool, block, amount, lower_tick, upper_tick, digits, str_query_base_amount){
  # amount0 = lp_in_token0
  base_url = "http://office.teahouse.finance:5927/pools/estimate/position_info"
  
  # http://office.teahouse.finance:8181/pools/estimate/position_info/by_amount0?network=eth_mainnet&pool=0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8
  # &amount0=463998416246&block=14067965&lowerTick=193740&upperTick=200820
  
  str_pool = paste("pool=",pool,sep="")
  base_url = paste(base_url,"/","by_",str_query_base_amount,"?","network=eth_mainnet&", sep="")
  options(scipen = 100)
  int_money = round(amount*10^digits)
  str_amount = paste(str_query_base_amount,"=", as.character(int_money),sep="")
  str_block = paste("block=",as.character(block),sep="")
  str_lower_tick = paste("lowerTick=",as.character(lower_tick),sep="")
  str_upper_tick = paste("upperTick=",as.character(upper_tick),sep="")
  parms = paste(str_pool,str_amount,str_block,str_lower_tick, str_upper_tick, sep="&")
  url = paste(base_url,parms,sep="")
  # res = GET(url)
  # raw_data = rawToChar(res$content)
  # out = fromJSON(raw_data)
  
  t = 10
  while(1){
    tryCatch({
      
      res = GET(url, timeout(t))
      raw_data = rawToChar(res$content)
      out = fromJSON(raw_data)
      break
      
    }, error = function(e) {
      print(e)
      t = t + 5
    })
    
    if (t > 65){
      break
    }
    
  }
  
  for (i in 1:10){
    if (!out$success) {
      res = RETRY("GET", url )
      raw_data = rawToChar(res$content)
      out = fromJSON(raw_data)
      Sys.sleep(2)
    } else{
      break
    }
  }
  out
}

get_fee_estimation <- function(pool, lower_tick, upper_tick, liquidity, start_block, end_block){
  
  base_url = "http://office.teahouse.finance:5927/pools/estimate/fee?network=eth_mainnet&"
  
  # http://office.teahouse.finance:8181/pools/estimate/fee?network=eth_mainnet&pool=0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8
  # &lowerTick=193740&upperTick=200820&liquidity=137919288532961335&startBlock=14067964&endBlock=14068499&humanReadable=false
  
  
  str_pool = paste("pool=",pool,sep="")
  str_lower_tick = paste("lowerTick=",as.character(lower_tick),sep="")
  str_upper_tick = paste("upperTick=",as.character(upper_tick),sep="")
  str_liquidity = paste("liquidity=",as.character(liquidity),sep="")
  str_start_block = paste("startBlock=",as.character(start_block),sep="")
  str_end_block = paste("endBlock=",as.character(end_block),sep="")
  str_read = "humanReadable=true"
  parms = paste(str_pool, str_lower_tick, str_upper_tick, str_liquidity,
                str_start_block, str_end_block, str_read,sep="&")
  url = paste(base_url,parms,sep="")
  # res = GET(url)
  # raw_data = rawToChar(res$content)
  # out = fromJSON(raw_data)
  
  t = 10
  while(1){
    tryCatch({
      
      res = GET(url, timeout(t))
      raw_data = rawToChar(res$content)
      out = fromJSON(raw_data)
      break
      
    }, error = function(e) {
      print(e)
      t = t + 5
    })
    
    if (t > 65){
      break
    }
    
  }
  
  
  for (i in 1:10){
    if (!out$success) {
      res = RETRY("GET", url )
      raw_data = rawToChar(res$content)
      out = fromJSON(raw_data)
      Sys.sleep(2)
    } else{
      break
    }
  }
  out
}

parameter_maker <- function(raw_param_vec){
  
  n <- round((raw_param_vec[1]+0.3)*30)#9~39
  q_set <- raw_param_vec[2]*0.099998+0.900001
  low_prob_set <- raw_param_vec[3]*0.099+0.001
  high_prob_set <- raw_param_vec[4]*0.0000009+0.999999
  
  param_set = list(n, q_set, low_prob_set, high_prob_set)
  names(param_set) = c('n', 'q_set', 'low_prob_set', 'high_prob_set')
  return(param_set)
}


freq_signal <- function(param_set, reg_time_points, set_reg_time, tick_spacing, max_bound_width, y, y_type, 
                        converter, lower_tick, upper_tick, token0_digits, token1_digits, quote_base_token){
  
  q_set = param_set$q_set
  low_prob_set = param_set$low_prob_set
  high_prob_set = param_set$high_prob_set
  
  ##### Step 2: hetGP method ##### 
  ##### Find the predictive distribution of ETH/USD on the next day #####
  #print(y[reg_time_points == set_reg_time])
  train_select = reg_time_points <= set_reg_time # as.Date(lubridate::now(tzone = "UTC"))
  time_select = reg_time_points[train_select]
  time_table = table(time_select)
  n = length(time_table)
  # print(c(n, param_set$n))
  # print(time_table)
  X = rep(1:n, table(time_select))/n
  Z = y[train_select]
  
  # fit hetGP model
  hetgp_fit <- fit_hetgp(X, Z)
  
  # prediction at the new day (1+1/n) given the fitted GP
  y_pred <- predict_distribuion (hetgp_fit, matrix(1+1/n, ncol = 1))
  
  # prediction mean and standard deviation
  pred_mean = y_pred$mean
  pred_std = y_pred$std
  
  if (y_type == 'tick') {
    
    raw_tick = y_pred$mean
    
  } else if (y_type == 'price'){
    
    raw_tick = price_to_tick(pred_mean, token0_digits, token1_digits, quote_base_token)
    #raw_tick = price_to_tick(pred_mean, 6, 18, 'token1')
  }
  
  ##### step 3: contruct the bound ##### 
  bound = get_tick_bound(raw_tick, tick_spacing, q_set, max_bound_width, y_pred, converter, token0_digits, token1_digits, quote_base_token)
  # cat("cumprob=",cumprob,"...\n")
  
  ##### step 4: do we need to replace the current bound    ##### 
  #####         with the bound in Step 3 ????              ##### 
  
  
  set_upper_tick = ifelse(is.null(upper_tick),bound$upper_tick, upper_tick)
  set_lower_tick = ifelse(is.null(lower_tick),bound$lower_tick, lower_tick)
  change_bound = ifelse(is.null(upper_tick) || is.null(lower_tick), TRUE, FALSE)
  
  #cat("no bound; new bound created...\n")
  
  x1 = tick_to_price(set_lower_tick, token0_digits, token1_digits, quote_base_token)
  x2 = tick_to_price(set_upper_tick, token0_digits, token1_digits, quote_base_token)
  
  #x1 = tick_to_price(set_lower_tick, 6, 18, 'token1')
  #x2 = tick_to_price(set_upper_tick, 6, 18, 'token1')
  
  if (y_type == 'tick'){
    
    contain_prob = cumprob_diff(set_lower_tick, set_upper_tick, pred_mean, pred_std)
    
  } else if (y_type == 'price') {
    
    contain_prob = cumprob_diff(x1, x2, pred_mean, pred_std)
    
  }
  
  if (contain_prob < low_prob_set | contain_prob > high_prob_set){
    
    set_upper_tick = bound$upper_tick
    set_lower_tick = bound$lower_tick
    change_bound = TRUE
  } 
  
  xgrid <- matrix(seq(0,1+1/n,0.01), ncol = 1)
  predictions <- predict(x = xgrid, object =  hetgp_fit)
  
  output = list(set_reg_time, set_lower_tick, set_upper_tick, change_bound, predictions)
  names(output) = c("set_reg_time", "lower_tick", "upper_tick", "change_bound", "predictions")
  ##### step 5: output current bound in currentbount.csv ##### 
  #bound_out <- data.frame("date"=Sys.Date(), "lower_lower"=set_lower_tick, "upper_tick"=set_upper_tick, "change_bound"=change_bound)
  #write.table(bound.out, file=current_bound_file_path, sep = ",", col.names = FALSE, row.names=FALSE, append = TRUE)
  return(output)
}


strategy_simulation <- function(pool, invest_amount, quote_base_token, pnl_base_token_option, back_test_data, test_param, start_t, end_t, 
                                detecion_freq, sampling_interval, max_tick_width, converter, y_type, unique_trade_t=FALSE, 
                                init_lower_tick=NULL, init_upper_tick=NULL){
  
  info = get_pool_info(pool)
  tick_spacing = info$tick_spacing
  token0_digits = info$token0_decimals
  token1_digits = info$token1_decimals
  
  trade_signal_df = get_trading_signals(back_test_data, test_param, start_t, end_t, detecion_freq, sampling_interval, tick_spacing, max_tick_width, converter, 
                                        y_type, token0_digits, token1_digits, quote_base_token, unique_trade_t, init_lower_tick, init_upper_tick)
  
  back_test(pool, pnl_base_token_option, token0_digits, token1_digits, trade_signal_df, invest_amount)
  
}

get_trading_signals <- function(back_test_data, test_param, start_t, end_t, detecion_freq, sampling_interval, tick_spacing, max_tick_width, converter, 
                                y_type, token0_digits, token1_digits, quote_base_token, truncate_trade_t, init_lower_tick=NULL, init_upper_tick=NULL) {
  # pnl_freq='raw'
  df = copy(back_test_data)
  str_freq = paste(detecion_freq,"hours", sep=" ")
  df['time_freq'] = floor_date(as.POSIXct(df$timestamp_utc), str_freq)
  
  if (sampling_interval > 0) {
    str_sampling_interval = paste(sampling_interval,"hours", sep=" ")
    df['samp_freq'] = floor_date(as.POSIXct(df$timestamp_utc), str_sampling_interval)
    df = df[!duplicated(df$samp_freq),]
  }
  
  trading_t_vec = seq(start_t, end_t , by=str_freq)
  
  my_lower_tick = init_lower_tick
  my_upper_tick = init_upper_tick
  my_result = data.table()
  
  for (trade_t in trading_t_vec){
    
    past_n_t = trade_t-test_param$n*24*60*60
    cond1 = as.POSIXct(df$timestamp_utc)<=trade_t
    cond2 = as.POSIXct(df$timestamp_utc)>=past_n_t
    price_data = subset(df, cond1&cond2)
    price_data = price_data[2:nrow(price_data),]
    
    not_null = !(is.null(my_lower_tick) & is.null(my_upper_tick))
    # do some preprocessing
    time_vec = price_data$time_freq
    t0 = as.POSIXct(past_n_t, origin="1970-01-01")
    t1 = as.POSIXct(trade_t, origin="1970-01-01")
    
    # freq_signal(param_set, reg_time_points, set_reg_time, tick_spacing, max_bound_width, y, y_type, 
    #   converter, lower_tick, upper_tick, token0_digits, token1_digits, quote_base_token)
    out = freq_signal(test_param, time_vec, trade_t, tick_spacing, max_tick_width, price_data$close,
                      y_type, converter, my_lower_tick, my_upper_tick, token0_digits, token1_digits, quote_base_token)
    my_lower_tick = out$lower_tick
    my_upper_tick = out$upper_tick
    
    x1 = tick_to_price(my_upper_tick, token0_digits, token1_digits, quote_base_token)
    x2 = tick_to_price(my_lower_tick, token0_digits, token1_digits, quote_base_token)
    
    if (x1 > x2){
      upper_price = x1
      lower_price = x2
    } else {
      upper_price = x2
      lower_price = x1
    }
    #print(as.POSIXct(trade_t, origin="1970-01-01"))
    eval_select = (trade_t <= df$time_freq) & (df$time_freq < trade_t + detecion_freq*60*60) 
    #eval_select = df$time_freq == as.POSIXct(trade_t, origin="1970-01-01")
    temp_df = as.data.table(df[eval_select, c("timestamp_unix", "timestamp_utc", 'samp_freq', "block_number",'close')])
    temp_df[,trading_t:=as.POSIXct(trade_t, origin="1970-01-01")]
    temp_df[,lower_tick:=out$lower_tick]
    temp_df[,upper_tick:= out$upper_tick]
    temp_df[,lower_price:= lower_price]
    temp_df[,upper_price:= upper_price]
    temp_df[,in_bound:=ifelse(close>=lower_price & close<=upper_price, TRUE, FALSE)]
    my_result = rbind(my_result, temp_df)
    #print(temp_df)
  }
  if (truncate_trade_t){
    
    row1 = my_result[!duplicated(my_result$trading_t),]
    row_last = my_result[ !duplicated(my_result[, c("trading_t")], fromLast=T),]
    out = rbind(row1, row_last)
    setorder(out, 'timestamp_unix')
    out
    #
  } else {
    my_result
  }
}

get_live_trading_signals <- function(back_test_data, test_param, t, detecion_freq, sampling_interval, tick_spacing, max_tick_width, converter,
                                     y_type, token0_digits, token1_digits, quote_base_token, init_lower_tick=NULL, init_upper_tick=NULL) {

  df = copy(back_test_data)
  str_sampling_interval = paste(sampling_interval,"hours", sep=" ")
  #assmue input k-bar data is 30 mins frequency
  t0 = as.POSIXct(df$timestamp_utc)[1]
  time_points = floor_date(seq(t0, t , by=str_sampling_interval), "30 mins")
  str_freq = paste(detecion_freq,"hours", sep=" ")
  df['time_freq'] = floor_date(as.POSIXct(df$timestamp_utc), str_freq)
  price_data = df[as.POSIXct(df$timestamp_utc) %in% time_points ,]
  my_lower_tick = init_lower_tick
  my_upper_tick = init_upper_tick
  
  price_data = price_data[2:nrow(price_data),]
  time_vec = price_data$time_freq
  out = freq_signal(test_param, time_vec, t, tick_spacing, max_tick_width, price_data$close,
                    y_type, converter, my_lower_tick, my_upper_tick, token0_digits, token1_digits, quote_base_token)
  my_lower_tick = out$lower_tick
  my_upper_tick = out$upper_tick
  
  x1 = tick_to_price(my_upper_tick, token0_digits, token1_digits, quote_base_token)
  x2 = tick_to_price(my_lower_tick, token0_digits, token1_digits, quote_base_token)
  
  if (x1 > x2){
    upper_price = x1
    lower_price = x2
  } else {
    upper_price = x2
    lower_price = x1
  }
  bound = list(my_lower_tick, my_upper_tick, lower_price, upper_price)
  names(bound) = c("lower_tick", "upper_tick", "lower_price", "upper_price")
  bound    
}



back_test <-function(pool, pnl_base_token_option, token0_digits, token1_digits, trading_signal_table, init_money_0){
  
  # pnl_base_token_option should be consistent with quote price.
  # LP and IL assume that p =  asset_token_amount / base_token_amount
  # If quote_price = token0_amount/token1_amount and pnl_token is token0, there is no need to invert the quote_price.
  # If quote_price = token1_amount/token0_amount and pnl_token is token0, then the quote_price should be inverted.
  # If quote_price = token0_amount/token1_amount and pnl_token is token1, then the quote_price should be inverted.
  # If quote_price = token1_amount/token0_amount and pnl_token is token1, there is no need to invert the quote_price.
  signal_df = copy(trading_signal_table)
  trade_len = nrow(signal_df)
  enter_p = rep(0, trade_len)
  bound_changes = rep(FALSE, trade_len)
  invest_amount0 = rep(0, trade_len)
  vault = rep(0, trade_len)
  fee = rep(0, trade_len)
  IL = rep(0, trade_len)
  amount0_LP = rep(0, trade_len)
  amount1_LP = rep(0, trade_len)
  fee = rep(0, trade_len)
  earn_0 = rep(0, trade_len)
  earn_1 = rep(0, trade_len)
  equity = rep(0, trade_len)
  enter_block = rep(0, trade_len)
  liquidity = rep(0, trade_len)
  status = rep('', trade_len)
  
  invest_amount0[1] = as.integer(init_money_0)
  vault[1] = init_money_0 - as.integer(init_money_0)
  bound_changes[1] = TRUE
  status[1] = 'add'
  enter_p[1] = signal_df$close[1]
  enter_block[1] = signal_df$block_number[1]
  
  if (pnl_base_token_option == 'token0'){
    # p = token0_amount/token1_amount
    amount0_LP[1] = init_base_token_LP(enter_p[1], signal_df$lower_price[1], signal_df$upper_price[1], invest_amount0[1])
    amount1_LP[1] = init_asset_token_Lp(enter_p[1], signal_df$lower_price[1], signal_df$upper_price[1], invest_amount0[1])
    
  } else if (pnl_base_token_option == 'token1'){
    # p = token1_amount/token0_amount
    amount0_LP[1] = init_asset_token_Lp(enter_p[1], signal_df$lower_price[1], signal_df$upper_price[1], invest_amount0[1])
    amount1_LP[1] = init_base_token_LP(enter_p[1], signal_df$lower_price[1], signal_df$upper_price[1], invest_amount0[1])
    
  }
  IL[1] =  cal_gen_IL(enter_p[1],signal_df$close[1], signal_df$lower_price[1], signal_df$upper_price[1], invest_amount0[1], 'value')
  
  if (round(amount0_LP[1]*10^token0_digits) > 0){
    position = get_position_info(pool, signal_df$block_number[1], amount0_LP[1], signal_df$lower_tick[1], signal_df$upper_tick[1], token0_digits, "amount0")
  } else if (round(amount1_LP[1]*10^token1_digits) > 0){ 
    position = get_position_info(pool,signal_df$block_number[1], amount1_LP[1], signal_df$lower_tick[1], signal_df$upper_tick[1], token1_digits, "amount1")
  }
  liquidity[1] = position$data$liquidity
  fee_obj = get_fee_estimation(pool,signal_df$lower_tick[1],signal_df$upper_tick[1],
                               liquidity[1],
                               enter_block[1], signal_df$block_number[1])
  
  earn_0[1] = fee_obj$data$earned0 
  earn_1[1] = fee_obj$data$earned1
  
  if (pnl_base_token_option == 'token0'){
    # p = token0_amount/token1_amount
    fee[1] = fee_obj$data$earned0 + fee_obj$data$earned1*signal_df$close[1]
    equity[1] = amount0_LP[1] + amount1_LP[1]*signal_df$close[1] + fee[1] + vault[1]
    
    
  } else if (pnl_base_token_option == 'token1'){
    # p = token1_amount/token0_amount
    fee[1] = fee_obj$data$earned0*signal_df$close[1] + fee_obj$data$earned1
    equity[1] =  amount0_LP[1]*signal_df$close[1] + amount1_LP[1] + fee[1] + vault[1]
  }
  
  remove_lp_df = data.table()
  
  for (i in c(2:trade_len)){
    
    if (signal_df$lower_tick[i]!=signal_df$lower_tick[i-1] || signal_df$upper_tick[i]!=signal_df$upper_tick[i-1]) {
      
      temp_df = signal_df[signal_df$timestamp_unix==signal_df$timestamp_unix[i],]
      
      temp_lp = get_amount_LP(enter_p[i-1], signal_df$close[i], signal_df$lower_price[i-1], signal_df$upper_price[i-1], invest_amount0[i-1], pnl_base_token_option)
      
      
      temp_fee_obj = get_fee_estimation(pool,signal_df$lower_tick[i-1],signal_df$upper_tick[i-1],
                                        liquidity[i-1],
                                        enter_block[i-1], signal_df$block_number[i])
      
      if (pnl_base_token_option == 'token0'){
        # p = token0_amount/token1_amount
        temp_fee = temp_fee_obj$data$earned0 + temp_fee_obj$data$earned1*signal_df$close[i]
        liquidation = temp_lp$amount0 + temp_lp$amount1*signal_df$close[i] + temp_fee + vault[i-1]
        
      } else if (pnl_base_token_option == 'token1'){
        # p = token1_amount/token0_amount
        temp_fee = temp_fee_obj$data$earned0*signal_df$close[i] + temp_fee_obj$data$earned1
        liquidation = temp_lp$amount0*signal_df$close[i] + temp_lp$amount1 + temp_fee + vault[i-1]
      }
      temp_IL = cal_gen_IL(enter_p[i-1],signal_df$close[i], signal_df$lower_price[i-1], signal_df$upper_price[i-1], invest_amount0[i-1], 'value')
      
      temp_df[,lower_tick:=signal_df$lower_tick[i-1]]
      temp_df[,upper_tick:=signal_df$upper_tick[i-1]]
      temp_df[,lower_price:=signal_df$lower_price[i-1]]
      temp_df[,upper_price:=signal_df$upper_price[i-1]]
      
      temp_df[, enter_price:=enter_p[i-1]]
      temp_df[, enter_block:=enter_block[i-1]]
      temp_df[, bound_changes:=bound_changes[i-1]]
      temp_df[, invest_money:=invest_amount0[i-1]]
      temp_df[, remain_vault:=vault[i-1]]
      temp_df[, amount0_LP:=temp_lp$amount0]
      temp_df[, amount1_LP:=temp_lp$amount1]
      temp_df[, liquidity:=liquidity[i-1]]
      temp_df[, IL:=temp_IL]
      temp_df[, earn0:=temp_fee_obj$data$earned0]
      temp_df[, earn1:=temp_fee_obj$data$earned1]
      temp_df[, fee:=temp_fee]
      temp_df[, equity:=liquidation]
      temp_df[, fund_status:='remove']
      remove_lp_df = rbind(remove_lp_df, temp_df)
      
      invest_amount0[i] = as.integer(liquidation)
      vault[i] = liquidation - as.integer(liquidation)
      bound_changes[i] = TRUE
      status[i] = 'add'
      enter_p[i] = signal_df$close[i]
      enter_block[i] = signal_df$block_number[i]
      
    } else {
      invest_amount0[i] = invest_amount0[i-1]
      vault[i] = vault[i-1]
      bound_changes[i] = FALSE
      status[i] = 'on'
      enter_p[i] = enter_p[i-1]
      enter_block[i] = enter_block[i-1]
    }
    
    lp_i = get_amount_LP(enter_p[i], signal_df$close[i], signal_df$lower_price[i], signal_df$upper_price[i], invest_amount0[i], pnl_base_token_option)
    amount0_LP[i] = lp_i$amount0
    amount1_LP[i] = lp_i$amount1
    
    # if (pnl_base_token_option == 'token0'){
    #   # p = token0_amount/token1_amount
    #   amount0_LP[i] = cal_gen_LP(enter_p[i], signal_df$close[i], signal_df$lower_price[i], signal_df$upper_price[i], invest_amount0[i], 'base')
    #   amount1_LP[i] = cal_gen_LP(enter_p[i], signal_df$close[i], signal_df$lower_price[i], signal_df$upper_price[i], invest_amount0[i], 'asset')
    # } else if (pnl_base_token_option == 'token1'){
    #   # p = token1_amount/token0_amount
    #   amount0_LP[i] = cal_gen_LP(enter_p[i], signal_df$close[i], signal_df$lower_price[i], signal_df$upper_price[i], invest_amount0[i], 'asset')
    #   amount1_LP[i] = cal_gen_LP(enter_p[i], signal_df$close[i], signal_df$lower_price[i], signal_df$upper_price[i], invest_amount0[i], 'base')
    # }
    IL[i] = cal_gen_IL(enter_p[i],signal_df$close[i], signal_df$lower_price[i], signal_df$upper_price[i], invest_amount0[i], 'value')
    
    # fix position error
    if (bound_changes[i] == TRUE){
      if (round(amount0_LP[i]*10^token0_digits) > 0){ 
        position = get_position_info(pool, enter_block[i], amount0_LP[i], signal_df$lower_tick[i], signal_df$upper_tick[i], token0_digits, "amount0")
      } else if (round(amount1_LP[i]*10^token1_digits) > 0){
        position = get_position_info(pool, enter_block[i], amount1_LP[i], signal_df$lower_tick[i], signal_df$upper_tick[i], token1_digits, "amount1")
      }
      liquidity[i] = position$data$liquidity
    } else {
      liquidity[i] = liquidity[i-1]
    }
    
    fee_obj = get_fee_estimation(pool,signal_df$lower_tick[i],signal_df$upper_tick[i],
                                 liquidity[i],
                                 enter_block[i], signal_df$block_number[i])
    
    earn_0[i] = fee_obj$data$earned0 
    earn_1[i] = fee_obj$data$earned1
    
    if (pnl_base_token_option == 'token0'){
      # p = token0_amount/token1_amount
      fee[i] = fee_obj$data$earned0 + fee_obj$data$earned1*signal_df$close[i]
      equity[i] = amount0_LP[i] + amount1_LP[i]*signal_df$close[i] + fee[i] + vault[i]
      
      
    } else if (pnl_base_token_option == 'token1'){
      # p = token1_amount/token0_amount
      fee[i] = fee_obj$data$earned0*signal_df$close[i] + fee_obj$data$earned1
      equity[i] = amount0_LP[i]*signal_df$close[i] + amount1_LP[i] + fee[i] + vault[i]
    }
    
    Sys.sleep(0.1)
    progress(i, trade_len)
  }
  
  signal_df[, enter_price:=enter_p]
  signal_df[, enter_block:=enter_block]
  signal_df[, bound_changes:=bound_changes]
  signal_df[, invest_money:=invest_amount0]
  signal_df[, remain_vault:=vault]
  signal_df[, amount0_LP:=amount0_LP]
  signal_df[, amount1_LP:=amount1_LP]
  signal_df[, liquidity:=liquidity]
  signal_df[, IL:=IL]
  signal_df[, earn0:=earn_0]
  signal_df[, earn1:=earn_1]
  signal_df[, fee:=fee]
  signal_df[, equity:=equity]
  signal_df[, fund_status:=status]
  
  final_df = rbind(signal_df, remove_lp_df)
  setorder(final_df, 'timestamp_unix',-'fund_status')
  final_df[nrow(final_df), fund_status:='remove']
  return(final_df)
}

adj_fee_outlier <- function(pool, outlier_df, pnl_base_token_option){
  
  data_len = nrow(outlier_df)
  
  fee = rep(0, data_len)
  earn_0 = rep(0, data_len)
  earn_1 = rep(0, data_len)
  equity = rep(0, data_len)
  
  for (i in 1:data_len){
    
    fee_obj = get_fee_estimation(pool,outlier_df$lower_tick[i],outlier_df$upper_tick[i],
                                 outlier_df$liquidity[i],
                                 outlier_df$enter_block[i], outlier_df$block_number[i])
    
    earn_0[i] = fee_obj$data$earned0 
    earn_1[i] = fee_obj$data$earned1
    #print(c(i,outlier_df$earn_0[i], outlier_df$earn_1[i]))
    if (pnl_base_token_option == 'token0'){
      # p = token0_amount/token1_amount
      fee[i] = fee_obj$data$earned0 + fee_obj$data$earned1*outlier_df$close[i]
      equity[i] = outlier_df$amount0_LP[i] + outlier_df$amount1_LP[i]*outlier_df$close[i] + fee[i] + outlier_df$remain_vault[i]
      
      
    } else if (pnl_base_token_option == 'token1'){
      # p = token1_amount/token0_amount
      fee[i] = fee_obj$data$earned0*outlier_df$close[i] + fee_obj$data$earned1
      equity[i] = outlier_df$amount0_LP[i]*outlier_df$close[i] + outlier_df$amount1_LP[i] + fee[i] + outlier_df$remain_vault[i]
    }
    progress(i, data_len)
  }
  out = list(fee, earn_0, earn_1, equity)
  names(out) = c("fee", "earn0", "earn1", "equity")
  out
}

adj_simulation_outlier <- function(pool, simulation_df, pnl_base_token_option){
  
  
  simulation_df[,is_outlier_fee:=ifelse(fee>outlier_bound(simulation_df$fee)[2], TRUE, FALSE)]
  
  outlier_df = simulation_df[is_outlier_fee==TRUE]
  
  data_len = nrow(outlier_df)
  
  if (data_len < 1){
    
    return(simulation_df)
    
  }
  
  fee = rep(0, data_len)
  
  equity = rep(0, data_len)
  
  for (i in 1:data_len){
    
    fee_obj = get_fee_estimation(pool,outlier_df$lower_tick[i],outlier_df$upper_tick[i],
                                 outlier_df$liquidity[i],
                                 outlier_df$enter_block[i], outlier_df$block_number[i])
    
    
    if (pnl_base_token_option == 'token0'){
      # p = token0_amount/token1_amount
      fee[i] = fee_obj$data$earned0 + fee_obj$data$earned1*outlier_df$close[i]
      equity[i] = outlier_df$amount0_LP[i] + outlier_df$amount1_LP[i]*outlier_df$close[i] + fee[i] + outlier_df$remain_vault[i]
      
      
    } else if (pnl_base_token_option == 'token1'){
      # p = token1_amount/token0_amount
      fee[i] = fee_obj$data$earned0*outlier_df$close[i] + fee_obj$data$earned1
      equity[i] = outlier_df$amount0_LP[i]*outlier_df$close[i] + outlier_df$amount1_LP[i] + fee[i] + outlier_df$remain_vault[i]
    }
    
  }
  no_outlier_result = list(fee, equity)
  names(no_outlier_result) = c("fee", "equity")
  
  outlier_df[, fee:=no_outlier_result$fee] 
  outlier_df[, equity:=no_outlier_result$equity] 
  df = rbind(simulation_df[is_outlier_fee==FALSE], outlier_df)
  setorder(df, "timestamp_unix")
  return(df)
}


init_base_token_LP <- function(P_0, P_lower, P_upper, base_token_amount){
  # p = asset_token_amount / base_token_amount
  P_0_ = P_0
  if (P_0 > P_upper){
    P_0_ = P_upper
  } else if (P_0 < P_lower) {
    P_0_ = P_lower
  } 
  base_token_ratio = (P_0_ ** (1 / 2) - P_lower ** (1 / 2)) / (P_0_ * (P_upper ** (1 / 2) - P_0_ ** (1 / 2)) / (P_0_ ** (1 / 2) * P_upper ** (1 / 2)) + (P_0_ ** (1 / 2) - P_lower ** (1 / 2)))
  base_token_amount * base_token_ratio
}

init_asset_token_Lp <- function(P_0, P_lower, P_upper, base_token_amount){
  # p = asset_token_amount / base_token_amount
  P_0_ = P_0
  if (P_0 > P_upper){
    P_0_ = P_upper
  } else if (P_0 < P_lower) {
    P_0_ = P_lower
  }
  
  asset_token_ratio = (P_0_ * (P_upper ** (1 / 2) - P_0_ ** (1 / 2)) / (P_0_ ** (1 / 2) * P_upper ** (1 / 2))) / (P_0_ * (P_upper ** (1 / 2) - P_0_ ** (1 / 2)) / (P_0_ ** (1 / 2) * P_upper ** (1 / 2)) + (P_0_ ** (1 / 2) - P_lower ** (1 / 2)))
  asset_token_amount_in_token0 = base_token_amount * asset_token_ratio
  asset_token_amount_in_token0 / P_0 #  asset_token_amount = asset_token_amount_in_token0 / P_0
}

cal_gen_LP <- function(P_0, P_1, P_lower, P_upper, base_token_amount, token) {
  # p = asset_token_amount / base_token_amount
  init_base_lp = init_base_token_LP(P_0, P_lower, P_upper, base_token_amount)
  init_asset_lp = init_asset_token_Lp(P_0, P_lower, P_upper, base_token_amount)
  
  if (P_0 < P_lower){
    L = init_asset_lp / (1/P_lower**(1/2)-1/P_upper**(1/2))
  } else if (P_0 > P_upper) {
    L = init_base_lp / (P_upper**(1/2)-P_lower**(1/2))
  }
  else {
    L = init_base_lp / (P_0**(1/2)-P_lower**(1/2))
  }
  
  base_virtual_amount = L * P_lower**(1/2)
  asset_virtual_amount = L / P_upper**(1/2)
  
  if ((P_lower <= P_1) & (P_1 <= P_upper)) {
    
    asset_remain_amount = L/P_1**(1/2) -  asset_virtual_amount
    base_remain_amount = L*P_1**(1/2) - base_virtual_amount
    
  } else if (P_1 < P_lower) {
    asset_remain_amount = L/P_lower**(1/2) -  asset_virtual_amount
    base_remain_amount = L*P_lower**(1/2) - base_virtual_amount
    
  } else if (P_1 > P_upper) {
    asset_remain_amount = L/P_upper**(1/2) - asset_virtual_amount
    base_remain_amount = L*P_upper**(1/2) - base_virtual_amount
  }
  
  if (token=='base'){
    return(base_remain_amount)
  } else {
    return(asset_remain_amount)
  }
  
}

cal_gen_IL <- function(P_0, P_1, P_lower, P_upper, base_token_amount, output_type) {
  
  # p = asset_token_amount / base_token_amount
  init_base_lp = init_base_token_LP(P_0, P_lower, P_upper, base_token_amount)
  init_asset_lp = init_asset_token_Lp(P_0, P_lower, P_upper, base_token_amount)
  holder_value = init_base_lp + init_asset_lp * P_1
  
  base_remain_amount = cal_gen_LP(P_0, P_1, P_lower, P_upper, base_token_amount, 'base')
  asset_remain_amount = cal_gen_LP(P_0, P_1, P_lower, P_upper, base_token_amount, 'asset')
  
  lp_value = base_remain_amount + asset_remain_amount * P_1
  
  if (output_type == "value"){
    
    round(holder_value - lp_value,6)
    
  } else if (output_type == "percentage") {
    
    round(100*(holder_value - lp_value) / holder_value,4)
  }
  
}

get_amount_LP <- function(enter_p, close_p, lower_p, upper_p, money_invest, pnl_base_token_option) {
  
  if (pnl_base_token_option == 'token0'){
    # p = token0_amount/token1_amount
    amount0_LP = cal_gen_LP(enter_p, close_p, lower_p, upper_p, money_invest, 'base')
    amount1_LP = cal_gen_LP(enter_p, close_p, lower_p, upper_p, money_invest, 'asset')
  } else if (pnl_base_token_option == 'token1'){
    # p = token1_amount/token0_amount
    amount0_LP = cal_gen_LP(enter_p, close_p, lower_p, upper_p, money_invest, 'asset')
    amount1_LP = cal_gen_LP(enter_p, close_p, lower_p, upper_p, money_invest, 'base')
  }
  lp = list(amount0_LP, amount1_LP)
  names(lp) = c('amount0','amount1')
  return(lp)
}


outlier_bound <- function(vec){
  
  mu = mean(vec)
  sig = sqrt(var(vec))
  x = (vec - mu)/sig
  
  q1 = quantile(x,0.25)
  q3 = quantile(x,0.75)
  iqr = q3 - q1
  lower_bound = (q1-1.5*iqr)*sig + mu
  upper_bound = (q3+1.5*iqr)*sig + mu
  c(lower_bound, upper_bound)
}
























#
# position = get_position_info('0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8',
#                             13717810,
#                             100000,
#                             189300,
#                             193980,6,'amount0')
# 
# fee = get_fee_estimation('0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8',189300,193980,
#                          position$data$liquidity,13717810,13717948)

# cal_IL(4641, 4641, 4700, 4800, 100000,'value')
# cal_IL(4641, 4581, 4700, 4800, 100000,'value')
# cal_IL(4641, 4686, 4700, 4800, 100000,'value')
# cal_IL(4641, 4755, 4700, 4800, 100000,'value')
# cal_IL(4641, 4692, 4700, 4800, 100000,'value')
# fee$data$earned0
# cal_gen_IL(4641, 4641, 4700, 4800, 100000,'value')
# cal_gen_IL(4641, 4581, 4700, 4800, 100000,'value')
# cal_gen_IL(4641, 4686, 4700, 4800, 100000,'value')
# cal_gen_IL(4641, 4755, 4700, 4800, 100000,'value')
# cal_gen_IL(4641, 4692, 4700, 4800, 100000,'value')
