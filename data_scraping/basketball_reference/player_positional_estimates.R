`%>%` = dplyr::`%>%`
players = data.frame(
  player_name = c("LaMarcus Alridge", 
                  "Giannis Antetokounmpo"),
  bbref_id = c("aldrila01","antetgi01"),
  bbref_url = c("a/aldrila01","a/antetgi01")
)

# * Functions ----

#' bbref_positional_estimates_one_player
#' @name bbref_positional_estimates_one_player
#' @title Scrape basketball-reference.com player play by play table for positional estimates
#' @description Input is a bbref player id. Output is a data frame with the scraped 
#'                bbref play by play table including the proportion of minutes at each position
#'                and an estimated number of minutes at each position
#' 
#' @param bbref_id Basketball Reference player ID
#' @return Data frame with one row per season | team split
#' Columns: 
#'  bbref_id, season, age, experience, team, league,
#'  position, games_played, minutes_played, on_court_plus_minus, off_court_plus_minus,
#'   prop_pg, prop_sg, prop_sf, prop_pf, prop_c, 
#'   minutes_pg, minutes_sg, minutes_sf, minutes_pf, minutes_c
#' 
#' @note For players who switched teams during a season there will be a row for 
#'        each team they played on that year and a team = 'TOT' row for the combination of
#'        both teams (see Nik Stauskas example)
#'        
#' @examples 
#' # Scrape for Giannis Antetokounmpo
#' bbref_positional_estimates_one_player('antetgi01')
#' # Scrape for Nik Stauskas 
#' bbref_positional_estimates_one_player('stausni01')
bbref_positional_estimates_one_player = function(bbref_id) {
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
  # Read play by play table
  pos_table = page %>% rvest::html_nodes(xpath = '//comment()') %>% # select comments
    rvest::html_text() %>% # extract the comments
    paste(collapse = '') %>% # collapse to single string
    xml2::read_html() %>% # Reread page
    rvest::html_node('table#pbp') %>% # read in play by play table
    rvest::html_table()
  # Clean up column names
  pos_table = pos_table[-1, c(1:14)]
  colnames(pos_table) = c("season", "age", "team", "league", "position",
                          "games_played", "minutes_played", "prop_pg",
                          "prop_sg", "prop_sf", "prop_pf", "prop_c",
                          "on_court_plus_minus", "off_court_plus_minus")
  
  # Remove the career numbers and by team rows
  pos_table = pos_table %>% dplyr::filter(stringr::str_detect(season, "[0-9]{4}"))
  # Change season to have end of year number
  pos_table = pos_table %>% 
    dplyr::mutate(season_end = substring(season, nchar(season)-1, nchar(season)),
                  season_start = substring(season, 1, 1)) %>%
    dplyr::mutate(season = ifelse(season_start == 2, paste0("20", season_end), paste0("19", season_end))) %>%
    dplyr::select(-season_end, -season_start)
  # Add experience years
  pos_table = pos_table %>% dplyr::mutate(experience = dplyr::dense_rank(season))
  # Remove percentages from positional estimates and convert to props
  pos_table = pos_table %>%
    # Remove %'s and divide by 100
    dplyr::mutate_at(dplyr::vars(dplyr::contains("prop")), 
                     dplyr::funs(
                       as.numeric(stringr::str_remove(., "%")) / 100 
                     )
    ) %>%
    # NA's as 0
    dplyr::mutate_at(dplyr::vars(dplyr::contains("prop")),
                     dplyr::funs(
                       ifelse(is.na(.), 0, .)
                     ))
  # Convert column types
  pos_table = suppressMessages(readr::type_convert(pos_table))
  
  # Calculate minutes weighted at each_position
  pos_table = pos_table %>%
    dplyr::mutate_at(dplyr::vars(dplyr::contains("prop")),
                     dplyr::funs(
                       minutes = minutes_played*.
                     )          
    ) %>%
    dplyr::rename_at(dplyr::vars(dplyr::ends_with("_minutes")),
                     dplyr::funs(
                       paste0("minutes_", stringr::str_remove(stringr::str_remove(., "_minutes"), "prop_"))
                     )           
    )
  
  # Add the bbref player id and reorder columns
  pos_table = pos_table %>% dplyr::mutate(bbref_id = bbref_id) %>%
    dplyr::select(bbref_id, season, age, experience, team, league, position, games_played, minutes_played,
                  on_court_plus_minus, off_court_plus_minus, dplyr::everything())
  
  
  return(pos_table)
}

bbref_positional_estimates = function(bbref_ids, parallel = TRUE) {
  `%dopar%` = foreach::`%dopar%`
  # Set up parallel running
  if (parallel) {
    cores = parallel::detectCores()
    cl = parallel::makeCluster(cores[1] - 1)
    doParallel::registerDoParallel(cl)
  }
  # Run over each player
  player_df = foreach::foreach(bbref_id = bbref_ids, .combine=rbind, .export = 'bbref_positional_estimates_one_player') %dopar% {
    `%>%` = dplyr::`%>%`
    bbref_positional_estimates_one_player(bbref_id)
  }
  # Stop parralel
  if (parallel) {
    parallel::stopCluster(cl)
  }
  
  return(player_df) 
}

positions_df = bbref_positional_estimates(bbref_players$bbref_id)

write.csv(positions_df, 'data/bbref_player_data/player_position_estimates.csv',
          row.names = FALSE)