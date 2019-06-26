# Project: Basketball-Reference Scraping
# Project Track: Data Scraping
# Description: Scrape team and individual tables from Basketball-Reference.com
# between the 2004-2005 and 2018-2019 seasons. Scrape NBA Draft table between
# 2005 and 2019
# Data Sources: Basketball-Reference
# Last Updated: 5/23/2019

import numpy as np
import pandas as pd
import requests
from time import sleep
from bs4 import BeautifulSoup as BS

def scrape_per_100_possessions(save=False):
    """
    Scrape Per 100 Possession table within NBA Season Summary Page on
    Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        historical_per_100_possessions_df (DataFrame): Per 100 Possession table
        between 2004-2005 and 2018-2019 NBA seasons.
    """
    historical_per_100_possessions_df = pd.DataFrame()
    for season in np.arange(2005, 2020):
        sleep(np.random.randint(10, 15))
        season_per_100_df = pd.DataFrame()
        url = 'https://www.basketball-reference.com/leagues/NBA_{}.html#team-stats-per_poss::none'.format(season)
        html = requests.get(url).text
        soup = BS(html, 'html.parser')
        placeholders = soup.find_all('div', {'class': 'placeholder'})
        for x in placeholders:
            comment = ''.join(x.next_siblings)
            soup_comment = BS(comment, 'html.parser')
            tables = soup_comment.find_all('table', attrs={"id":"team-stats-per_poss"})
            for tag in tables:
                df = pd.read_html(tag.prettify())[0]
                season_per_100_df = season_per_100_df.append(df).reset_index()
                season_per_100_df.drop('index', axis=1, inplace=True)
                season_per_100_df.columns = ['RANK', 'TEAM', 'G', 'MP'] + \
                                            ['PER100_' + str(col) for col in \
                                            season_per_100_df.columns if col not in \
                                            ['Rk', 'Team', 'G', 'MP']]
        season_per_100_df['SEASON'] = '{0}-{1}'.format(season-1, season)
        season_per_100_df['PLAYOFF_TEAM'] = np.where(season_per_100_df['TEAM'].str.find('*') > -1, 1, 0)
        season_per_100_df['TEAM'] = season_per_100_df['TEAM'].str.strip(' * ')
        historical_per_100_possessions_df = historical_per_100_possessions_df.append(season_per_100_df, sort=False)
    column_order = ['RANK', 'SEASON', 'TEAM', 'PLAYOFF_TEAM', 'G', 'MP', 'PER100_FG',
                    'PER100_FGA', 'PER100_FG%', 'PER100_3P', 'PER100_3PA',
                    'PER100_3P%', 'PER100_2P', 'PER100_2PA', 'PER100_2P%',
                    'PER100_FT', 'PER100_FTA', 'PER100_FT%', 'PER100_ORB',
                    'PER100_DRB', 'PER100_TRB', 'PER100_AST', 'PER100_STL',
                    'PER100_BLK', 'PER100_TOV', 'PER100_PF', 'PER100_PTS']
    historical_per_100_possessions_df = historical_per_100_possessions_df.reindex(columns=column_order)
    if save:
        parent_directory = '../../data/nba/basketball_reference/team_data/per100_poss/'
        historical_per_100_possessions_df.to_csv(parent_directory +
                                                'per100_poss.csv',
                                                index=False)
    else:
        pass
    return historical_per_100_possessions_df

def scrape_opponent_per_100_possessions(save=False):
    """
    Scrape Opponent Per 100 Possession table within NBA Season Summary Page on
    Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        historical_opponent_per_100_df (DataFrame): Opponent Per 100 Possession
        table between 2004-2005 and 2018-2019 NBA seasons.
    """
    historical_opponent_per_100_df = pd.DataFrame()
    for season in np.arange(2005, 2020):
        sleep(np.random.randint(10, 15))
        season_opponent_per_100_df = pd.DataFrame()
        url = 'https://www.basketball-reference.com/leagues/NBA_{0}.html#opponent-stats-per_poss::none'.format(season)
        html = requests.get(url).text
        soup = BS(html, 'html.parser')
        placeholders = soup.find_all('div', {'class': 'placeholder'})
        for x in placeholders:
            comment = ''.join(x.next_siblings)
            soup_comment = BS(comment, 'html.parser')
            tables = soup_comment.find_all('table', attrs={"id":"opponent-stats-per_poss"})
            for tag in tables:
                df = pd.read_html(tag.prettify())[0]
                season_opponent_per_100_df = season_opponent_per_100_df.append(df).reset_index()
                season_opponent_per_100_df.drop('index', axis=1, inplace=True)
                season_opponent_per_100_df.columns = ['RANK', 'TEAM', 'G', 'MP'] + \
                                                    ['OPP_PER100_' + str(col) for \
                                                    col in season_opponent_per_100_df.columns \
                                                    if col not in ['Rk', 'Team', 'G', 'MP']]
        season_opponent_per_100_df['SEASON'] = '{0}-{1}'.format(season-1, season)
        season_opponent_per_100_df['PLAYOFF_TEAM'] = np.where(season_opponent_per_100_df['TEAM'].str.find('*') > -1, 1, 0)
        season_opponent_per_100_df['TEAM'] = season_opponent_per_100_df['TEAM'].str.strip(' * ')
        historical_opponent_per_100_df = historical_opponent_per_100_df.append(season_opponent_per_100_df, sort=False)
    column_order = ['RANK', 'SEASON', 'TEAM', 'PLAYOFF_TEAM', 'G', 'MP',
                    'OPP_PER100_FG', 'OPP_PER100_FGA', 'OPP_PER100_FG%',
                    'OPP_PER100_3P', 'OPP_PER100_3PA', 'OPP_PER100_3P%',
                    'OPP_PER100_2P', 'OPP_PER100_2PA', 'OPP_PER100_2P%',
                    'OPP_PER100_FT', 'OPP_PER100_FTA', 'OPP_PER100_FT%',
                    'OPP_PER100_ORB', 'OPP_PER100_DRB', 'OPP_PER100_TRB',
                    'OPP_PER100_AST', 'OPP_PER100_STL', 'OPP_PER100_BLK',
                    'OPP_PER100_TOV', 'OPP_PER100_PF', 'OPP_PER100_PTS']
    historical_opponent_per_100_df = historical_opponent_per_100_df.reindex(columns=column_order)
    if save:
        parent_directory = '../../data/nba/basketball_reference/team_data/opp_per100_poss/'
        historical_opponent_per_100_df.to_csv(parent_directory +
                                            'opp_per100_poss.csv',
                                            index=False)
    else:
        pass
    return historical_opponent_per_100_df

def scrape_team_shooting(save=False):
    """
    Scrape Team Shooting table within NBA Season Summary Page on
    Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        historical_team_shooting_df (DataFrame): Team Shooting table between
        2004-2005 and 2018-2019 NBA seasons.
        league_average_team_shooting_df (DataFrame): League Average Team Shooting
        between 2004-2005 and 2018-2019 seasons.
    """
    historical_team_shooting_df = pd.DataFrame()
    league_average_team_shooting_df = pd.DataFrame()
    for season in np.arange(2005, 2020):
        sleep(np.random.randint(10, 15))
        season_team_shooting_df = pd.DataFrame()
        url = 'https://www.basketball-reference.com/leagues/NBA_{0}.html#team_shooting::none'.format(season)
        html = requests.get(url).text
        soup = BS(html, 'html.parser')
        placeholders = soup.find_all('div', {'class': 'placeholder'})
        for x in placeholders:
            comment = ''.join(x.next_siblings)
            soup_comment = BS(comment, 'html.parser')
            tables = soup_comment.find_all('table', attrs={"id":"team_shooting"})
            for tag in tables:
                df = pd.read_html(tag.prettify())[0]
                season_team_shooting_df = season_team_shooting_df.append(df).reset_index()
                season_team_shooting_df.columns = season_team_shooting_df.columns.get_level_values(1)
                season_team_shooting_df.drop('', axis=1, inplace=True)
                season_team_shooting_df.columns = ['RANK', 'TEAM', 'G', 'MP',
                                                   'FG%', 'AVERAGE_DISTANCE',
                                                   '%FGA_2P', '%FGA_0-3',
                                                   '%FGA_3-10', '%FGA_10-16',
                                                   'FGA_16-3PT', '%FGA_3P',
                                                   'FG%_2P', 'FG%_0-3', 'FG%_3-10',
                                                   'FG%_10-16', 'FG%_16-3PT',
                                                   'FG%_3P', '%ASTD_2P', '%FGA_DUNKS',
                                                   'DUNKS_MADE', '%FGA_LAYUPS',
                                                   'LAYUPS_MADE', '%ASTD_3P',
                                                   '%FGA3P_CORNER', 'FG%3_CORNER',
                                                   'HEAVE_ATTEMPTS', 'HEAVE_MAKES']
        season_team_shooting_df['SEASON'] = '{0}-{1}'.format(season-1, season)
        season_team_shooting_df['PLAYOFF_TEAM'] = np.where(season_team_shooting_df['TEAM'].str.find('*') > -1, 1, 0)
        season_team_shooting_df['TEAM'] = season_team_shooting_df['TEAM'].str.strip(' * ')
        season_average_team_shooting_df = season_team_shooting_df[season_team_shooting_df['TEAM']=='League Average']
        season_team_shooting_df = season_team_shooting_df[season_team_shooting_df['TEAM']!='League Average']
        league_average_team_shooting_df = league_average_team_shooting_df.append(season_average_team_shooting_df, sort=False)
        historical_team_shooting_df = historical_team_shooting_df.append(season_team_shooting_df, sort=False)
    column_order = ['RANK', 'SEASON', 'TEAM', 'PLAYOFF_TEAM', 'G', 'MP', 'FG%',
                    'AVERAGE_DISTANCE', '%FGA_2P', '%FGA_0-3', '%FGA_3-10',
                    '%FGA_10-16', 'FGA_16-3PT', '%FGA_3P', 'FG%_2P', 'FG%_0-3',
                    'FG%_3-10', 'FG%_10-16', 'FG%_16-3PT', 'FG%_3P',
                    '%ASTD_2P', '%FGA_DUNKS', 'DUNKS_MADE', '%FGA_LAYUPS',
                    'LAYUPS_MADE', '%ASTD_3P', '%FGA3P_CORNER', 'FG%3_CORNER',
                    'HEAVE_ATTEMPTS', 'HEAVE_MAKES']
    league_average_team_shooting_df = league_average_team_shooting_df.reindex(columns=column_order)
    historical_team_shooting_df = historical_team_shooting_df.reindex(columns=column_order)
    if save:
        parent_directory = '../../data/nba/basketball_reference/team_data/team_shooting/'
        historical_team_shooting_df.to_csv(parent_directory +
                                          'team_shooting.csv',
                                          index=False)
        league_average_team_shooting_df.to_csv('../../data/nba/basketball_reference/league_data/league_averages/team_shooting/league_average_team_shooting.csv',
                                              index=False)
    else:
        pass
    return historical_team_shooting_df, league_average_team_shooting_df

def scrape_opponent_shooting(save=False):
    """
    Scrape Opponent Team Shooting table within NBA Season Summary Page on
    Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        historical_opponent_shooting_df (DataFrame): Opponent Team Shooting
        table between 2004-2005 and 2018-2019 NBA seasons.
    """
    historical_opponent_shooting_df = pd.DataFrame()
    for season in np.arange(2005, 2020):
        sleep(np.random.randint(10, 15))
        season_opponent_shooting_df = pd.DataFrame()
        url = 'https://www.basketball-reference.com/leagues/NBA_{0}.html#opponent_shooting::none'.format(season)
        html = requests.get(url).text
        soup = BS(html, 'html.parser')
        placeholders = soup.find_all('div', {'class': 'placeholder'})
        for x in placeholders:
            comment = ''.join(x.next_siblings)
            soup_comment = BS(comment, 'html.parser')
            tables = soup_comment.find_all('table', attrs={"id":"opponent_shooting"})
            for tag in tables:
                df = pd.read_html(tag.prettify())[0]
                season_opponent_shooting_df = season_opponent_shooting_df.append(df).reset_index()
                season_opponent_shooting_df.columns = season_opponent_shooting_df.columns.get_level_values(1)
                season_opponent_shooting_df.drop('', axis=1, inplace=True)
                season_opponent_shooting_df.columns = ['RANK', 'TEAM', 'G', 'MP',
                                                       'OPP_FG%', 'OPP_AVERAGE_DISTANCE',
                                                       'OPP_%FGA_2P', 'OPP_%FGA_0-3',
                                                       'OPP_%FGA_3-10', 'OPP_%FGA_10-16',
                                                       'OPP_FGA_16-3PT', 'OPP_%FGA_3P',
                                                       'OPP_FG%_2P', 'OPP_FG%_0-3',
                                                       'OPP_FG%_3-10', 'OPP_FG%_10-16',
                                                       'OPP_FG%_16-3PT', 'OPP_FG%_3P',
                                                       'OPP_%ASTD_2P', 'OPP_%FGA_DUNKS',
                                                       'OPP_DUNKS_MADE', 'OPP_%FGA_LAYUPS',
                                                       'OPP_LAYUPS_MADE', 'OPP_%ASTD_3P',
                                                       'OPP_%FGA3P_CORNER', 'OPP_FG%3_CORNER']
        season_opponent_shooting_df['SEASON'] = '{0}-{1}'.format(season-1, season)
        season_opponent_shooting_df['PLAYOFF_TEAM'] = np.where(season_opponent_shooting_df['TEAM'].str.find('*') > -1, 1, 0)
        season_opponent_shooting_df['TEAM'] = season_opponent_shooting_df['TEAM'].str.strip(' * ')
        season_opponent_shooting_df = season_opponent_shooting_df[season_opponent_shooting_df['TEAM']!='League Average']
        historical_opponent_shooting_df = historical_opponent_shooting_df.append(season_opponent_shooting_df, sort=False)
    column_order = ['RANK', 'SEASON', 'TEAM', 'PLAYOFF_TEAM', 'G', 'MP', 'OPP_FG%',
                    'OPP_AVERAGE_DISTANCE', 'OPP_%FGA_2P', 'OPP_%FGA_0-3',
                    'OPP_%FGA_3-10', 'OPP_%FGA_10-16', 'OPP_FGA_16-3PT',
                    'OPP_%FGA_3P', 'OPP_FG%_2P', 'OPP_FG%_0-3', 'OPP_FG%_3-10',
                    'OPP_FG%_10-16', 'OPP_FG%_16-3PT', 'OPP_FG%_3P',
                    'OPP_%ASTD_2P', 'OPP_%FGA_DUNKS', 'OPP_DUNKS_MADE',
                    'OPP_%FGA_LAYUPS', 'OPP_LAYUPS_MADE', 'OPP_%ASTD_3P',
                    'OPP_%FGA3P_CORNER', 'OPP_FG%3_CORNER']
    historical_opponent_shooting_df = historical_opponent_shooting_df.reindex(columns=column_order)
    if save:
        parent_directory = '../../data/nba/basketball_reference/team_data/opp_shooting/'
        historical_opponent_shooting_df.to_csv(parent_directory +
                                              'opponent_shooting.csv',
                                              index=False)
    else:
        pass
    return historical_opponent_shooting_df

def scrape_miscellaneous_stats(save=False):
    """
    Scrape Miscellaneous Stats table within NBA Season Summary Page on
    Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        historical_misc_stats_df (DataFrame): Miscellaneous Stats table between
        2004-2005 and 2018-2019 NBA seasons.
        league_average_misc_stats_df  (DataFrame): League Average Miscellaneous
        Stats between 2004-2005 and 2018-2019 season.
    """
    historical_misc_stats_df = pd.DataFrame()
    league_average_misc_stats_df = pd.DataFrame()
    for season in np.arange(2005, 2020):
        sleep(np.random.randint(10, 15))
        season_misc_stats_df = pd.DataFrame()
        url = 'https://www.basketball-reference.com/leagues/NBA_{0}.html#misc_stats::none'.format(season)
        html = requests.get(url).text
        soup = BS(html, 'html.parser')
        placeholders = soup.find_all('div', {'class': 'placeholder'})
        for x in placeholders:
            comment = ''.join(x.next_siblings)
            soup_comment = BS(comment, 'html.parser')
            tables = soup_comment.find_all('table', attrs={"id":"misc_stats"})
            for tag in tables:
                df = pd.read_html(tag.prettify())[0]
                season_misc_stats_df = season_misc_stats_df.append(df).reset_index()
                season_misc_stats_df.columns = season_misc_stats_df.columns.get_level_values(1)
                season_misc_stats_df.drop('', axis=1, inplace=True)
                season_misc_stats_df.columns = ['RANK', 'TEAM', 'AVERAGE_AGE',
                                                'W', 'L', 'PW', 'PL', 'MOV',
                                                'SOS', 'SRS', 'ORTG', 'DRTG',
                                                'NRTG', 'PACE', 'FT_RATE',
                                                '3PA_RATE', 'TS%', 'OFFENSIVE_EFG%',
                                                'OFFENSIVE_TOV%', 'OFFENSIVE_ORB%',
                                                'OFFENSIVE_FT/FGA', 'DEFENSIVE_eFG%',
                                                'DEFENSIVE_TOV%', 'DEFENSIVE_DRB%',
                                                'DEFENSIVE_FT/FGA', 'ARENA',
                                                'TOTAL_ATTENDANCE', 'ATTENDANCE/G']
        season_misc_stats_df['SEASON'] = '{0}-{1}'.format(season-1, season)
        season_misc_stats_df['PLAYOFF_TEAM'] = np.where(season_misc_stats_df['TEAM'].str.find('*') > -1, 1, 0)
        season_misc_stats_df['TEAM'] = season_misc_stats_df['TEAM'].str.strip(' * ')
        season_misc_stats_df['W/L%'] = season_misc_stats_df['W']/(season_misc_stats_df['W'] + season_misc_stats_df['L'])
        season_average_misc_stats_df = season_misc_stats_df[season_misc_stats_df['TEAM']=='League Average']
        season_misc_stats_df = season_misc_stats_df[season_misc_stats_df['TEAM']!='League Average']
        league_average_misc_stats_df = league_average_misc_stats_df.append(season_average_misc_stats_df, sort=False)
        historical_misc_stats_df = historical_misc_stats_df.append(season_misc_stats_df, sort=False)
    column_order = ['RANK', 'SEASON', 'TEAM', 'PLAYOFF_TEAM', 'AVERAGE_AGE',
                    'W', 'L', 'W/L%', 'PW', 'PL', 'MOV', 'SOS', 'SRS', 'ORTG',
                    'DRTG', 'NRTG', 'PACE', 'FT_RATE', '3PA_RATE', 'TS%',
                    'OFFENSIVE_EFG%', 'OFFENSIVE_TOV%', 'OFFENSIVE_ORB%',
                    'OFFENSIVE_FT/FGA', 'DEFENSIVE_eFG%', 'DEFENSIVE_TOV%',
                    'DEFENSIVE_DRB%', 'DEFENSIVE_FT/FGA', 'ARENA',
                    'TOTAL_ATTENDANCE', 'ATTENDANCE/G']
    league_average_misc_stats_df = league_average_misc_stats_df.reindex(columns=column_order)
    historical_misc_stats_df = historical_misc_stats_df.reindex(columns=column_order)
    if save:
        parent_directory = '../../data/nba/basketball_reference/team_data/miscellaneous/'
        historical_misc_stats_df.to_csv(parent_directory +
                                        'miscellaneous_stats.csv',
                                        index=False)
        league_average_misc_stats_df.to_csv('../../data/nba/basketball_reference/league_data/league_averages/miscellaneous/league_average_miscellaneous_stats.csv',
                                            index=False)
    else:
        pass
    return historical_misc_stats_df, league_average_misc_stats_df

def scrape_player_per_100_possessions(save=False):
    """
    Scrape Player Per 100 Possession table within NBA Season Summary Page on
    Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        historical_player_per_100_poss_df (DataFrame): Player Per 100 Possession
        table between 2004-2005 and 2018-2019 NBA seasons.
    """
    historical_player_per_100_poss_df = pd.DataFrame()
    for season in np.arange(2005, 2020):
        sleep(np.random.randint(10, 15))
        url = 'https://www.basketball-reference.com/leagues/NBA_{0}_per_poss.html#per_poss_stats::none'.format(season)
        season_player_per_100_poss_df = pd.read_html(url)[0]
        season_player_per_100_poss_df.drop('Unnamed: 29', axis=1, inplace=True)
        season_player_per_100_poss_df.columns = ['RANK', 'PLAYER', 'POSITION', 'AGE', 'TEAM', 'G', 'GS', 'MP'] + \
                                    ['PER100_' + str(col) for col in \
                                    season_player_per_100_poss_df.columns if col not in \
                                    ['Rk', 'Player', 'Pos', 'Age', 'Tm', 'G', 'GS', 'MP']]
        season_player_per_100_poss_df = season_player_per_100_poss_df[season_player_per_100_poss_df['RANK']!='Rk']
        season_player_per_100_poss_df['SEASON'] = '{0}-{1}'.format(season-1, season)
        historical_player_per_100_poss_df = historical_player_per_100_poss_df.append(season_player_per_100_poss_df, sort=False)
    column_order = ['RANK', 'PLAYER', 'SEASON', 'POSITION', 'AGE', 'TEAM', 'G', 'GS', 'MP',
       'PER100_FG', 'PER100_FGA', 'PER100_FG%', 'PER100_3P', 'PER100_3PA',
       'PER100_3P%', 'PER100_2P', 'PER100_2PA', 'PER100_2P%', 'PER100_FT',
       'PER100_FTA', 'PER100_FT%', 'PER100_ORB', 'PER100_DRB', 'PER100_TRB',
       'PER100_AST', 'PER100_STL', 'PER100_BLK', 'PER100_TOV', 'PER100_PF',
       'PER100_PTS', 'PER100_ORtg', 'PER100_DRtg']
    historical_player_per_100_poss_df = historical_player_per_100_poss_df.reindex(columns=column_order)
    dtype = {'RANK':'object', 'PLAYER':'object', 'SEASON':'object', 'POSITION':'object',
            'AGE':'int64', 'TEAM':'object', 'G':'int64', 'GS':'int64', 'MP':'int64',
            'PER100_FG':'float64', 'PER100_FGA':'float64', 'PER100_FG%':'float64',
            'PER100_3P':'float64', 'PER100_3PA':'float64', 'PER100_3P%':'float64',
            'PER100_2P':'float64', 'PER100_2PA':'float64', 'PER100_2P%':'float64',
            'PER100_FT':'float64', 'PER100_FTA':'float64', 'PER100_FT%':'float64',
            'PER100_ORB':'float64', 'PER100_DRB':'float64', 'PER100_TRB':'float64',
            'PER100_AST':'float64', 'PER100_STL':'float64', 'PER100_BLK':'float64',
            'PER100_TOV':'float64', 'PER100_PF':'float64', 'PER100_PTS':'float64',
            'PER100_ORtg':'float64', 'PER100_DRtg':'float64'}
    historical_player_per_100_poss_df = historical_player_per_100_poss_df.astype(dtype)
    if save:
        parent_directory = '../../data/nba/basketball_reference/player_data/per100_poss/'
        historical_player_per_100_poss_df.to_csv(parent_directory +
                                              'per100_poss.csv',
                                              index=False)
    else:
        pass
    return historical_player_per_100_poss_df

def scrape_player_advanced_stats(save=False):
    """
    Scrape Player Advanced Stats table within NBA Season Summary Page on
    Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        historical_player_per_100_poss_df (DataFrame): Player Advanced Stats
        table between 2004-2005 and 2018-2019 NBA seasons.
    """
    historical_player_advanced_df = pd.DataFrame()
    for season in np.arange(2005, 2020):
        sleep(np.random.randint(10, 15))
        url = 'https://www.basketball-reference.com/leagues/NBA_{0}_advanced.html#advanced_stats::none'.format(season)
        season_player_advanced_df = pd.read_html(url)[0]
        season_player_advanced_df.drop(['Unnamed: 19', 'Unnamed: 24'], axis=1, inplace=True)
        season_player_advanced_df.columns = ['RANK', 'PLAYER', 'POSITION', 'AGE',
                                             'TEAM', 'G', 'MP', 'PER', 'TS%', '3PA_RATE',
                                             'FT_RATE', 'ORB%', 'DRB%', 'TRB%', 'AST%',
                                             'STL%', 'BLK%', 'TOV%', 'USG%',
                                             'OWS', 'DWS', 'WS', 'WS/48', 'OBPM',
                                             'DBPM', 'BPM', 'VORP']
        season_player_advanced_df = season_player_advanced_df[season_player_advanced_df['RANK']!='Rk']
        season_player_advanced_df['SEASON'] = '{0}-{1}'.format(season-1, season)
        historical_player_advanced_df = historical_player_advanced_df.append(season_player_advanced_df, sort=False)
    column_order = ['RANK', 'PLAYER', 'SEASON', 'POSITION', 'AGE', 'TEAM', 'G',
                    'MP', 'PER', 'TS%', '3PA_RATE', 'FT_RATE', 'ORB%', 'DRB%',
                    'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'OWS', 'DWS',
                    'WS', 'WS/48', 'OBPM', 'DBPM', 'BPM', 'VORP']
    historical_player_advanced_df = historical_player_advanced_df.reindex(columns=column_order)
    dtype = {'RANK':'object', 'PLAYER':'object', 'SEASON':'object', 'POSITION':'object',
             'AGE':'int64', 'TEAM':'object', 'G':'int64', 'MP':'int64', 'PER':'float64',
             'TS%':'float64', '3PA_RATE':'float64', 'FT_RATE':'float64', 'ORB%':'float64',
             'DRB%':'float64', 'TRB%':'float64', 'AST%':'float64', 'STL%':'float64',
             'BLK%':'float64', 'TOV%':'float64', 'USG%':'float64', 'OWS':'float64',
             'DWS':'float64', 'WS':'float64', 'WS/48':'float64', 'OBPM':'float64',
             'DBPM':'float64', 'BPM':'float64', 'VORP':'float64'}
    historical_player_advanced_df = historical_player_advanced_df.astype(dtype)
    if save:
        parent_directory = '../../data/nba/basketball_reference/player_data/advanced/'
        historical_player_advanced_df.to_csv(parent_directory +
                                              'advanced.csv',
                                              index=False)
    else:
        pass
    return historical_player_advanced_df

def scrape_player_total_stats(save=False):
    """
    Scrape Player Total Stats table within NBA Season Summary Page on
    Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        historical_player_totals_df (DataFrame): Player Total Stats
        table between 2004-2005 and 2018-2019 NBA seasons.
    """
    historical_player_totals_df = pd.DataFrame()
    for season in np.arange(2005, 2020):
        sleep(np.random.randint(10, 15))
        url = 'https://www.basketball-reference.com/leagues/NBA_{0}_totals.html#totals_stats::none'.format(season)
        season_player_totals_df = pd.read_html(url)[0]
        season_player_totals_df.columns = ['RANK', 'PLAYER', 'POSITION', 'AGE',
                                           'TEAM', 'G', 'GS', 'MP', 'FG', 'FGA',
                                           'FG%', '3P', '3PA', '3P%', '2P', '2PA',
                                           '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB',
                                           'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV',
                                           'PF', 'PTS']
        season_player_totals_df = season_player_totals_df[season_player_totals_df['RANK']!='Rk']
        season_player_totals_df['SEASON'] = '{0}-{1}'.format(season-1, season)
        historical_player_totals_df = historical_player_totals_df.append(season_player_totals_df, sort=False)
    column_order = ['RANK', 'PLAYER', 'SEASON', 'POSITION', 'AGE', 'TEAM', 'G',
                    'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA',
                    '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST',
                    'STL', 'BLK', 'TOV', 'PF', 'PTS']
    historical_player_totals_df = historical_player_totals_df.reindex(columns=column_order)
    dtype = {'RANK':'object', 'PLAYER':'object', 'SEASON':'object', 'POSITION':'object',
             'AGE':'int64', 'TEAM':'object', 'G':'int64', 'GS':'int64', 'MP':'int64',
             'FG':'int64', 'FGA':'int64', 'FG%':'float64', '3P':'int64', '3PA':'int64',
             '3P%':'float64', '2P':'int64', '2PA':'int64', '2P%':'float64', 'eFG%':'float64',
             'FT':'int64', 'FTA':'int64', 'FT%':'float64', 'ORB':'int64', 'DRB':'int64',
             'TRB':'int64', 'AST':'int64', 'STL':'int64', 'BLK':'int64', 'TOV':'int64',
             'PF':'int64', 'PTS':'int64'}
    historical_player_totals_df = historical_player_totals_df.astype(dtype)
    if save:
        parent_directory = '../../data/nba/basketball_reference/player_data/totals/'
        historical_player_totals_df.to_csv(parent_directory +
                                              'totals.csv',
                                              index=False)
    else:
        pass
    return historical_player_totals_df

def scrape_team_ratings(save=False):
    """
    Scrape Team Ratings table within NBA Season Summary Page on
    Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        historical_team_ratings_df (DataFrame): Team Ratings table between
        2004-2005 and 2018-2019 NBA seasons.
    """
    historical_team_ratings_df = pd.DataFrame()
    for season in np.arange(2005, 2020):
        sleep(np.random.randint(10, 15))
        url = 'https://www.basketball-reference.com/leagues/NBA_{0}_ratings.html#ratings::14'.format(season)
        season_team_ratings_df = pd.read_html(url)[0]
        season_team_ratings_df.columns = season_team_ratings_df.columns.get_level_values(1)
        season_team_ratings_df.columns = ['RANK', 'TEAM', 'CONFERENCE', 'DIVISION',
                                          'W', 'L', 'W/L%', 'MOV', 'ORTG', 'DRTG',
                                          'NRTG', 'ADJUSTED_MOV', 'ADJUSTED_ORTG',
                                          'ADJUSTED_DRTG', 'ADJUSTED_NRTG']
        season_team_ratings_df['SEASON'] = '{0}-{1}'.format(season-1, season)
        historical_team_ratings_df = historical_team_ratings_df.append(season_team_ratings_df, sort=False)
    column_order = ['RANK', 'TEAM', 'SEASON', 'CONFERENCE', 'DIVISION', 'W', 'L',
                    'W/L%', 'MOV', 'ORTG', 'DRTG', 'NRTG', 'ADJUSTED_MOV',
                    'ADJUSTED_ORTG', 'ADJUSTED_DRTG', 'ADJUSTED_NRTG']
    historical_team_ratings_df = historical_team_ratings_df.reindex(columns=column_order)
    if save:
        parent_directory = '../../data/nba/basketball_reference/team_data/team_ratings/'
        historical_team_ratings_df.to_csv(parent_directory +
                                              'team_ratings.csv',
                                              index=False)

    else:
        pass
    return historical_team_ratings_df

def scrape_per_game_league_averages(save=False):
    """
    Scrape Per Game League Averages table on Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        per_game_league_averages_df (DataFrame): Per Game League Averages table for
        seasons between 1946-1947 and 2018-2019
    """
    url = 'https://www.basketball-reference.com/leagues/NBA_stats_per_game.html#stats::none'
    per_game_league_averages_df = pd.read_html(url)[0]
    per_game_league_averages_df.columns = per_game_league_averages_df.columns.get_level_values(1)
    per_game_league_averages_df.columns = ['RANK', 'SEASON', 'LEAGUE', 'AGE', 'HEIGHT',
                                  'WEIGHT', 'G', 'MP', 'PER_GAME_FG', 'PER_GAME_FGA',
                                  'PER_GAME_3P', 'PER_GAME_3PA', 'PER_GAME_FT',
                                  'PER_GAME_FTA', 'PER_GAME_ORB', 'PER_GAME_DRB',
                                  'PER_GAME_TRB', 'PER_GAME_AST', 'PER_GAME_STL',
                                  'PER_GAME_BLK', 'PER_GAME_TOV', 'PER_GAME_PF',
                                  'PER_GAME_PTS', 'FG%', '3P%', 'FT%', 'PACE',
                                  'eFG%', 'TOV%', 'ORB%','FT/FGA', 'ORTG']
    per_game_league_averages_df = per_game_league_averages_df[(per_game_league_averages_df['RANK']!='Rk') &
                                                              (per_game_league_averages_df['RANK'].notnull())]
    dtype = {'RANK':'int64', 'SEASON':'object', 'LEAGUE':'object', 'AGE':'float64',
             'HEIGHT':'object', 'WEIGHT':'float64', 'G':'int64', 'MP':'float64',
             'PER_GAME_FG':'float64', 'PER_GAME_FGA':'float64',
             'PER_GAME_3P':'float64', 'PER_GAME_3PA':'float64',
             'PER_GAME_FT':'float64', 'PER_GAME_FTA':'float64',
             'PER_GAME_ORB':'float64', 'PER_GAME_DRB':'float64',
             'PER_GAME_TRB':'float64', 'PER_GAME_AST':'float64',
             'PER_GAME_STL':'float64', 'PER_GAME_BLK':'float64',
             'PER_GAME_TOV':'float64', 'PER_GAME_PF':'float64',
             'PER_GAME_PTS':'float64', 'FG%':'float64', '3P%':'float64',
             'FT%':'float64', 'PACE':'float64', 'eFG%':'float64', 'TOV%':'float64',
             'ORB%':'float64','FT/FGA':'float64', 'ORTG':'float64'}
    per_game_league_averages_df = per_game_league_averages_df.astype(dtype)
    per_game_league_averages_df['SEASON'] = per_game_league_averages_df['SEASON'].apply(lambda x: x[0:5] + x[0:2] + x[5:8])
    if save:
        parent_directory = '../../data/nba/basketball_reference/league_data/league_averages/per_game/'
        per_game_league_averages_df.to_csv(parent_directory +
                                              'per_game.csv',
                                              index=False)
    else:
        pass
    return per_game_league_averages_df

def scrape_per_poss_league_averages(save=False):
    """
    Scrape Per Possession League Averages table on Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        per_poss_league_averages_df (DataFrame): Per Possession League Averages
        table for seasons between 1946-1947 and 2018-2019
    """
    url = 'https://www.basketball-reference.com/leagues/NBA_stats_per_poss.html#stats::none'
    per_poss_league_averages_df = pd.read_html(url)[0]
    per_poss_league_averages_df.columns = per_poss_league_averages_df.columns.get_level_values(1)
    per_poss_league_averages_df.columns = ['RANK', 'SEASON', 'LEAGUE', 'AGE', 'HEIGHT',
                                  'WEIGHT', 'G', 'PER_100_FG', 'PER_100_FGA', 'PER_100_3P',
                                  'PER_100_3PA', 'PER_100_FT', 'PER_100_FTA', 'PER_100_ORB',
                                  'PER_100_DRB', 'PER_100_TRB', 'PER_100_AST', 'PER_100_STL',
                                  'PER_100_BLK', 'PER_100_TOV', 'PER_100_PF', 'PER_100_PTS',
                                  'FG%', '3PT%', 'FT%', 'PACE', 'EFG%', 'TOV%', 'ORB%', 'FT/FGA',
                                  'ORTG']
    per_poss_league_averages_df = per_poss_league_averages_df[(per_poss_league_averages_df['RANK']!='Rk') & (per_poss_league_averages_df['RANK'].notnull())]
    dtype = {'RANK':'int64', 'SEASON':'object', 'LEAGUE':'object', 'AGE':'float64',
             'HEIGHT':'object', 'WEIGHT':'float64', 'G':'int64', 'G':'int64',
             'PER_100_FG':'float64', 'PER_100_FGA':'float64', 'PER_100_3P':'float64',
             'PER_100_3PA':'float64', 'PER_100_FT':'float64', 'PER_100_FTA':'float64',
             'PER_100_ORB':'float64', 'PER_100_DRB':'float64', 'PER_100_TRB':'float64',
             'PER_100_AST':'float64', 'PER_100_STL':'float64', 'PER_100_BLK':'float64',
             'PER_100_TOV':'float64', 'PER_100_PF':'float64', 'PER_100_PTS':'float64',
             'FG%':'float64', '3PT%':'float64', 'FT%':'float64', 'PACE':'float64',
             'EFG%':'float64', 'TOV%':'float64', 'ORB%':'float64', 'FT/FGA':'float64',
             'ORTG':'float64'}
    per_poss_league_averages_df = per_poss_league_averages_df.astype(dtype)
    per_poss_league_averages_df['SEASON'] = per_poss_league_averages_df['SEASON'].apply(lambda x: x[0:5] + x[0:2] + x[5:8])
    if save:
        parent_directory = '../../data/nba/basketball_reference/league_data/league_averages/per100_poss/'
        per_poss_league_averages_df.to_csv(parent_directory +
                                              'per100_poss.csv',
                                              index=False)
    else:
        pass
    return per_poss_league_averages_df

def scrape_expanded_standings(save=False):
    """
    Scrape Expanded Standings table on Basketball-Reference.com.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        expanded_standings_df (DataFrame): Expanded Standings table for most
        recent season.
    """
    url = 'https://www.basketball-reference.com/leagues/NBA_2019_standings.html#expanded_standings::none'
    expanded_standings_df = pd.DataFrame()
    html = requests.get(url).text
    soup = BS(html, 'html.parser')
    placeholders = soup.find_all('div', {'class': 'placeholder'})
    for x in placeholders:
        comment = ''.join(x.next_siblings)
        soup_comment = BS(comment, 'html.parser')
        tables = soup_comment.find_all('table', attrs={"id":"expanded_standings"})
        for tag in tables:
            df = pd.read_html(tag.prettify())[0]
            expanded_standings_df = expanded_standings_df.append(df).reset_index()
            expanded_standings_df.columns = expanded_standings_df.columns.get_level_values(1)
            expanded_standings_df.drop('', axis=1, inplace=True)
    expanded_standings_df.columns = ['RANK', 'TEAM', 'OVERALL_RECORD', 'HOME_RECORD',
                                     'ROAD_RECORD', 'EASTERN_CONF_RECORD',
                                     'WESTERN_CONF_RECORD', 'ATLANTIC_DIV_RECORD',
                                     'CENTRAL_DIV_RECORD', 'SOUTHEAST_DIV_RECORD',
                                     'NORTHWEST_DIV_RECORD', 'PACIFIC_DIV_RECORD',
                                     'SOUTHWEST_DIC_RECORD', 'PRE_ALLSTAR_RECORD',
                                     'POST_ALLSTAR_RECORD', 'MARGIN_0-3_RECORD',
                                     'MARGIN+10_RECORD', 'OCT_RECORD', 'NOV_RECORD',
                                     'DEC_RECORD', 'JAN_RECORD', 'FEB_RECORD',
                                     'MAR_RECORD','APR_RECORD']
    if save:
        parent_directory = '../../data/nba/basketball_reference/league_data/expanded_standings/'
        expanded_standings_df.to_csv(parent_directory +
                                              'expanded_standings.csv',
                                              index=False)
    else:
        pass
    return expanded_standings_df

def scrape_nba_draft(save=False):
    """
    Scrape NBA Draft Pick table for 2005-2018 seasons.

    Args:
        save (bool): Indicates whether to write resulting pandas DataFrame to
                     .csv file. Defaults to False.

    Returns:
        draft_picks_df (DataFrame): NBA Draft Pick table
        between 2005 and 2018 seasons.
    """
    draft_picks_df = pd.DataFrame()
    min_draft_year = 2006
    max_draft_year = 2018
    player_count = ((max_draft_year - min_draft_year) + 1) * 60
    for i in range(0, player_count, 100):
        url = "https://www.basketball-reference.com/play-index/draft_finder.cgi?request=1&year_min={0}&year_max={1}&round_min=&round_max=&pick_overall_min=&pick_overall_max=&franch_id=&college_id=0&is_active=&is_hof=&pos_is_g=Y&pos_is_gf=Y&pos_is_f=Y&pos_is_fg=Y&pos_is_fc=Y&pos_is_c=Y&pos_is_cf=Y&c1stat=&c1comp=&c1val=&c2stat=&c2comp=&c2val=&c3stat=&c3comp=&c3val=&c4stat=&c4comp=&c4val=&order_by=year_id&order_by_asc=&offset={2}#stats::none".format(min_draft_year, max_draft_year, i)
        table = pd.read_html(url)[0]
        draft_picks_df = pd.concat([draft_picks_df, table])
    draft_picks_df.columns = draft_picks_df.columns.droplevel()
    mask = (draft_picks_df['Player'].notnull()) & (draft_picks_df['Player'] != 'Player')
    draft_picks_df = draft_picks_df[mask]
    draft_picks_df = draft_picks_df[['Year', 'Pk', 'Rd', 'Tm', 'Player', 'Age', 'Born', 'College']]
    draft_picks_df.columns = ['YEAR', 'PICK', 'ROUND', 'TEAM', 'PLAYER', 'AGE', 'BORN', 'COLLEGE']

    if save:
        parent_directory = '../../data/nba/basketball_reference/draft/'
        draft_picks_df.to_csv(parent_directory +
                                          'draft_selections.csv',
                                          index=False)
    else:
        pass
    return draft_picks_df

def create_league_base_table():
    """
    Combine Per Game League Averages, Per Poss League Averages, Team Shooting Averages,
    and Miscellaneous Averages DataFrames to create comprehensive base table for league stats.

    Args:
        None

    Returns:
        league_stats_df (DataFrame): League Averages for seasons between
        1946-1947 and 2018-2019 seasons
    """
    per_game_league_averages_df = pd.read_csv('../../data/nba/basketball_reference/league_data/league_averages/per_game/per_game.csv')
    per_poss_league_averages_df = pd.read_csv('../../data/nba/basketball_reference/league_data/league_averages/per100_poss/per100_poss.csv')
    league_average_team_shooting_df = pd.read_csv('../../data/nba/basketball_reference/league_data/league_averages/team_shooting/league_average_team_shooting.csv')
    league_average_misc_df = pd.read_csv('../../data/nba/basketball_reference/league_data/league_averages/miscellaneous/league_average_miscellaneous_stats.csv')

    league_stats_df = per_game_league_averages_df.merge(league_average_team_shooting_df, on='SEASON', how='left', suffixes=('', '_duplicate'))
    league_stats_df.drop([col for col in league_stats_df.columns if '_duplicate' in col], axis=1, inplace=True)
    league_stats_df = league_stats_df.merge(league_average_misc_df, on='SEASON', how='left', suffixes=('', '_duplicate'))
    league_stats_df.drop([col for col in league_stats_df.columns if '_duplicate' in col], axis=1, inplace=True)
    league_stats_df = league_stats_df.merge(per_poss_league_averages_df, on='SEASON', how='left', suffixes=('', '_duplicate'))
    league_stats_df.drop([col for col in league_stats_df.columns if '_duplicate' in col], axis=1, inplace=True)

    return league_stats_df

def create_team_base_table():
    """
    Combine Team Ratings, Miscellaneous Stats, Per 100 Possessions,
    Opponnent Per 100 Possessions, Team Shooting, and Opponent Shooting
    DataFrames to create comprehensive base table for team stats.

    Args:
        None

    Returns:
        team_stats_df (DataFrame): Team statistics for seasons between
        2004-2005 and 2018-2019 seasons
    """
    team_ratings_df = pd.read_csv('../../data/nba/basketball_reference/team_data/team_ratings/team_ratings.csv')
    misc_stats_df = pd.read_csv('../../data/nba/basketball_reference/team_data/miscellaneous/miscellaneous_stats.csv')
    per_100_possessions_df = pd.read_csv('../../data/nba/basketball_reference/team_data/per100_poss/per100_poss.csv')
    opponent_per_100_possessions_df = pd.read_csv('../../data/nba/basketball_reference/team_data/opp_per100_poss/opp_per100_poss.csv')
    team_shooting_df = pd.read_csv('../../data/nba/basketball_reference/team_data/team_shooting/team_shooting.csv')
    opponent_shooting_df = pd.read_csv('../../data/nba/basketball_reference/team_data/opp_shooting/opponent_shooting.csv')

    team_stats_df = team_ratings_df.merge(misc_stats_df, on=['TEAM', 'SEASON'], how='left', suffixes=('', '_duplicate'))
    team_stats_df.drop([col for col in team_stats_df.columns if '_duplicate' in col], axis=1, inplace=True)
    team_stats_df = team_stats_df.merge(per_100_possessions_df, on=['TEAM', 'SEASON'], how='left', suffixes=('', '_duplicate'))
    team_stats_df.drop([col for col in team_stats_df.columns if '_duplicate' in col], axis=1, inplace=True)
    team_stats_df = team_stats_df.merge(opponent_per_100_possessions_df, on=['TEAM', 'SEASON'], how='left', suffixes=('', '_duplicate'))
    team_stats_df.drop([col for col in team_stats_df.columns if '_duplicate' in col], axis=1, inplace=True)
    team_stats_df = team_stats_df.merge(team_shooting_df, on=['TEAM', 'SEASON'], how='left', suffixes=('', '_duplicate'))
    team_stats_df.drop([col for col in team_stats_df.columns if '_duplicate' in col], axis=1, inplace=True)
    team_stats_df = team_stats_df.merge(opponent_shooting_df, on=['TEAM', 'SEASON'], how='left', suffixes=('', '_duplicate'))
    team_stats_df.drop([col for col in team_stats_df.columns if '_duplicate' in col], axis=1, inplace=True)

    return team_stats_df

def create_player_base_table():
    """
    Combine Total, Per 100 Possessions, and Advanced DateFrames
    to create comprehensive base table for player stats.

    Args:
        None

    Returns:
        player_stats_df (DataFrame): Player statistics for seasons between
        2004-2005 and 2018-2019 seasons
    """
    player_totals_df = pd.read_csv('../../data/nba/basketball_reference/player_data/totals/totals.csv')
    player_per_100_possessions_df = pd.read_csv('../../data/nba/basketball_reference/player_data/per100_poss/per100_poss.csv')
    player_advanced_df = pd.read_csv('../../data/nba/basketball_reference/player_data/advanced/advanced.csv')

    player_stats_df = player_totals_df.merge(player_per_100_possessions_df,
                                            on=['PLAYER', 'SEASON', 'TEAM'],
                                            how='left', suffixes=('', '_duplicate'))
    player_stats_df.drop([col for col in player_stats_df.columns if '_duplicate' in col],
                                            axis=1, inplace=True)
    player_stats_df = player_stats_df.merge(player_advanced_df,
                                            on=['PLAYER', 'SEASON', 'TEAM'],
                                            how='left', suffixes=('', '_duplicate'))
    player_stats_df.drop([col for col in player_stats_df.columns if '_duplicate' in col],
                                            axis=1, inplace=True)
    player_stats_df['PLAYER'] = player_stats_df['PLAYER'].str.replace('*', '')

    def join_bbrefid(player_stats_df):
        """
        Join bbref_id onto Basketball-Reference base table.

        Args:
            player_stats_df (DataFrame): Basketball-Reference base table

        Returns:
            player_stats_df (DataFrame): Basketball-Referene base table with bbref_id join on.
        """
        # List of players without bbref_id in bridge table. Will add bbref_id for
        # these edge cases at the end of the function.
        bridge_table_missing_players = ['Erik Murphy', 'Ha Seung-Jin', 'Marcus Vinicius',
                                        'Taurean Waller-Prince', 'Walter Herrmann', 'Wang Zhizhi']
        # Get distinct player/seasons to differentiate players with the same name
        # but across different seasons (i.e., Gary Payton)
        distinct_player_seasons = (player_stats_df.groupby(['PLAYER', 'SEASON'])
                                                  .count()
                                                  .reset_index()
                                                  [['PLAYER', 'SEASON']])
        # Read in and join bridge table
        player_table = pd.read_csv('../../data/player_ids/player_table.csv')
        total = pd.merge(distinct_player_seasons, player_table, how='left', left_on='PLAYER', right_on='player_name')
        total['season_yyy'] = total.apply(lambda row: int(str(row['SEASON'][5:])), axis=1)
        # Filter out duplicate rows created by players with same name across different seasons (i.e., Gary Payton)
        total = total[((total['season_yyy']>=total['first_season']) & (total['season_yyy']<=total['last_season'])) |
                        (total['PLAYER'].isin(bridge_table_missing_players))][['PLAYER', 'SEASON', 'bbref_id']]
        # Add bbref_id to edge cases that do not show up in bridge table
        total.loc[total['PLAYER']=='Erik Murphy', 'bbref_id'] = 'murpher01'
        total.loc[total['PLAYER']=='Ha Seung-Jin', 'bbref_id'] = 'seungha01'
        total.loc[total['PLAYER']=='Marcus Vinicius', 'bbref_id'] = 'vincima01'
        total.loc[total['PLAYER']=='Taurean Waller-Prince', 'bbref_id'] = 'princta02'
        total.loc[total['PLAYER']=='Walter Herrmann', 'bbref_id'] = 'herrmwa01'
        total.loc[total['PLAYER']=='Wang Zhizhi', 'bbref_id'] = 'zhizhwa01'

        # Join bbref_id to player base table
        final = pd.merge(player_stats_df, total, how='left', left_on=['PLAYER', 'SEASON'], right_on=['PLAYER', 'SEASON'])
        # Handle edge cases in which two players with the same name play during the same season
        final = final[~(((final['PLAYER']=='Tony Mitchell') & (final['TEAM']=='DET') & (final['bbref_id']=='mitchto03')) |
                        ((final['PLAYER']=='Tony Mitchell') & (final['TEAM']=='MIL') & (final['bbref_id']=='mitchto02')) |
                         ((final['PLAYER']=='Chris Johnson') & (final['TEAM']=='MEM') & (final['bbref_id']=='johnsch03') & (final['SEASON']=='2012-2013')) |
                         ((final['PLAYER']=='Chris Johnson') & (final['TEAM']=='MIN') & (final['bbref_id']=='johnsch04') & (final['SEASON']=='2012-2013')) |
                         ((final['PLAYER']=='Marcus Williams') & (final['TEAM']=='NJN') & (final['bbref_id']=='willima04') & (final['SEASON']=='2007-2008')) |
                         ((final['PLAYER']=='Marcus Williams') & (final['TEAM']=='TOT') & (final['bbref_id']=='willima03') & (final['SEASON']=='2007-2008')) |
                         ((final['PLAYER']=='Marcus Williams') & (final['TEAM']=='SAS') & (final['bbref_id']=='willima03') & (final['SEASON']=='2007-2008')) |
                         ((final['PLAYER']=='Marcus Williams') & (final['TEAM']=='LAC') & (final['bbref_id']=='willima03') & (final['SEASON']=='2007-2008')) |
                         ((final['PLAYER']=='Marcus Williams') & (final['TEAM']=='GSW') & (final['bbref_id']=='willima04') & (final['SEASON']=='2008-2009')) |
                         ((final['PLAYER']=='Marcus Williams') & (final['TEAM']=='SAS') & (final['bbref_id']=='willima03') & (final['SEASON']=='2008-2009')) |
                         ((final['PLAYER']=='Chris Wright') & (final['TEAM']=='DAL') & (final['bbref_id']=='wrighch01') & (final['SEASON']=='2012-2013')))]
        return final
    player_stats_df = join_bbrefid(player_stats_df)
    player_stats_df.rename(columns={'bbref_id':'BBREF_ID'}, inplace=True)
    return player_stats_df

if __name__=='__main__':
    misc_stats_df, league_average_misc_df = scrape_miscellaneous_stats(save=False)
    sleep(180)
    per_100_possessions_df = scrape_per_100_possessions(save=False)
    sleep(180)
    opponent_per_100_possessions_df = scrape_opponent_per_100_possessions(save=False)
    sleep(180)
    team_shooting_df, league_average_team_shooting_df = scrape_team_shooting(save=False)
    sleep(180)
    opponent_shooting_df = scrape_opponent_shooting(save=False)
    sleep(180)
    player_per_100_possessions_df = scrape_player_per_100_possessions(save=False)
    sleep(180)
    player_advanced_df = scrape_player_advanced_stats(save=False)
    sleep(180)
    player_totals_df = scrape_player_total_stats(save=False)
    sleep(180)
    team_ratings_df = scrape_team_ratings(save=False)
    sleep(180)
    per_game_league_averages_df = scrape_per_game_league_averages(save=False)
    sleep(180)
    per_poss_league_averages_df = scrape_per_poss_league_averages(save=False)
    sleep(180)
    expanded_standings_df = scrape_expanded_standings(save=False)
    sleep(180)
    draft_picks_df = scrape_nba_draft(save=False)

    # Join tables to create individual team, player, and league base tables
    team_stats_df = create_team_base_table()
    team_stats_df.to_csv('../../data/nba/basketball_reference/team_data/combined/bbref_team_data.csv', index=False)
    player_stats_df = create_player_base_table()
    player_stats_df.to_csv('../../data/nba/basketball_reference/player_data/combined/bbref_player_data.csv', index=False)
    league_stats_df = create_league_base_table()
    league_stats_df.to_csv('../../data/nba/basketball_reference/league_data/league_averages/combined/bbref_league_data.csv', index=False)
