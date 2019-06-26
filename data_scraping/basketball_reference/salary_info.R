# PURPOSE: Scrape BBref Salary Information
`%>%` = dplyr::`%>%`

bbref_get_salary_one_player = function(bbref_link) {
  url = paste0('https://www.basketball-reference.com/players/', bbref_link, '.html')
  
  # Read in page
  page = tryCatch({
    xml2::read_html(url)
  },
  error = function(e) {
    stop(paste0('Unable to read bbref page for ', bbref_link))
    data.frame()
  }
  )
  

  # Read salary table
  salary_table = tryCatch({
    page %>% rvest::html_nodes(xpath = '//comment()') %>% # select comments
      rvest::html_text() %>% # extract the comments
      paste(collapse = '') %>% # collapse to single string
      xml2::read_html() %>% # Reread page
      rvest::html_node('table#all_salaries') %>% # read in college table
      rvest::html_table()
  },
  error = function(e) {
    data.frame()
  })
  
  if (nrow(salary_table) > 0) {
    salary_table = salary_table[-nrow(salary_table),]
    # Sum over a season. Players who played for multiple teams just get summed together.
    salary_table = salary_table %>% dplyr::group_by(Season) %>%
      dplyr::summarise(Salary = sum(as.numeric(stringr::str_remove_all(Salary, '\\$|,'))))
    # Clean season data
    salary_table = salary_table %>% 
      dplyr::mutate(Season = ifelse(substring(Season, 1, 2) == 19 & substring(Season, 6, 7) == '00',
                    2000,
                    as.numeric(paste0(substring(Season, 1, 2), substring(Season, 6, 7))))) %>%
      dplyr::select(season = Season, salary = Salary)
    salary_table$contract_type = 'past'
  }
  # Now get future contracts
  table_ids = 
    page %>% rvest::html_nodes(xpath = '//comment()') %>% # select comments
      rvest::html_text() %>% # extract the comments
      paste(collapse = '') %>% # collapse to single string
      xml2::read_html() %>% # Reread page
      rvest::html_nodes('table') %>% # read in all tables on page
      rvest::html_attr('id') # get the id's
  table_ids = table_ids[stringr::str_which(table_ids, "contracts_[a-z]{3}")]
  if (length(table_ids) == 0) {
    if (nrow(salary_table) == 0) {
      return(data.frame(
        bbref_id = stringr::str_split(bbref_link, '\\/', simplify = TRUE)[2],
        season = NA,
        contract_type = NA,
        salary = NA
      ))
    }
    else {
      return(cbind(bbref_id = stringr::str_split(bbref_link, '\\/', simplify = TRUE)[2],
                   salary_table))
    }
  }
  contract_table_all = data.frame()
  for (id in table_ids) {
    # Read in each of the tables with the contracts id
    contract_info = page %>% rvest::html_nodes(xpath = '//comment()') %>% # select comments
      rvest::html_text() %>% # extract the comments
      paste(collapse = '') %>% # collapse to single string
      xml2::read_html() %>% # Reread page
      rvest::html_node(paste0('table#', id))
    # Get the table as itself
    contract_table = contract_info %>% rvest::html_table()
    # Go look at Greg Monroe's bbref page...
    if (sum(is.na(contract_table)) > 0) {
      next
    }
    # Pivot it
    contract_table = tidyr::gather(contract_table, season, salary, 
                                   colnames(contract_table)[2]:colnames(contract_table)[ncol(contract_table)],
                                   factor_key = FALSE)
    # Clean Season and Salary
    contract_table = contract_table %>% 
      dplyr::mutate(
        season = ifelse(substring(season, 1, 2) == 19 & substring(season, 6, 7) == '00',
                        2000,
                        as.numeric(paste0(substring(season, 1, 2), substring(season, 6, 7)))),
        salary = as.numeric(stringr::str_remove_all(salary, '\\$|,'))
      )
    # Get the span information
    contract_table$contract_type = contract_info %>%     
      rvest::html_nodes('td span') %>%
      rvest::html_attr('class')
    contract_table = contract_table %>% 
      dplyr::mutate(
        contract_type = dplyr::case_when(
          contract_type == "salary-pl" ~ 'player_option',
          contract_type == 'salary-tm' ~ 'team_option',
          contract_type == 'salary_et' ~ 'early_termination',
          contract_type == '' ~ 'regular',
          TRUE ~ 'free_agent'
        )
      ) %>%
      dplyr::select(-Team)
    
    contract_table_all = rbind(contract_table_all, contract_table)
    
  }
  # Check out "w/willial03"
  if (nrow(contract_table_all) == 0) {
    if (nrow(salary_table) == 0) {
      return(data.frame(
        bbref_id = stringr::str_split(bbref_link, '\\/', simplify = TRUE)[2],
        season = NA,
        contract_type = NA,
        salary = NA
      ))
    }
    else {
      return(cbind(bbref_id = stringr::str_split(bbref_link, '\\/', simplify = TRUE)[2],
                   salary_table))
    }
  }
  contract_table_all = contract_table_all %>%
    dplyr::group_by(season, contract_type) %>%
    dplyr::summarise(salary = sum(salary)) %>% dplyr::ungroup()
  # Join past and future data
  salary_data = rbind(salary_table, contract_table_all)
  salary_data = cbind(bbref_id = stringr::str_split(bbref_link, '\\/', simplify = TRUE)[2],
                      salary_data)
  
  return(salary_data) 
}

bbref_get_salary = function(bbref_links, parallel = TRUE) {
  `%dopar%` = foreach::`%dopar%`
  # Set up parallel running
  if (parallel) {
    cores = parallel::detectCores()
    cl = parallel::makeCluster(cores[1] - 1)
    doParallel::registerDoParallel(cl)
  }
  # Run over each player
  player_df = foreach::foreach(bbref_link = bbref_links, .combine=rbind, .export = 'bbref_get_salary_one_player') %dopar% {
    `%>%` = dplyr::`%>%`
    bbref_get_salary_one_player(bbref_link)
  }
  # Stop parralel
  if (parallel) {
    parallel::stopCluster(cl)
  }
  
  return(player_df) 
}

bbref_salary_history= function() {
  url = 'https://www.basketball-reference.com/contracts/salary-cap-history.html'
  salary_cap = 
    xml2::read_html(url) %>%
    rvest::html_nodes(xpath = '//comment()') %>% # select comments
    rvest::html_text() %>% # extract the comments
    paste(collapse = '') %>% # collapse to single string
    xml2::read_html() %>% # Reread page
    rvest::html_node('#salary_cap_history') %>% # read in college table
    rvest::html_table()    
  # Clean seasons and salary
  salary_cap = salary_cap %>%
    dplyr::mutate(
      season = ifelse(substring(Year, 1, 2) == 19 & substring(Year, 6, 7) == '00',
                      2000,
                      as.numeric(paste0(substring(Year, 1, 2), substring(Year, 6, 7)))),
      salary_cap = as.numeric(stringr::str_remove_all(`Salary Cap`, '\\$|,'))
    ) %>%
    dplyr::select(season, salary_cap)
  # Add projected salary caps for present and future years
  salary_cap = rbind(salary_cap, data.frame(season = c(2019, 2020, 2021),
                                            salary_cap = c(101869000,  109e6, 116e6)))
  
  return(salary_cap)
  
}

bbref_players = read.csv('~/Documents/nba_positional_scarcity/data/player_table.csv',
                         stringsAsFactors = FALSE)
salary_info = bbref_get_salary(bbref_players$bbref_link, TRUE)
salary_cap = bbref_salary_history()

salary_info_all = dplyr::left_join(salary_info, salary_cap, by = 'season')
# Add salaryt as % of cap
salary_info_all = salary_info_all %>% 
  dplyr::mutate(salary_prop_cap = salary / salary_cap) %>% 
  dplyr::select(-salary_cap)