# PURPOSE: Global script to hold misc functions and package loading
`%!in%` = function(x,y)!('%in%'(x,y))
list.of.packages <- c("shiny","tidyverse", "DT", "shinyWidgets", "devtools", "shinyjs")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages,function(x){library(x,character.only=TRUE)}) 
library(shinyjs)

# * Source Files ----
# * Data ----
source('load_data.R')

# * Rand Start ----
rand_row = sample(1:nrow(player), 1)

# * Functions ----
# ** Get Current Season ----
get_current_season = function() {
  date = Sys.Date()
  year = lubridate::year(date)
  month = lubridate::month(date)
  
  if (month %in% c(10, 11, 12)) {
    year = integer(year) + 1
  }
  return(year)
}

# ** Percentile Color ----
get_percentile_color = function(percentile) {
  colfunc = colorRampPalette(c("red", "green3"))
  percentiles = colfunc(101)
  return(percentiles[percentile+1])
}

# ** Plot Player Projection ----
plot_player_projection = function(player_df) {
  if (nrow(player_df) == 0) {
    seasons_played = 2014:(get_current_season()+4)
    df = data.frame(seasons_played = 2014:(get_current_season()+4),
                    blend = rep(0, length(seasons_played)))
    return(ggplot(df, aes(x = seasons_played, y = blend)) + geom_blank() +
             theme_minimal() + 
             theme(text = element_text(family = "Roboto Condensed"),
                   title = element_text(size = 18),
                   plot.subtitle = element_text(size = 16),
                   plot.caption = element_text(size = 10),
                   axis.title = element_text(size = 14),
                   axis.text = element_text(size = 12),
                   panel.grid.minor.x = element_blank()) +
             scale_y_continuous(name = "", limits = c(-5, 10)) +
             scale_x_continuous(breaks = seasons_played, labels = paste0("'", as.numeric(stringr::str_sub(seasons_played, 3, 4)))) + 
             geom_vline(aes(xintercept = get_current_season())) +
             labs(
               title = "Player Projection",
               x = ""
             ) 
    ) 
  }
  
  # Rename variables
  player_df = player_df %>% dplyr::rename_at(dplyr::vars(dplyr::contains('bbref_id')), 
                                             list('bbref_id' = ~paste('bbref_id'))) %>%
    dplyr::rename_at(dplyr::vars(dplyr::contains('season')), 
                     list('season' = ~paste('season')))
  player_df = player_df %>% dplyr::rename_if(stringr::str_detect(colnames(player_df), "bbref_id|season", negate = TRUE), 
                                             list('blend' = ~paste('blend')))
  
  player_df = player_df %>% mutate(season = ifelse(stringr::str_detect(season, "-"),
                                                   as.numeric(stringr::str_sub(season, 6, 9)),
                                                   season))
  # Filter
  seasons_played = min(player_df$season):max(player_df$season)
  if (nrow(player_df %>% filter(season > get_current_season())) == 0) {
    plot = ggplot(player_df %>% filter(season <= get_current_season()),
                  aes(x = season, y = blend)) + 
      geom_line(inherit.aes = TRUE,
                linetype = "solid", size = 2) +
      geom_point(data = player_df %>% filter(season <= get_current_season()),
                 size = 4, color = 'white', fill = "black", pch = 21) +
      geom_text(data = player_df %>% filter(season <= get_current_season()),
                aes(label = formatC(blend, format = "f", digits = 1)), 
                nudge_y = .5, fontface = "bold", family = "Roboto Condensed") +
      scale_y_continuous(name = "", limits = c(min(player_df$blend, -5), max(player_df$blend, 10))) +
      scale_x_continuous(breaks = seasons_played, labels = paste0("'", stringr::str_sub(seasons_played, 3, 4))) + 
      geom_vline(aes(xintercept = get_current_season())) +
      theme_minimal() +
      theme(text = element_text(family = "Roboto Condensed"),
            title = element_text(size = 18),
            plot.subtitle = element_text(size = 16),
            plot.caption = element_text(size = 10),
            axis.title = element_text(size = 14),
            axis.text = element_text(size = 12),
            panel.grid.minor.x = element_blank()) +
      labs(
        title = "Player Projection",
        x = ""
      ) 
    
  }
  else {
    plot = ggplot(player_df %>% filter(season >= get_current_season()), 
                  aes(x = season, y = blend)) + 
      geom_line(size = 2, linetype = "dotted") +
      geom_point(size = 4, color = 'white', fill = "black", pch = 21) +
      geom_text(aes(label = formatC(blend, format = "f", digits = 1)), 
                nudge_y = .5, fontface = "bold", family = "Roboto Condensed") +
      scale_y_continuous(name = "", limits = c(min(player_df$blend, -5), max(player_df$blend, 10))) +
      scale_x_continuous(breaks = seasons_played, labels = paste0("'", stringr::str_sub(seasons_played, 3, 4))) + 
      geom_vline(aes(xintercept = get_current_season())) +
      theme_minimal() +
      theme(text = element_text(family = "Roboto Condensed"),
            title = element_text(size = 18),
            plot.subtitle = element_text(size = 16),
            plot.caption = element_text(size = 10),
            axis.title = element_text(size = 14),
            axis.text = element_text(size = 12),
            panel.grid.minor.x = element_blank()) +
      labs(
        title = "Player Projection",
        x = ""
      )
    
    if (nrow(player_df %>% filter(season < get_current_season())) > 0) {
      plot = plot + geom_line(data = player_df %>% filter(season <= get_current_season()),
                              inherit.aes = TRUE,
                              linetype = "solid", size = 2) +
        geom_point(data = player_df %>% filter(season <= get_current_season()),
                   size = 4, color = 'white', fill = "black", pch = 21) +
        geom_text(data = player_df %>% filter(season <= get_current_season()),
                  aes(label = formatC(blend, format = "f", digits = 1)), 
                  nudge_y = .5, fontface = "bold", family = "Roboto Condensed")
      
    }
    
  }
  
  return(plot)
  
}

# * Prep Data ----
# Create player selection table
# First find the last team everyone played for
player_select = advanced_stats %>% filter(team != 'TOT', season >= 2014) %>%
  group_by(bbref_id) %>% mutate(max_season = max(season)) %>%
  filter(season == max_season) %>% mutate(team_number = row_number()) %>% 
  mutate(max_row_number = max(team_number)) %>% filter(team_number == max_row_number) %>%
  select(bbref_id, team)

# Now join on player name
player_select = inner_join(player_select, player, by = 'bbref_id')
# Now join team name
player_select = left_join(player_select, team, by = c('team' = 'bbref_team_id'))

# Create selection column
player_select = player_select %>% mutate(player_select_col = paste0(player_name, " (", team_mascot, ")"))
player_select = player_select %>% arrange(last_name_lower)


# Prep advanced stats
advanced_stats = advanced_stats %>% filter(season >= 2014) %>% 
  group_by(bbref_id, season) %>%
  mutate(team_number = ifelse(team == 'TOT', 99, row_number()))  %>%
  mutate(max_team_number = max(team_number)) %>%
  mutate(team_number = ifelse(max_team_number == 99, team_number-1, team_number)) %>%
  arrange(bbref_id, season, team_number) %>% ungroup()

# Prep percentile data
percentile = percentile %>%
  select(bbref_id, season, advanced_position_cluster, age_percentile_position, games_played_percentile_position, minutes_percentile_position,
         true_shooting_percent_percentile_position, usg_percent_percentile_position)

stats_percentiles = left_join(advanced_stats, percentile, by = c('bbref_id', 'season')) 

stats_percentiles = stats_percentiles %>%
  mutate(
    Season = ifelse(team_number == 1, 
                    paste0("<text class ='full_team'>", season, "</text>"), ""),
    Team = ifelse(team == 'TOT' | max_team_number != 99, 
                  paste0("<text class='full_team'>", team, "</text>"),
                  paste0("<text class='trade_team'>", team, "</text>")),
    Pos = ifelse(team == 'TOT' | max_team_number != 99,
                 paste0("<text class='full_team'>", advanced_position_cluster, "</text>"),
                 paste0("<text class='trade_team'>", advanced_position_cluster, "</text>")),
    Age = case_when(
      team == 'TOT' | max_team_number != 99 ~ 
        paste0("<pre> <text class='full_team'>", age, "</text><text class='percentile' style='color:", 
               get_percentile_color(round(100*age_percentile_position, 0)),
               "'>&nbsp;",
               round(100*age_percentile_position, 0), "</text>",
               case_when(
                 round(100*age_percentile_position, 0) == 100 ~ "</pre>",
                 round(100*age_percentile_position, 0) >= 10 ~ "&nbsp;</pre>",
                 TRUE ~ "&nbsp;&nbsp;</pre>"
               )),
      TRUE ~ paste0("<text class='trade_team'><pre>", age, "&nbsp;&nbsp;&nbsp;&nbsp;</pre></text>")
      
    ),
    GP = case_when(
      is.na(games_played) ~ "",
      team == 'TOT' | max_team_number != 99 ~ 
        paste0("<text class='full_team'>", games_played, 
               "</text><text class='percentile' style='color:",
               get_percentile_color(round(100*games_played_percentile_position, 0)),
               "'> ", round(100*games_played_percentile_position, 0), "</text>"),
      TRUE ~ paste0("<text class='trade_team'>", games_played, "</text>")
      
    ),
    MP = case_when(
      is.na(minutes_played) ~ "",
      team == 'TOT' | max_team_number != 99 ~ 
        paste0("<text class='full_team'>",
               minutes_played, "</text><text class='percentile' style='color:",
               get_percentile_color(round(100*minutes_percentile_position, 0)),
               "'> ", round(100*minutes_percentile_position, 0), "</text>"),
      TRUE ~ paste0("<text class='trade_team'>", minutes_played, "</text>")
    ),
    `TS%` = case_when(
      is.na(TS_perc) ~ "",
      team == 'TOT' | max_team_number != 99 ~ 
        paste0("<text class='full_team'>",
               format(round(100*TS_perc,1), nsmall = 1), 
               "%</text><text class='percentile' style='color:",
               get_percentile_color(round(100*true_shooting_percent_percentile_position, 0)),
               "'> ", round(100*true_shooting_percent_percentile_position, 0), "</text>"),
      TRUE ~ paste0("<text class='trade_team'>", format(round(100*TS_perc,1)), "% &nbsp;&nbsp;</text>")
    ),
    `USG%` = case_when(
      is.na(USG_perc) ~ "",
      team == 'TOT' | max_team_number != 99 ~ 
        paste0("<text class='full_team'>",
               format(USG_perc, nsmall = 1),
               "%</text><text class='percentile' style='color:",
               get_percentile_color(round(100*usg_percent_percentile_position, 0)),
               "'> ", round(100*usg_percent_percentile_position, 0), "</text>"),
      TRUE ~ paste0("<text class ='trade_team'>", format(USG_perc, nsmall = 1), "%</text>")
    )
  ) %>%
  select(bbref_id, Season, Team, Pos, Age, GP, MP, `TS%`, `USG%`)
# * Salary Data ----
salary = salary %>% 
  mutate(
          Season = case_when(
            season > get_current_season() &
              contract_type == 'regular' ~
              paste0("<text class='contract_future_regular'>", season, "</text>"),
            season > get_current_season() &
              contract_type == 'team_option' ~
              paste0("<text class='contract_future_team_option'>", season, "</text>"),
            season > get_current_season() &
              contract_type == 'player_option' ~
              paste0("<text class='contract_future_player_option'>", season, "</text>"),
            season > get_current_season() &
              contract_type == 'free_agent' ~
              paste0("<text class='contract_future_early_term'>", season, "</text>"),
            season <= get_current_season() ~
              paste0("<text class='contract_past'>", season, "</text>"),
            TRUE ~ paste0("<text class='contract_past'>", season, "</text>")
          ),
         Salary = case_when(
           season > get_current_season() &
             contract_type == 'regular' ~
             paste0("<text class='contract_future_regular'>$", format(salary, big.mark = ",", big.interval = 3),
                    "</text>"),
           season > get_current_season() &
             contract_type == 'team_option' ~
             paste0("<text class='contract_future_team_option'>$", format(salary, big.mark = ",", big.interval = 3),
                    "</text>"),
           season > get_current_season() &
             contract_type == 'player_option' ~
             paste0("<text class='contract_future_player_option'>$", format(salary, big.mark = ",", big.interval = 3),
                    "</text>"),
           season > get_current_season() &
             contract_type == 'free_agent' ~
             paste0("<text class='contract_future_early_term'>$", format(salary, big.mark = ",", big.interval = 3),
                    "</text>"),
           season <= get_current_season() ~
             paste0("<text class='contract_past'>$", format(salary, big.mark = ",", big.interval = 3),
                    "</text>"),
           TRUE ~ format(salary, big.mark = ",", big.interval = 3)
         ),
         `% of Cap` = case_when(
           is.na(salary_prop_cap) &
             contract_type == 'regular' ~
             paste0("<text class='contract_future_regular'>-</text>"),
           is.na(salary_prop_cap) &
             contract_type == 'team_option' ~
             paste0("<text class='contract_future_team_option'>-</text>"),
           is.na(salary_prop_cap) &
             contract_type == 'player_option' ~
             paste0("<text class='contract_future_player_option'>-</text>"),
           is.na(salary_prop_cap) &
             contract_type == 'free_agent' ~
             paste0("<text class='contract_future_early_term'>-</text>"),
           season <= get_current_season() ~
             paste0("<text class='contract_past'>", round(100*salary_prop_cap, 0), "%",
                    "</text>"),
           season > get_current_season() &
             contract_type == 'regular'~ 
             paste0("<text class='contract_future_regular'>", round(100*salary_prop_cap, 0), "%",
                                    "</text>"),
           !is.na(salary_prop_cap) &
             contract_type == 'team_option'~ 
             paste0("<text class='contract_future_team_option'>", round(100*salary_prop_cap, 0), "%",
                    "</text>"),
           !is.na(salary_prop_cap) &
             contract_type == 'player_option'~ 
             paste0("<text class='contract_future_player_option'>", round(100*salary_prop_cap, 0), "%",
                    "</text>"),
           !is.na(salary_prop_cap) &
             contract_type == 'free_agent'~ 
             paste0("<text class='contract_future_early_term'>", round(100*salary_prop_cap, 0), "%",
                    "</text>")
         )) %>%
    select(bbref_id, Season, Salary, `% of Cap`)

# * Per 100 ----
