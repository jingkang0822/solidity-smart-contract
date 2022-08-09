


price_to_tick <- function(price, token0_digits, token1_digits, base_token='token0'){
  # uniswap v3 price: p = token1 / token0
  # 1 token0 = p token1
  # eg.1 token0 can be exchanged to 5 token1
  # p = 1.0001^i*10^d, d = token0_digits - token1_digits
  # log_1.0001(p) = i+d*log_1.0001(10)
  # i = log_1.0001(p) - d*log_1.0001(10)
  if (base_token == 'token0'){
    p = price
  } else if (base_token == 'token1'){
    p = 1 / price
  }
  log_p = log(p, 1.0001)
  d = token0_digits - token1_digits
  log_p - d * log(10, 1.0001)
}

adj_upper_lower <- function(p_now, p_lower, p_upper, tick_spacing, token0_digits, token1_digits, base_token){
  
   lower_bound = p_lower
   upper_bound = p_upper
  
  if (p_now <= p_lower){
    
    lower_tick = price_to_tick(p_now, token0_digits, token1_digits, base_token) - tick_spacing
    lower_bound = tick_to_price(lower_tick, token0_digits, token1_digits, base_token)
    
  } else if (p_now >= p_upper){
    
    upper_tick =  price_to_tick(p_now, token0_digits, token1_digits, base_token) + tick_spacing
    upper_bound = tick_to_price(upper_tick, token0_digits, token1_digits, base_token)
  }
  
  return(c(lower_bound, upper_bound))
}

tick_to_price <- function(tick, token0_digits, token1_digits, base_token='token0'){
  # uniswap v3 price: p = token1 / token0
  # 1 token0 = p token1
  # eg.1 token0 can be exchanged to 5 token1
  # p = 1.0001^i*10^d, d = token0_digits - token1_digits
  d = token0_digits - token1_digits
  
  if (base_token == 'token0'){
    1.0001^tick*10^d
  } else if (base_token == 'token1'){
    1 / (1.0001^tick*10^d)
  }
}

fit_hetgp <- function(feature_mat, lable_vec){
  
  hetgp_fit <- mleHetGP(X = feature_mat, Z = lable_vec, covtype = "Matern5_2", 
                        lower=0.1, upper=2.5,
                        settings = list(checkHom = FALSE, linkThetas = "none", trace=-1),
                        noiseControl = list(lowerTheta_g=10,upperTheta_g=1000))
  
  return(drop(hetgp_fit))
  
}

predict_distribuion <- function(hetgp_fit, feature_mat){
  
  # prediction at the new day (1+1/n) given the fitted GP
  # Output from predict.homGP separates variance in terms of epistemic/mean (p$sd2) and residual (p$nugs) estimates
  # https://bookdown.org/rbg/surrogates/chap10.html
  
  y_pred = predict(hetgp_fit, feature_mat)
  
  # prediction mean and standard deviation
  pred = list(drop(y_pred$mean), drop(sqrt(y_pred$sd2+y_pred$nugs)))
  
  names(pred) = c('mean', 'std')
  
  return(pred)
}

get_tick_bound <- function(raw_tick, tick_spacing, q_set, max_bound_width, pred_obj, converter, token0_digits, token1_digits, base_token){
  
  ##### step 3: contruct the bound ##### 
  mean_tick <- round(raw_tick / tick_spacing) * tick_spacing 
  upper_tick <- ceiling(raw_tick / tick_spacing) * tick_spacing 
  lower_tick <- floor(raw_tick / tick_spacing) * tick_spacing 
  
  if(upper_tick == mean_tick) {
    upper_tick = mean_tick + tick_spacing
  } else if (lower_tick == mean_tick){
    lower_tick = mean_tick - tick_spacing
  }
  
  pred_mean = pred_obj$mean
  pred_std = pred_obj$std
  
  while(1){
    
    x1 = converter(lower_tick, token0_digits, token1_digits, base_token)
    x2 = converter(upper_tick, token0_digits, token1_digits, base_token)
    
    cumprob = cumprob_diff(x1, x2, pred_mean, pred_std)
  
    if (cumprob < q_set){
   
      lower_tick = lower_tick - tick_spacing
      upper_tick = upper_tick + tick_spacing
      
    } else {
      
      break
    }
    
    
  }

  tick_bound = list(mean_tick, upper_tick, lower_tick)
  names(tick_bound) = c("mean_tick", "upper_tick", "lower_tick")
  return(tick_bound)
  
}

cumprob_diff <- function(x1, x2, mu, sigma){
  
  if (x2 > x1){
    pnorm(x2, mu, sigma) - pnorm(x1, mu, sigma)
  } else {
    pnorm(x1, mu, sigma) - pnorm(x2, mu, sigma)
  }
}





# 1.0001^(195687)*10^(6-18)
# 1/ 0.0003148861
# 3175.751
# eth_to_tick(3175.751)
# price_to_tick(1/3175.751, 6, 18)
# 1 / tick_to_price(195687, 6, 18)
# 
# 6386.6
# 
# 6425.1
# 
# price_to_tick(1/6386.6, 6, 18)
# price_to_tick(1/6348.4, 6, 18)
