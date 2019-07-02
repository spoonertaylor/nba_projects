# PURPOSE: Edit positional data to include position based on minutes played
# Plot position changes over time
library(tidyverse)
# * DATA ----
positional_estimates = read.csv('nba_projects/data/nba/basketball_reference/player_data/positional_estimates/player_position_estimates.csv',
                                stringsAsFactors = FALSE)

# positional_estimates = positional_estimates %>%
#   mutate(position_minutes = dplyr::case_when(
#     pmax(minutes_pg, minutes_sg, minutes_sf, minutes_pf, minutes_c) == minutes_pg ~ 'PG',
#     pmax(minutes_pg, minutes_sg, minutes_sf, minutes_pf, minutes_c) == minutes_sg ~ 'SG',
#     pmax(minutes_pg, minutes_sg, minutes_sf, minutes_pf, minutes_c) == minutes_sf ~ 'SF',
#     pmax(minutes_pg, minutes_sg, minutes_sf, minutes_pf, minutes_c) == minutes_pf ~ 'PF',
#     pmax(minutes_pg, minutes_sg, minutes_sf, minutes_pf, minutes_c) == minutes_c ~ 'C'
#   )) %>%
#   mutate(position_numeric = 1*prop_pg + 2*prop_sg + 3*prop_sf + 4*prop_pf + 5*prop_c)

player_table = read.csv('nba_projects/data/player_ids/player_table.csv', stringsAsFactors = FALSE)

positional_estimates = left_join(positional_estimates, player_table, by = 'bbref_id')

larg_var = positional_estimates %>% group_by(bbref_id) %>% summarise(pos_var = var(position_numeric), seasons = length(unique(season)), max_season = max(season)) %>%
  arrange(desc(pos_var))

# * EDA ----
# Look at a players positional arch
plot_positional_arch = function(id, min_season, max_season) {
  data_temp = positional_estimates %>% filter(bbref_id == id, season >= min_season, season <= max_season)
  data_temp = data_temp %>% group_by(season) %>% mutate(teams = row_number()) %>% mutate(max_row = max(teams)) %>%
    ungroup() %>% mutate(keep = dplyr::case_when(
      max_row == 1 ~ TRUE,
      max_row > 1 & team == 'TOT' ~ TRUE,
      TRUE ~ FALSE
    )) %>%
    filter(keep)
  p = ggplot(data_temp, aes(x = season, y = position_numeric)) + geom_line() +
    geom_point(alpha = 0.8, size = 3) +
    labs(
      title = paste0(unique(data_temp$player_name)[1], " Positional Scale Career Arch"),
      subtitle = paste0(min(data_temp$season), "-", max(data_temp$season)),
      caption = glue::glue("
                   Data: basketball-reference.com Positional Estimates
                   By: @spoonertaylor, @chrisfellertwtr
                   "),
      x = "",
      y = "Positional Scale"
    ) +
    scale_x_continuous(breaks = min_season:max_season, labels = min_season:max_season) +
    ylim(.5, 5) +
    theme_minimal() +
    theme(text = element_text(family = "Roboto Condensed"),
          title = element_text(size = 18),
          plot.subtitle = element_text(size = 16),
          plot.caption = element_text(size = 10),
          axis.title = element_text(size = 14),
          axis.text = element_text(size = 12),
          panel.grid.minor.x = element_blank())
  return(p)
}

p = plot_positional_arch('antetgi01', 2004, 2019)

p + ggforce::geom_mark_circle(aes(filter = season == 2016, label = "Point Giannis",
                                    description = paste0("In 2016 Giannis played 40% of his minutes at PG ",
                                                         "and 59% of his minutes at SG. His AST% went from 13% to 20% and ",
                                                         "for the first time in his career had a positive OBPM... But lead the NBA in fouls.")), 
                                label.family = "Roboto Condensed", label.fontsize = c(14, 9)) +
  ggforce::geom_mark_circle(aes(filter = season == 2019, label = "MVP Giannis",
                                description = paste0("Along with having career highs in almost every statistical field, ",
                                                     "Giannis increased his minutes at C from 7% in 2018 ",
                                                     " to 27% in 2019. ")), 
                            label.family = "Roboto Condensed", label.fontsize = c(14, 9))


p = plot_positional_arch('hardeja01', 2004, 2019)

p + ggforce::geom_mark_circle(aes(filter = season == 2012, label = "Last Bit of Thunder",
                                  description = paste0("In Harden's last year in OKC he only started 2 of the 62 games he played in ",
                                                       " but had the best OBPM of the Thunder's Big 3 with a USG rate 10% less then his star teammates.")), 
                              label.family = "Roboto Condensed", label.fontsize = c(14, 9)) +
  ggforce::geom_mark_circle(aes(filter = season == 2017, label = "Is Harden a Point Guard?",
                                description = paste0("Harden played 98% of his minutes at PG for HOU with Tyler Ennis and Patrick Beverley (for part of the season) ",
                                                     " being the only other PG's on the team. His USG rate was a career high (at the time) 34% as he lead the league ",
                                                     " in win shares. ")), 
                            label.family = "Roboto Condensed", label.fontsize = c(14, 9)) +
  ggrepel::geom_text_repel(data = positional_estimates %>%
                             filter(season == 2018, bbref_id == 'hardeja01'),
                           aes(label = "Welcome Chris Paul", family = "Roboto Condensed"),
                           seed = 23, size = 5, 
                           min.segment.length = 0, segment.color = "black",
                           point.padding = 0.5)


# Group by unique positions and get the average proportion
avg_prop = positional_estimates %>% filter(team != 'TOT') %>%
  group_by(season, position) %>%
  summarise(n = n(),
            prop_pg = mean(prop_pg),
            prop_sg = mean(prop_sg),
            prop_sf = mean(prop_sf),
            prop_pf = mean(prop_pf),
            prop_c = mean(prop_c)) 

avg_prop_long = reshape2::melt(avg_prop %>% select(position, starts_with('prop')),
                                  id.vars = c('season','position'),
                                  measure.vars = c('prop_pg', 'prop_sg', 'prop_sf', 'prop_pf', 'prop_c'),
                                  variable.name = 'position_played',
                                  value.name = 'prop') %>%
                  mutate(position_played = stringr::str_remove(position_played, 'prop_')) %>%
                  mutate(position_played = factor(position_played, levels = c('pg', 'sg', 'sf', 'pf', 'c'))) %>%
                  mutate(position = factor(position, levels = c('C', 'PF', 'SF', 'SG', 'PG')))

ggplot(avg_prop_long %>% filter(season >= 2004), aes(x = position_played, y = prop)) + geom_col() +
  facet_wrap(.~position) +
  gganimate::transition_states(season, transition_length=1, state_length=4) +
  gganimate::enter_fade() + 
  gganimate::exit_shrink() +
  gganimate::ease_aes("sine-in-out") +
  labs(
    title = "Average Distribution of Minutes by Primary Position",
    subtitle = "{closest_state}",
    caption = glue::glue("
                         Data: basketball-reference.com Positional Estimates
                         By: @spoonertaylor, @chrisfellertwtr
                         "),
    x = "",
    y = "Average Proportion of Minutes Played"
    ) +
  scale_x_discrete(labels = c("PG", "SG", "SF", "PF", "C")) +
  theme_minimal() +
  theme(text = element_text(family = "Roboto Condensed"),
        title = element_text(size = 18),
        plot.subtitle = element_text(size = 16),
        plot.caption = element_text(size = 10),
        axis.title = element_text(size = 14),
        axis.text = element_text(size = 12),
        panel.grid.minor.x = element_blank()) -> pos_plot

anim = animate(pos_plot)

anim_save("nba_projects/position_change.gif", anim)


ggplot(positional_estimates %>% filter(season >= 2004, minutes_played >= 750), aes(x = position_numeric)) + geom_histogram() +
  facet_wrap(~season) + 
  labs(
    subtitle = "MIN >= 750",
    x = "",
    y = ""
  )
