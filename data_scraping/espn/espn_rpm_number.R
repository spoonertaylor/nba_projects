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
  # Get ESPN links
  links = rvest::html_nodes(body, xpath = '//*[@id="my-players-table"]/div/div[2]/table') %>% 
    rvest::html_nodes('a') %>% rvest::html_attr('href')
  idx = stringr::str_detect(links, "id/[0-9]+/.+")
  links = links[idx]
  links = stringr::str_extract(links, "id/[0-9]+/.+") %>%
    stringr::str_remove('id/')
  if (length(links) == nrow(table)) {
    table$espn_link = links
  }
  else {
    names =   links = rvest::html_nodes(body, xpath = '//*[@id="my-players-table"]/div/div[2]/table') %>% 
      rvest::html_nodes('a') %>% rvest::html_text()
    names = names[idx]
    id_df = data.frame(name = names, espn_link = links)
    table = dplyr::left_join(table, id_df, by = 'name')
  }

  # In case there was a player that played in multiple teams
  table = table %>% tidyr::separate(player_name, into = c("name", "pos"), sep = ', ') %>%
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

# * Save data ----
write.csv(rpm, file = "~/Documents/nba_positional_scarcity/data/espn_nba_rpm.csv", row.names = FALSE)
