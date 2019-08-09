library(tidyverse)

# * Data ----
players = read.csv('nba_projects/data/player_ids/player_table.csv', stringsAsFactors = FALSE)
positions = read.csv('nba_projects/data/nba/basketball_reference/player_data/positional_estimates/player_position_estimates.csv',
                     stringsAsFactors = FALSE)
stats = read.csv('nba_projects/data/nba/basketball_reference/player_data/combined/bbref_player_data.csv',
                 stringsAsFactors = FALSE)

measurements = read.csv('nba_projects/data/nba/basketball_reference/player_data/measurements/player_measurements.csv',
                        stringsAsFactors = FALSE)

stats = stats %>% select(-PLAYER, -POSITION)

# Keep total rows or if a player just played on one team
stats = stats %>% dplyr::group_by(BBREF_ID, SEASON) %>% dplyr::mutate(row = row_number()) %>%
  dplyr::mutate(max_row = max(row)) %>%
  dplyr::ungroup() %>%
  dplyr::mutate(team_flag = ifelse(max_row == 1 | TEAM == 'TOT', TRUE, FALSE)) %>%
  dplyr::select(-row, -max_row) %>%
  dplyr::filter(team_flag)

# * JOIN ----
stats = left_join(stats, measurements, by = c("BBREF_ID" = "bbref_id"))

# * Percentiles
# First don't do it by position
stats_percentile = stats %>%
  group_by(SEASON) %>%
  mutate(height_percentile_all = percent_rank(height),
         weight_percentile_all = percent_rank(weight),
         age_percentile_all = percent_rank(desc(AGE)),
         games_played_percentile_all = percent_rank(G),
         games_started_percentile_all = percent_rank(GS),
         minutes = MP,
         minutes_percentile_all = percent_rank(MP),
         fg_percentile_all = percent_rank(FG),
         fga_percentile_all = percent_rank(FGA),
         fg_percent_percentile_all = percent_rank(`FG.`),
         three_point_made_percentile_all = percent_rank(X3P),
         three_point_attempt_percentile_all = percent_rank(X3PA),
         three_point_percent_percentile_all = percent_rank(`X3P.`),
         two_point_made_percentile_all = percent_rank(X2P),
         two_point_attempt_percentile_all = percent_rank(X2PA),
         two_point_percent_percentile_all = percent_rank(`X2P.`),
         efg_percent_percentile_all = percent_rank(`eFG.`),
         true_shooting_percent_percentile_all = percent_rank(`TS.`),
         free_throw_made_percentile_all = percent_rank(FT),
         free_throw_attempt_percentile_all = percent_rank(FTA),
         free_throw_percent_percentile_all = percent_rank(`FT.`),
         oreb_percentile_all = percent_rank(ORB),
         drb_percentile_all = percent_rank(DRB),
         trb_percentile_all = percent_rank(TRB),
         ast_percentile_all = percent_rank(AST),
         stl_percentile_all = percent_rank(STL),
         blk_percentile_all = percent_rank(BLK),
         turnover_percentile_all = percent_rank(TOV),
         foul_percentile_all = percent_rank(PF),
         points_percentile_all = percent_rank(PTS),
         # Per 100 Stats
         fg_made_per100_percentile_all = percent_rank(PER100_FG),
         fg_attempted_per100_percentile_all = percent_rank(PER100_FGA),
         three_point_made_per100_percentile_all = percent_rank(PER100_3P),
         three_point_attempt_per100_percentile_all = percent_rank(PER100_3PA),
         two_point_made_per100_percentile_all = percent_rank(PER100_2P),
         two_point_attempt_per100_percentile_all = percent_rank(PER100_2PA),
         free_throw_made_per100_percentile_all = percent_rank(PER100_FT),
         free_throw_attempt_per100_percentile_all = percent_rank(PER100_FTA),
         oreb_percentile_per100_all = percent_rank(PER100_ORB),
         drb_percentile_per100_all = percent_rank(PER100_DRB),
         total_percentile_per100_all = percent_rank(PER100_TRB),
         ast_percentile_per100_all = percent_rank(PER100_AST),
         stl_percentile_per100_all = percent_rank(PER100_STL),
         blk_percentile_per100_all = percent_rank(PER100_BLK),
         tov_percentile_per100_all = percent_rank(PER100_TOV),
         foul_percentile_per100_all = percent_rank(PER100_PF),
         points_percentile_per100_all = percent_rank(PER100_PTS),
         # Rate Stats
         three_point_attempt_rate_percentile_all = percent_rank(X3PA_RATE),
         free_throw_rate_percentile_all = percent_rank(FT_RATE),
         orb_percent_percentile_all = percent_rank(`ORB.`),
         drb_percent_percentile_all = percent_rank(`DRB.`),
         trb_percent_percentile_all = percent_rank(`TRB.`),
         ast_percent_percentile_all = percent_rank(`AST.`),
         stl_percent_percentile_all = percent_rank(`STL.`),
         blk_percent_percentile_all = percent_rank(`BLK.`),
         tov_percent_percentile_all = percent_rank(`TOV.`),
         usg_percent_percentile_all = percent_rank(`USG.`),
         # Percent Stats
         off_win_shares_percentile_all = percent_rank(OWS),
         def_win_shares_percentile_all = percent_rank(DWS),
         win_shares_percentile_all = percent_rank(WS),
         win_sharres_per_48_percentile_all = percent_rank(`WS.48`),
         off_bpm_percentile_all = percent_rank(OBPM),
         def_bpm_percentile_all = percent_rank(DBPM),
         bpm_percentile_all = percent_rank(BPM),
         vorp_percentile_all = percent_rank(VORP)
         ) %>%
  select(BBREF_ID, SEASON, contains('percentile_all'))

write.csv(stats_percentile, file = "~/Documents/nba_projects/data/nba/basketball_reference/player_data/percentile/nba_percentile_all.csv",
          row.names = FALSE)

# Now by position | season
# Join position
stats = stats %>%
  mutate(season_temp = as.integer(substr(SEASON, 6,10)))
stats = inner_join(stats, positions %>% select(bbref_id, season, advanced_position_cluster), 
                   by = c("BBREF_ID" = 'bbref_id', "season_temp" = "season"))
stats_percentile = stats %>%
  group_by(SEASON, advanced_position_cluster) %>%
  mutate(height_percentile_position = percent_rank(height),
         weight_percentile_position = percent_rank(weight),
         age_percentile_position = percent_rank(desc(AGE)),
         games_played_percentile_position = percent_rank(G),
         games_started_percentile_position = percent_rank(GS),
         minutes = MP,
         minutes_percentile_position = percent_rank(MP),
         fg_percentile_position = percent_rank(FG),
         fga_percentile_position = percent_rank(FGA),
         fg_percent_percentile_position = percent_rank(`FG.`),
         three_point_made_percentile_position = percent_rank(X3P),
         three_point_attempt_percentile_position = percent_rank(X3PA),
         three_point_percent_percentile_position = percent_rank(`X3P.`),
         two_point_made_percentile_position = percent_rank(X2P),
         two_point_attempt_percentile_position = percent_rank(X2PA),
         two_point_percent_percentile_position = percent_rank(`X2P.`),
         efg_percent_percentile_position = percent_rank(`eFG.`),
         true_shooting_percent_percentile_position = percent_rank(`TS.`),
         free_throw_made_percentile_position = percent_rank(FT),
         free_throw_attempt_percentile_position = percent_rank(FTA),
         free_throw_percent_percentile_position = percent_rank(`FT.`),
         oreb_percentile_position = percent_rank(ORB),
         drb_percentile_position = percent_rank(DRB),
         trb_percentile_position = percent_rank(TRB),
         ast_percentile_position = percent_rank(AST),
         stl_percentile_position = percent_rank(STL),
         blk_percentile_position = percent_rank(BLK),
         turnover_percentile_position = percent_rank(TOV),
         foul_percentile_position = percent_rank(PF),
         points_percentile_position = percent_rank(PTS),
         # Per 100 Stats
         fg_made_per100_percentile_position = percent_rank(PER100_FG),
         fg_attempted_per100_percentile_position = percent_rank(PER100_FGA),
         three_point_made_per100_percentile_position = percent_rank(PER100_3P),
         three_point_attempt_per100_percentile_position = percent_rank(PER100_3PA),
         two_point_made_per100_percentile_position = percent_rank(PER100_2P),
         two_point_attempt_per100_percentile_position = percent_rank(PER100_2PA),
         free_throw_made_per100_percentile_position = percent_rank(PER100_FT),
         free_throw_attempt_per100_percentile_position = percent_rank(PER100_FTA),
         oreb_percentile_per100_position = percent_rank(PER100_ORB),
         drb_percentile_per100_position = percent_rank(PER100_DRB),
         total_percentile_per100_position = percent_rank(PER100_TRB),
         ast_percentile_per100_position = percent_rank(PER100_AST),
         stl_percentile_per100_position = percent_rank(PER100_STL),
         blk_percentile_per100_position = percent_rank(PER100_BLK),
         tov_percentile_per100_position = percent_rank(PER100_TOV),
         foul_percentile_per100_position = percent_rank(PER100_PF),
         points_percentile_per100_position = percent_rank(PER100_PTS),
         # Rate Stats
         three_point_attempt_rate_percentile_position = percent_rank(X3PA_RATE),
         free_throw_rate_percentile_position = percent_rank(FT_RATE),
         orb_percent_percentile_position = percent_rank(`ORB.`),
         drb_percent_percentile_position = percent_rank(`DRB.`),
         trb_percent_percentile_position = percent_rank(`TRB.`),
         ast_percent_percentile_position = percent_rank(`AST.`),
         stl_percent_percentile_position = percent_rank(`STL.`),
         blk_percent_percentile_position = percent_rank(`BLK.`),
         tov_percent_percentile_position = percent_rank(`TOV.`),
         usg_percent_percentile_position = percent_rank(`USG.`),
         # Percent Stats
         off_win_shares_percentile_position = percent_rank(OWS),
         def_win_shares_percentile_position = percent_rank(DWS),
         win_shares_percentile_position = percent_rank(WS),
         win_sharres_per_48_percentile_position = percent_rank(`WS.48`),
         off_bpm_percentile_position = percent_rank(OBPM),
         def_bpm_percentile_position = percent_rank(DBPM),
         bpm_percentile_position = percent_rank(BPM),
         vorp_percentile_position = percent_rank(VORP)
  ) %>%
  select(BBREF_ID, SEASON, advanced_position_cluster, contains('percentile_position'))

write.csv(stats_percentile, file = "~/Documents/nba_projects/data/nba/basketball_reference/player_data/percentile/nba_percentile_position.csv",
          row.names = FALSE)

