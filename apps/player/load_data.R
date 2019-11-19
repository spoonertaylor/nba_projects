# PURPOSE: Load Data Sources
`%>%` = dplyr::`%>%`

file_path = paste0(getwd(), "/../../data/")
player = read.csv(paste0(file_path, 'player_ids/player_table.csv'), stringsAsFactors = FALSE)
player = player %>% filter(!is.na(player_name))

team = read.csv(paste0(file_path, 'nba/team_id/nba_team_id.csv'), stringsAsFactors = FALSE)
# Projection table
projection = read.csv("../../modeling/player_projection_model/chris/modeling/predictions/actuals_and_predictions.csv", stringsAsFactors = FALSE)

# Position table
position = read.csv(paste0(file_path, 'nba/basketball_reference/player_data/positional_estimates/player_position_estimates.csv'),
                    stringsAsFactors = FALSE)
# Percentile by position
percentile = read.csv(paste0(file_path, 'nba/basketball_reference/player_data/percentile/nba_percentile_position.csv'),
                      stringsAsFactors = FALSE)

colnames(percentile) = tolower(colnames(percentile))
percentile = percentile %>% 
  mutate(season = ifelse(nchar(season) > 4, as.integer(stringr::str_sub(season, 6, 9)), as.integer(season)))

advanced_stats = read.csv(paste0(file_path, 'nba/basketball_reference/player_data/advanced/advanced_table.csv'),
                          stringsAsFactors = FALSE)

# Measurements
measurements = read.csv(paste0(file_path, 'nba/basketball_reference/player_data/measurements/player_measurements.csv'),
                        stringsAsFactors = FALSE)

# Salary Data
salary = read.csv(paste0(file_path, "nba/basketball_reference/player_data/salary/salary_info.csv"),
                  stringsAsFactors = FALSE)

# Player Info
player_info = position %>% 
  select(bbref_id, season, age, experience, position_minutes, position_numeric, advanced_position_cluster) %>%
  group_by(bbref_id) %>% mutate(max_season = max(season)) %>%
  filter(season == max_season) %>% select(-max_season) %>% ungroup()

player_info = inner_join(player_info, measurements %>% select(bbref_id, feet, inches, weight), by = 'bbref_id')
player_info = player_info %>% mutate(height = paste0(feet, "'", inches, '"'))

player_info = inner_join(player_info, player %>% select(player_name, bbref_id), by = 'bbref_id')

percentile_info = percentile %>% group_by(bbref_id) %>% mutate(max_season = max(season)) %>%
  filter(season == max_season) %>% 
  select(bbref_id, age_percentile_position,height_percentile_position, weight_percentile_position) %>%
  ungroup()
player_info = inner_join(player_info, percentile_info, by = 'bbref_id')

# Per Game Stats ----
per_game = read.csv(paste0(file_path, "nba/basketball_reference/player_data/per_game/per_game_table.csv"),
                    stringsAsFactors = FALSE)
per_game = per_game %>% filter(season >= 2014)
per_game_percentile = read.csv(paste0(file_path, "nba/basketball_reference/player_data/percentile/nba_per_game_percentile_position.csv"),
                       stringsAsFactors = FALSE)
per_game_percentile = per_game_percentile %>% filter(season >= 2014)

per_game = per_game %>% left_join(per_game_percentile %>% select(-age, -team), by = c('bbref_id', 'season'))
# Per 100 Stats ----
per_100 = read.csv(paste0(file_path, "nba/basketball_reference/player_data/per100_poss/per100_poss.csv"),
                   stringsAsFactors = FALSE) %>%
  mutate(SEASON = as.numeric(paste0('20', stringr::str_sub(SEASON, 8, 9))))
colnames(per_100) = tolower(colnames(per_100))
