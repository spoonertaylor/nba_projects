library(tidyverse)
`%>%` = `%>%`
get_current_season = function() {
  date = Sys.Date()
  year = lubridate::year(date)
  month = lubridate::month(date)
  
  if (month %in% c(10, 11, 12)) {
    year = integer(year) + 1
  }
  return(year)
}

plot_player_projection = function(df, bbref_player_id, start_year = NULL) {
  player_name = read.csv('nba_projects/data/player_ids/player_table.csv', stringsAsFactors = FALSE)
  player_name = player_name[player_name$bbref_id == bbref_player_id, 'player_name']
  # Rename variables
  df = df %>% dplyr::rename_at(dplyr::vars(dplyr::contains('bbref_id')), 
                               list('bbref_id' = ~paste('bbref_id'))) %>%
              dplyr::rename_at(dplyr::vars(dplyr::contains('season')), 
                               list('season' = ~paste('season')))
  df = df %>% dplyr::rename_if(stringr::str_detect(colnames(df), "bbref_id|season", negate = TRUE), 
                          list('blend' = ~paste('blend')))
  # Filter
  player_df = df %>% filter(bbref_id == bbref_player_id)
  if (is.null(start_year)) {
    seasons_played = min(player_df$season):max(player_df$season)
  }
  else {
    seasons_played = start_year:max(player_df$season)
    player_df = player_df %>% filter(season >= start_year)
  }

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
      title = paste0(player_name, " Projection"),
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
  
  return(plot)
  
}
