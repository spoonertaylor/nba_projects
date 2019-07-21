# * PURPOSE: Cluster NBA players into 3 primary positions: Guards, Wings, Bigs
# * Library -----
library(tidyverse)

# * Data ----
positions = read.csv('nba_projects/data/nba/basketball_reference/player_data/positional_estimates/player_position_estimates.csv',
                     stringsAsFactors = FALSE)
measurements = read.csv('nba_projects/data/nba/basketball_reference/player_data/measurements/player_measurements.csv',
                        stringsAsFactors = FALSE)

players = read.csv('nba_projects/data/player_ids/player_table.csv', stringsAsFactors = FALSE)

advanced_data = read.csv('nba_projects/data/nba/basketball_reference/player_data/advanced/advanced_table.csv',
                         stringsAsFactors = FALSE)
advanced_data = advanced_data %>% filter(team_flag) %>%
  select(-c(age, team, league, position,games_played, minutes_played, team_flag))
# Get rid of non total rows
# For players that had multiple teams in same season, flag column of which column to keep
positions = positions %>% dplyr::group_by(bbref_id, season) %>% dplyr::mutate(row = row_number()) %>%
  dplyr::mutate(max_row = max(row)) %>%
  dplyr::ungroup() %>%
  dplyr::mutate(team_flag = ifelse(max_row == 1 | team == 'TOT', TRUE, FALSE)) %>%
  dplyr::select(-row, -max_row) %>%
  dplyr::filter(team_flag)


# Left join measurements onto positions
df = left_join(positions, measurements, by = 'bbref_id') %>% inner_join(players %>% select(player_name, bbref_id), on = "bbref_id")
# Join on advanced table
df = left_join(df, advanced_data, by = c('bbref_id', 'season'))

# * Clustering ----
df2 = df %>% filter(season >= 2004) %>% replace(., is.na(.), 0)
df_scale = scale(df2 %>%
            select(prop_pg, prop_sf, prop_c, height, weight,
                               three_point_rate, ORB_perc, DRB_perc, AST_perc, BLK_perc,
                   USG_perc, TS_perc))

clusters = kmeans(df_scale, 3, nstart = 50)
positions$advanced_position_cluster = NA
positions[positions$season >= 2004, 'advanced_position_cluster'] = as.factor(clusters$cluster)
positions = positions %>% mutate(advanced_position_cluster = case_when(
  advanced_position_cluster == 1 ~ 'Big',
  advanced_position_cluster == 2 ~ 'Wing',
  advanced_position_cluster == 3 ~ 'Guard'
))

# * Plotting ----
ggplot(positions, aes(x = three_point_rate, y = AST_perc, color = cluster))+ geom_point()

ggplot(df2, aes(x = factor(position_minutes, levels = c('PG', 'SG', 'SF', 'PF', 'C')))) +
  geom_bar(aes(fill = cluster), position = 'fill') + xlab("") + theme_minimal() +
  #facet_wrap(.~season) + 
  theme(text = element_text(family = "Roboto Condensed"),
        title = element_text(size = 18),
        plot.subtitle = element_text(size = 16),
        plot.caption = element_text(size = 10),
        axis.title = element_text(size = 14),
        axis.text = element_text(size = 12),
        panel.grid.minor.x = element_blank(),
        legend.position = 'top')

temp = df2 %>% group_by(season, position_minutes, cluster) %>% summarise(n = n()) %>% 
  ungroup() %>% group_by(season, position_minutes) %>% mutate(prop = n / sum(n))
ggplot(temp %>% filter(position_minutes == 'PF'), aes(x = season, y = prop, color = cluster)) + geom_line()