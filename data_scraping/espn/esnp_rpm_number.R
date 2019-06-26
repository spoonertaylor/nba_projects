# PURPOSE: Scrape ESPN Numbers 
`%>%` = dplyr::`%>%`
# * Function ----
#' @name get_rpm_numbers
#' @title Scrape ESPN RPM numbers
#' @description Takes in a NBA season and a page number and scrapes the ESPN numbers
#' 
#' @param year NBA season, for example 2018-19 season is 2019
#' @param page_number
#' @return Data frame with a RPM per player - team combination
#' Columns: "rank", "name", "team", "gp", "mpg", "orpm", "drpm", "rpm", "wins", "season"
get_rpm_numbers = function(year, page_number) {
  # Create url
  url = paste0('http://www.espn.com/nba/statistics/rpm/_/year/', year, '/page/', page_number)
  # Read in page
  page = tryCatch({
    xml2::read_html(url)
  },
  error = function(e) {
    warning(paste0('Unable to read for ', year, ' page ', page_number))
    NULL
  }
  )
  # If there aren't any games, return an empty data frame
  if (!is.null(page)) {
    body = tryCatch({
      rvest::html_node(page, 'body')
    },
    error = function(e) {
      warning(paste0('Unable to read for ', month, ' ', year))
      return(data.frame())
    }
    )    
  }
  else {
    return(data.frame())
  }
  # Extract table 
  table = rvest::html_nodes(body, xpath = '//*[@id="my-players-table"]/div/div[2]/table') %>%
    rvest::html_table()
  
  table = table[[1]]
  
  cols = c("rank", "player_name", "team", "gp", "mpg", "orpm", "drpm", "rpm", "wins")
  
  colnames(table) = cols
  table = table[-1,]
  # In case there was a player that played in multiple teams
  table = table %>% tidyr::separate(name, into = c("name", "pos"), sep = ', ') %>%
    tidyr::separate_rows(team, sep = '/')
  
  table = table %>% dplyr::mutate(season = year)
  return(table)
}

# * Get data for seasons 2014-2019 ----
rpm = data.frame()
for (year in 2014:2019) {
  # Last Updated: April 21, 2019
  rpm_pages = lapply(1:20, function(page) get_rpm_numbers(year, page))
  
  rpm_temp = dplyr::bind_rows(rpm_pages)  
  rpm = rbind(rpm, rpm_temp)
}

# * Join ESPN ID's ----
espn_player_ids = read.csv("~/Documents/nba_positional_scarcity/data/espn_player_id.csv",
                           stringsAsFactors = FALSE)
rpm2 = dplyr::left_join(rpm, espn_player_ids, by = "player_name")
# Filter out some duplicates.
# The specific espn number is a wild Tony Mitchell case.
rpm2 = rpm2 %>% dplyr::filter(season >= first_season, season <= last_season, espn_number != 2489010) %>%
  dplyr::select(player_name, pos, team, gp, mpg, orpm, drpm, rpm, wins, season, espn_link, espn_number, espn_id)

# * Save data ----
write.csv(rpm, file = "data/espn_nba_rpm.csv")
