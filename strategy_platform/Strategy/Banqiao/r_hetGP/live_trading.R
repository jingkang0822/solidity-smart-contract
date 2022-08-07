
packages <- c("httr", "basicPlotteR","data.table", "lubridate", "jsonlite","hetGP", "laGP", "lhs")

# Install packages not yet installed
installed_packages <- packages %in% rownames(installed.packages())
if (any(installed_packages == FALSE)) {
  install.packages(packages[!installed_packages], dependencies = TRUE)
}

# Packages loading
invisible(lapply(packages, library, character.only = TRUE))


set_working_env <- function(working_directory){
  
  setwd(working_directory)
  print(paste("cwd:", getwd()))
  
  source("r_hetGP/lib/optimization.R", chdir = TRUE)
  source("r_hetGP/lib/simulation.R", chdir = TRUE)
}


live_trading_signals <- function(
    t, df, test_param, detecion_freq,
    sampling_interval, tick_spacing, max_tick_width, 
    token0_digits, token1_digits, quote_base_token, 
    init_lower_price, init_upper_price
){

  trade_t = as.POSIXct(t)
  back_test_data = df
  
  if (init_lower_price > 0){
    init_upper_tick = price_to_tick(init_lower_price, token0_digits, token1_digits, quote_base_token)
  } else {
    init_upper_tick = NULL
  }
  if (init_upper_price > 0){
    init_lower_tick = price_to_tick(init_upper_price, token0_digits, token1_digits, quote_base_token)
  } else {
    init_lower_tick = NULL
  }
  final = get_live_trading_signals(back_test_data, test_param, trade_t, detecion_freq, sampling_interval, tick_spacing, max_tick_width,
                                   tick_to_price, 'price', token0_digits, token1_digits, quote_base_token, 
                                   init_lower_tick, init_upper_tick)
  c(final$lower_price, final$upper_price)
}

