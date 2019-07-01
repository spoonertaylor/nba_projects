# * PURPOSE Scrape Bbref for the heigh and weight measurements
`%>%` = dplyr::`%>%`
# * Functions ----

#' bbref_measurements_one_player
#' @name bbref_measurements_one_player
#' @title Scrape basketball-reference.com player height and weight
#' @description Input is a bbref player id. Output is a data frame with the scraped 
#'                bbref player measurements
#' 
#' @param bbref_id Basketball Reference player ID
#' @return Data frame. weight is in inches, weight in pounds
#' Columns: 
#'  bbref_id, height, weight
#' 
#'        
#' @examples 
#' # Scrape for Giannis Antetokounmpo
#' bbref_measurements_one_player('antetgi01')
bbref_measurements_one_player = function(bbref_id) {
  # Create url
  url = paste0("https://www.basketball-reference.com/players/", substring(bbref_id, 1, 1), "/", bbref_id ,".html")
  # Read in page
  page = tryCatch({
    xml2::read_html(url)
  },
  error = function(e) {
    stop(paste0('Unable to read bbref page for ', bbref_id))
    NULL
  }
  )
  
  p = page %>% rvest::html_nodes('p')
  
  measurements = suppressWarnings(p[stringr::str_detect(p, '\\([0-9]{3}cm,')] %>% rvest::html_text())
  height = as.numeric(stringr::str_extract(measurements, "\\([0-9]+cm") %>% stringr::str_remove_all("\\(|cm")) * 25 / 64
  weight = as.numeric(stringr::str_extract(measurements, "[0-9]{3}lb") %>% stringr::str_remove("lb"))
  
  return(data.frame(
    bbref_id = bbref_id,
    height = height,
    weight = weight
  ))
}

#' bbref_measurements
#' @name bbref_measurements
#' @title Scrape basketball-reference.com player height and weight
#' @description Input is any number of bbref player id's. Output is a data frame with the scraped 
#'                bbref player measurements one row per player
#' 
#' @param bbref_id List of Basketball Reference player ID
#' @param parallel Boolean, TRUE run function in parallel using all but one cluster on your machine
#' @return Data frame one row per player. weight is in inches, weight in pounds
#' Columns: 
#'  bbref_id, height, weight
#' 
bbref_measurements = function(bbref_ids, parallel = TRUE) {
  `%dopar%` = foreach::`%dopar%`
  # Set up parallel running
  if (parallel) {
    cores = parallel::detectCores()
    cl = parallel::makeCluster(cores[1] - 1)
    doParallel::registerDoParallel(cl)
  }
  # Run over each player
  player_df = foreach::foreach(bbref_id = bbref_ids, .combine=rbind, .export = 'bbref_measurements_one_player') %dopar% {
    `%>%` = dplyr::`%>%`
    bbref_measurements_one_player(bbref_id)
  }
  # Stop parralel
  if (parallel) {
    parallel::stopCluster(cl)
  }
  
  return(player_df) 
}

# bbref_players = read.csv('~/Documents/nba_projects/data/player_ids/player_table.csv', stringsAsFactors = FALSE)
# 
# measurement_df = bbref_measurements(bbref_players$bbref_id)
# 
# write.csv(measurement_df, '~/Documents/nba_projects/data/nba/basketball_reference/player_data/measurements/player_measurements.csv',
#           row.names = FALSE)