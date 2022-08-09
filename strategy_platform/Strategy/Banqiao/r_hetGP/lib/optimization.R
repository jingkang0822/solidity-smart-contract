source("simulation.R")

simulation_analysis_table <- function(simulation_df) {
  
  end_equity = c()
  sum_fee_at_remove = c()
  sum_IL_at_remove = c()
  price_coverage = c()
  total_bound_changes = c()
  min_duraion = c()
  max_duration = c()
  avg_duration = c()
  q1_duration = c()
  middle_duration = c()
  q3_duration = c()
  
  price_coverage = c(price_coverage, nrow(simulation_df[(close>=lower_price)&(close<=upper_price),]) / nrow(simulation_df))
  end_equity = c(end_equity, simulation_df$equity[nrow(simulation_df)])
  simulation_df[,lead_changes:=shift(bound_changes,-1)]
  sum_fee_at_remove = c(sum_fee_at_remove,  sum(simulation_df[fund_status=='remove',]$fee))
  sum_IL_at_remove = c(sum_IL_at_remove, sum(simulation_df[fund_status=='remove',]$IL))
  total_bound_changes = c(total_bound_changes, sum(simulation_df$bound_changes))
  ts= as.POSIXct(simulation_df[bound_changes==1,]$timestamp_utc)
  t1 = ts[2:length(ts)]
  t0 = ts[1:(length(ts)-1)]
  duration_i = as.numeric(difftime(t1, t0, units = 'days'))
  duration_i = duration_i[2:length(duration_i)]
  min_duraion = c(min_duraion, min(duration_i))
  max_duration = c(max_duration, max(duration_i))
  avg_duration = c(avg_duration, mean(duration_i))
  q1_duration = c(q1_duration, quantile(duration_i,0.25, na.rm=TRUE))
  middle_duration = c(middle_duration, quantile(duration_i,0.5, na.rm=TRUE))
  q3_duration = c(q3_duration, quantile(duration_i,0.75, na.rm=TRUE))
  
  names(q1_duration) = NULL
  names(middle_duration) = NULL
  names(q3_duration) = NULL
  
  data.table(
    price_coverage = round(price_coverage,4),
    end_equity = end_equity,
    sum_fee_at_remove = sum_fee_at_remove,
    sum_IL_at_remove = sum_IL_at_remove,
    total_bound_changes = total_bound_changes,
    min_duraion = min_duraion,
    max_duration = max_duration,
    avg_duration = round(avg_duration,2),
    q1_duration = q1_duration,
    middle_duration = round(middle_duration,2),
    q3_duration = q3_duration
  )
}


simulation_summary <- function(os, args_list, converter){
  #arg_list, pnl_base_token, coverter, token0_digits, token1_digits, quote_base_token
  param_obj = apply(os$X, 1, parameter_maker)
  param_table = data.frame(matrix(unlist(param_obj), nrow=length(param_obj), byrow=TRUE))
  names(param_table) = names(param_obj[[1]])
  param_table['payoff'] = -os$y
  param_table['iteration'] = row.names(param_table)
  
  end_equity = c()
  sum_fee_at_remove = c()
  sum_IL_at_remove = c()
  price_coverage = c()
  total_bound_changes = c()
  min_duraion = c()
  max_duration = c()
  avg_duration = c()
  q1_duration = c()
  middle_duration = c()
  q3_duration = c()
  
  for(i in 1:length(param_obj)) {
    param_list = param_obj[[i]]
    print(param_list)
    simulation_df = strategy_simulation(args_list$pool, args_list$invest_amount, args_list$quote_base_token, args_list$pnl_base_token_option, args_list$back_test_data, 
                                        param_list, args_list$start_t, args_list$end_t, args_list$detecion_freq, args_list$sampling_interval, 
                                        args_list$max_tick_width, converter, args_list$y_type, TRUE, args_list$init_lower_tick, args_list$init_upper_tick)
    
    simulation_df = adj_simulation_outlier(args_list$pool, simulation_df,  args_list$pnl_base_token)
    
    price_coverage = c(price_coverage, nrow(simulation_df[(close>=lower_price)&(close<=upper_price),]) / nrow(simulation_df))
    end_equity = c(end_equity, simulation_df$equity[nrow(simulation_df)])
    simulation_df[,lead_changes:=shift(bound_changes,-1)]
    sum_fee_at_remove = c(sum_fee_at_remove,  sum(simulation_df[fund_status=='remove',]$fee))
    sum_IL_at_remove = c(sum_IL_at_remove, sum(simulation_df[fund_status=='remove',]$IL))
    total_bound_changes = c(total_bound_changes, sum(simulation_df$bound_changes))
    ts= as.POSIXct(simulation_df[bound_changes==1,]$timestamp_utc)
    t1 = ts[2:length(ts)]
    t0 = ts[1:(length(ts)-1)]
    duration_i = as.numeric(difftime(t1, t0, units = 'days'))
    duration_i = duration_i[2:length(duration_i)]
    min_duraion = c(min_duraion, min(duration_i))
    max_duration = c(max_duration, max(duration_i))
    avg_duration = c(avg_duration, mean(duration_i))
    q1_duration = c(q1_duration, quantile(duration_i,0.25, na.rm=TRUE))
    middle_duration = c(middle_duration, quantile(duration_i,0.5, na.rm=TRUE))
    q3_duration = c(q3_duration, quantile(duration_i,0.75, na.rm=TRUE))
    
  }
  
  names(q1_duration) = NULL
  names(middle_duration) = NULL
  names(q3_duration) = NULL
  param_table['price_coverage'] = round(price_coverage,4)
  param_table['end_equity'] = end_equity
  param_table['sum_fee_at_remove'] = sum_fee_at_remove
  param_table['sum_IL_at_remove'] = sum_IL_at_remove
  param_table['total_bound_changes'] = total_bound_changes
  param_table['min_duraion'] = min_duraion
  param_table['max_duration'] = max_duration
  param_table['avg_duration'] = round(avg_duration,2)
  param_table['q1_duration'] = q1_duration
  param_table['middle_duration'] =  round(middle_duration,2)
  param_table['q3_duration'] = q3_duration
  
  return(param_table)
}


final_pnl <- function(simulation_df){
  
  -(simulation_df$equity[nrow(simulation_df)])
}

sum_fee_IL <- function(simulation_df){
  
  cal_df = simulation_df[simulation_df$fund_status=='remove', c('fee','IL')]
  out = sum(cal_df$fee) - sum(cal_df$IL)
  -out
}

avg_path_fee_IL <- function(simulation_df){
  
  -(mean(simulation_df$fee - simulation_df$IL))
}

EI <- function(gpi, x, fmin, pred=predGPsep){

  if(is.null(nrow(x))) x <- matrix(x, nrow=1)
  p <- pred(gpi, x, lite=TRUE)
  d <- fmin - p$mean
  sigma <- sqrt(p$s2)
  dn <- d/sigma
  ei <- d*pnorm(dn) + sigma*dnorm(dn)
  return(ei)

}


obj_EI <- function(x, fmin, gpi, pred=predGPsep){

  - EI(gpi, x, fmin, pred)
}


EI_search <- function(X, y, gpi, pred=predGPsep, multi.start=5, tol=sqrt(.Machine$double.eps)){

  m <- which.min(y)
  fmin <- y[m]
  start <- matrix(X[m,], nrow=1)
  if(multi.start > 1)
    start <- rbind(start, randomLHS(multi.start - 1, ncol(X)))
  xnew <- matrix(NA, nrow=nrow(start), ncol=ncol(X)+1)
  for(i in 1:nrow(start)) {
    if(EI(gpi, start[i,], fmin) <= tol) { out <- list(value=-Inf); next }
    out <- optim(start[i,], obj_EI, method="L-BFGS-B",
                 lower=0, upper=1, gpi=gpi, pred=pred, fmin=fmin)
    xnew[i,] <- c(out$par, -out$value)
  }
  solns <- data.frame(cbind(start, xnew))
  names(solns) <- c("s1", "s2", "s3", "s4", "x1", "x2", "x3", "x4", "val")
  solns <- solns[solns$val > tol,]
  return(solns)
}


optim_EI <- function(args_list, converter, ninit, end, reward_function){
  
  target_func <- function(param){
    
    param_list = parameter_maker(param)
    simulation_df = strategy_simulation(args_list$pool, args_list$invest_amount, args_list$quote_base_token, args_list$pnl_base_token_option, args_list$back_test_data, 
                                        param_list, args_list$start_t, args_list$end_t, args_list$detecion_freq, args_list$sampling_interval, 
                                        args_list$max_tick_width, converter, args_list$y_type, TRUE, args_list$init_lower_tick, args_list$init_upper_tick)
    
    simulation_df = adj_simulation_outlier(args_list$pool, simulation_df,  args_list$pnl_base_token)
    reward_function(simulation_df)
    out = list(reward_function(simulation_df), simulation_analysis_table(simulation_df))
  }
  
  get_y <- function(out){
    
    len = length(out)
    if (len == 2){
      
      return(out[[1]])
      
    } else {
      
      y = c()
      for (i in 1:length(out)){
        temp = unlist(out[[i]][1])
        y = c(y, temp)
      }
      return(y)
    }
  }
  
  get_tb <- function(out){
    
    len = length(out)
    if (len == 2){
      
      return(out[[2]])
      
    } else {
      
      tb = data.table()
      for (i in 1:length(out)){
        temp = out[[i]][2]
        tb = rbind(tb, temp[[1]])
      }
      return(tb)
    }
  }
  
  set.seed(1789)
  X = randomLHS(ninit, 4)
  outcome = apply(X,1,target_func)
  y = get_y(outcome)
  tb = get_tb(outcome)
  gpi <- newGPsep(X, y, d=0.1, g=1e-6, dK=TRUE)
  da <- darg(list(mle=TRUE, max=0.5), randomLHS(100, 4))
  mleGPsep(gpi, param="d", tmin=da$min, tmax=da$max, ab=da$ab)
  
  ## optimization loop of sequential acquisitions
  maxei <- c()
  for(i in (ninit+1):end) {
    print(i)
    solns <- EI_search(X, y, gpi)
    m <- which.max(solns$val)
    maxei <- c(maxei, solns$val[m])
    xnew <- as.matrix(solns[m,5:8])
    print(xnew)
    new_out <- target_func(xnew)
    ynew = get_y(new_out)
    print(ynew)
    updateGPsep(gpi, xnew, ynew)
    mleGPsep(gpi, param="d", tmin=da$min, tmax=da$max, ab=da$ab)
    X <- rbind(X, xnew)
    y <- c(y, ynew)
    tb <- rbind(tb, get_tb(new_out))
    Sys.sleep(2)
  }
  param_obj = apply(X, 1, parameter_maker)
  param_table = data.frame(matrix(unlist(param_obj), nrow=length(param_obj), byrow=TRUE))
  names(param_table) = names(param_obj[[1]])
  param_table['payoff'] = -y
  param_table['iteration'] = row.names(param_table)
  param_table = cbind(param_table, tb)
  ## clean up and return
  deleteGPsep(gpi)
  return(list(X=X, y=y, tables=param_table, maxei=maxei))
  
}


bov <- function(r, end=length(r))
{
  prog <- rep(min(r), end)
  prog[1:min(end, length(r))] <- r[1:min(end, length(r))]
  for(i in 2:end) 
    if(is.na(prog[i]) || prog[i] > prog[i-1]) prog[i] <- prog[i-1]
  return(prog)
}