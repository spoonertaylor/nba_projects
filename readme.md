### An NBA Project Has No Name
---


#### analytics/
**One-off in-depth analyses**
- draft_pick_trends/
    - `draft_pick_position_trends.py`
    - `readme.md`
    - Description: Analysis of pick totals by position (as definied by RealGM) since one-and-done era began (2006-2019).

#### data/
**Flat files**
- nba/
    - basketball_reference/
        - draft/
            - `draft_selections.csv`
        - league_data/
            - expanded_standings/
                - `expanded_standings.csv`
                - `data_dictionary.xlsx`
            - league_averages/
                - combined/
                    - `bbref_league_data.csv` (all league data combined)
                - miscellaneous/
                    - `league_average_miscellaneous_stats.csv`
                    - `data_dictionary.xlsx`
                - per_game/
                    - `per_game.csv`
                    - `data_dictionary.xlsx`
                - per100_poss/
                    - `per100_poss.csv`
                    - `data_dictionary.xlsx`
                - team_shooting/
                    - `league_average_team_shooting.csv`
                    - `data_dictionary.xlsx`
        - player_data/
            - advanced/
                - `advanced.csv`
                - `data_dictionary.xlsx`
            - combined/
                - `bbref_player_data.csv` (all player data combined)
            - per100_poss/
                - `per100_poss.csv`
                - `data_dictionary.xlsx`
            - positional_estimates/
                - `player_position_estimates.csv`
            - salary/
                - `salary_info.csv`
            - totals/
                - `totals.csv`
                - `data_dictionary.xlsx`
        - team_data/
            - combined/
                - `bbref_team_data.csv` (all team data combined)
            - miscellaneous/
                - `miscellaneous_stats.csv`
                - `data_dictionary.xlsx`
            - opp_per100_poss/
                - `opp_per100_poss.csv`
                - `data_dictionary.xlsx`
            - opp_shooting/
                - `opp_shooting.csv`
                - `data_dictionary.xlsx`
            - per100_poss/
                - `per100_poss.csv`
                - `data_dictionary.xlsx`
            - team_ratings/
                - `team_ratings.csv`
                - `data_dictionary.xlsx`
            - team_shooting/
                - `team_shooting.csv`
                - `data_dictionary.xlsx`
    - espn/
        - `espn_nba_rpm.csv`
    - real_gm/
        - `draft_selections.csv`

- ncaa/
    - sports_reference/
        - player_data/
            - advanced/
                - `advanced.csv`
            - per40_min/
                - `per40_min.csv`
            - per100_poss/
                - `per100_poss.csv`

- player_ids/
    - `player_table.csv`

#### Data Scraping
**Scraping Scripts**
- basketball_reference/
    - `basketball_reference_scraper.py`
    - `player_positional_estimates.R`
    - `salary_info.R`
    - `years_in_college.R`
- espn/
    - `esnp_rpm_number.R`
    - `espn_rpm_number.R`
- ids/
    - `bbref_player_id.R`
    - `espn_player_id.R`
    - `get_player_ids.R`
    - `sports_ref_player_id.R`
- sports_reference/
    - `sports_reference_scraper.py`

#### Modeling
**Models**
- college_position_clustering/
- target_metric/
    - `target_metric.py`
- target_selection/
    - `target_selection.py`
    - `example_plots.py`
    - `readme.md`

#### Reporting
-
