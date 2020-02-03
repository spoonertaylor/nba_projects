library(tidyverse)

pbp = list.files(path = "~/Documents/nba_projects/data/nba/pbp/",
                 pattern = "*.csv",
                 full.names = TRUE) %>% 
        map_df(~read_csv(.))

# Filter out garbage time
pbp = pbp %>%
  mutate(score_diff = abs(home_score - away_score)) %>%
  mutate(garbage_time = case_when(
    period == 4 & pctimestring <= "12:00" & pctimestring >= "9:00" & score_diff >= 25 ~ TRUE,
    period == 4 & pctimestring <= "9:00" & pctimestring >= "6:00" & score_diff >= 20 ~ TRUE,
    period == 4 & pctimestring <= "6:00" & score_diff >= 15 ~ TRUE,
    TRUE ~ FALSE
  ))

pbp = pbp %>% filter(!garbage_time)

home_pbp = pbp %>% select(season, game_date, game_id, period, pctimestring,
                          home_team_abbrev, away_team_abbrev,
                          home_player_1,
                          home_player_2,
                          home_player_3,
                          home_player_4,
                          home_player_5) %>%
  rename(team_id = home_team_abbrev,
         opp_id = away_team_abbrev,
         player_1 = home_player_1,
         player_2 = home_player_2,
         player_3 = home_player_3,
         player_4 = home_player_4,
         player_5 = home_player_5) %>%
  distinct()

away_pbp = pbp %>% select(season, game_date, game_id, period, pctimestring,
                          home_team_abbrev, away_team_abbrev,
                          away_player_1,
                          away_player_2,
                          away_player_3,
                          away_player_4,
                          away_player_5) %>%
  rename(team_id = away_team_abbrev,
         opp_id = home_team_abbrev,
         player_1 = away_player_1,
         player_2 = away_player_2,
         player_3 = away_player_3,
         player_4 = away_player_4,
         player_5 = away_player_5) %>%
  distinct()

pbp_wide = rbind(home_pbp, away_pbp)
# Create the minutes bucket
pbp_wide = pbp_wide %>% 
  mutate(minute_bucket = ifelse(str_detect(pctimestring, "[0-9]{2}:00"), as.numeric(str_extract(pctimestring, "[0-9]+")),
                                as.numeric(str_extract(pctimestring, "[0-9]+")) + 1)) %>%
  select(-pctimestring) %>%
  distinct()
# One row for each player
pbp_long = pbp_wide %>% pivot_longer(cols = contains("player"),
                                     names_to = "player_num",
                                     values_to = "player_name") %>%
  select(-player_num)

# Proportion per minute
pbp_prop = pbp_long %>% 
  group_by(team_id, period, minute_bucket, player_name) %>%
  summarise(s = n()) %>%
  group_by(team_id, period, minute_bucket) %>%
  mutate(prop = s / sum(s)) %>%
  group_by(team_id, player_name) %>%
  mutate(total_minutes = sum(s))

team = "LAC"
pbp_plot = pbp_prop %>% filter(team_id == team) %>%
  filter(period <= 4) %>%
  mutate(time_left = 48 - 12*(period - 1) + (minute_bucket - 12))
# Add if they start or not
pbp_plot = pbp_plot %>%
  group_by(period, minute_bucket) %>%
  arrange(desc(prop)) %>%
  mutate(r = row_number()) %>%
  ungroup() %>%
  mutate(is_starter = ifelse(period == 1 & minute_bucket == 12 & r <= 5, TRUE, FALSE)) %>%
  mutate(total_minutes = ifelse(is_starter, 9999999, total_minutes))

# Create a temp table so every player is in every row
players = unique(pbp_plot$player_name)
period = rep(1:4, length(players))
minute_bucket = rep(1:12, length(players))

temp_df = expand.grid(period = period, minute_bucket = minute_bucket, player_name = players,
                      stringsAsFactors = FALSE) %>%
  distinct() %>%
  mutate(time_left = 48 - 12*(period - 1) + (minute_bucket - 12),
         team_id = team)

# Join onto temp table
pbp_plot = left_join(temp_df, pbp_plot, by = c('period', 'minute_bucket', 'time_left', 'player_name', 'team_id'))
pbp_plot[is.na(pbp_plot)] = 0
pbp_plot = pbp_plot %>% arrange(desc(total_minutes))

facet.labs <- c("Q1", "Q2", "Q3", "Q4")
names(facet.labs) <- c("1", "2", "3", "4")

ggplot(pbp_plot, aes(x = minute_bucket, y = reorder(player_name, total_minutes), fill = prop)) +
  geom_raster() +
  geom_tile(fill = NA, size = .5) +
  scale_x_reverse(breaks = c(12, 6, 0)) +
  facet_grid(.~period, labeller = labeller(period = facet.labs)) +
  scale_fill_gradient(low = "white", high = "#E03A3E") +
  theme_minimal() +
  theme(text = element_text(family = "Roboto Condensed"),
        title = element_text(size = 14),
        plot.subtitle = element_text(size = 13),
        plot.caption = element_text(size = 10),
        axis.title = element_text(size = 14),
        axis.text = element_text(size = 12),
#        axis.text.x = element_text(angle = 0, hjust = 0, vjust = 1),
        legend.text = element_text(size = 14),
        panel.grid.minor.x = element_blank(),
        legend.position = "none",
        # For facet spacing
        panel.spacing = unit(.01, "lines"),
        panel.grid.major = element_blank(), 
        panel.grid.minor = element_blank(),
        panel.background = element_blank()) +
    labs(
      title = paste0("2019-2020 ", team, " Lineup Rotations"),
      subtitle = "Pre Hood Injury",
      x = "",
      y = "",
      caption = glue::glue("As of 12/26/19",
                           "\nRough exclusion of garbage time")
    )