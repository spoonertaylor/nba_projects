# Project: Sports-Reference Scraping
# Project Track: Data Scraping
# Description: Scrape player tables from Sports-Reference.com for players who
# played in the NBA between 2004-2005 and 2018-2019 seasons.
# Data Sources: Sports-Reference
# Last Updated: 6/10/2019

import numpy as np
import pandas as pd
import requests
from time import sleep
from bs4 import BeautifulSoup as BS

def scrape_per_100_possessions(save=False):
    """
    Scrape collegiate Per 100 Possesion stats for all players that played in
    the NBA between the 2004-2005 and 2018-2019 seasons. Per 100 Possession stats
    comes from Sports-Reference.com. For each player, individual season and career
    stats are scraped.

    Args:
    save (bool): Indicates whether to write resulting pandas DataFrame to
                 .csv file. Defaults to False.
    Returns:
        sports_ref_per100: pandas DataFrame containing collegiate Per 100
        Possesion stats
        missing_players_df: pandas DataFrame containing player names,
        sports-reference ID's, basketball-reference ID's, and NBA season debute
        for all players who did not return any stats from sports-reference.
        Used to double-check if the function unexpectidely did not return any data
        for non-international or high-school players.
    """
    sports_ref_per100 = pd.DataFrame()
    errors = []
    player_ids_df = pd.read_csv('../../data/player_ids/player_table.csv')
    for index, row in player_ids_df.iterrows():
        sleep(np.random.randint(10, 15))
        url = "https://www.sports-reference.com/cbb/players/{0}.html#players_per_poss::none".format(row['sportsref_id'])
        html = requests.get(url).text
        soup = BS(html, 'html.parser')
        placeholders = soup.find_all('div', {'class': 'placeholder'})
        for x in placeholders:
            comment = ''.join(x.next_siblings)
            soup_comment = BS(comment, 'html.parser')
            tables = soup_comment.find_all('table', attrs={"id":"players_per_poss"})
            for tag in tables:
                df = pd.read_html(tag.prettify())[0]
                df = df[['Season', 'School', 'Conf', 'G', 'GS', 'MP',
                        'FG', 'FGA', 'FG%', '2P', '2PA', '2P%', '3P',
                        '3PA', '3P%', 'FT', 'FTA', 'FT%', 'TRB', 'AST',
                        'STL', 'BLK', 'TOV', 'PF', 'PTS', 'ORtg', 'DRtg']]
                df.columns = ['SEASON', 'SCHOOL', 'CONFERENCE', 'G', 'GS', 'MP'] + \
                             ['PER100_' + str(col) for col in df.columns if col not in \
                             ['Season', 'School', 'Conf', 'G', 'GS', 'MP']]
                df['PLAYER'] = row['player_name']
                df['SPORTS_REF_ID'] = row['sportsref_id']
                errors.append((row['player_name'], row['sportsref_id'], row['bbref_id'], row['first_season']))
        sports_ref_per100 = sports_ref_per100.append(df, sort=False)
        errors.append((row['player_name'], row['sportsref_id'], row['bbref_id'], row['first_season']))
    missing_players_df = pd.DataFrame([x for x in errors if errors.count(x)==1], columns=['PLAYER_NAME', 'PLAYER_ID', 'BBREF_ID', 'FIRST_SEASON'])
    sports_ref_per100 = sports_ref_per100.drop_duplicates()
    if save:
        parent_directory = '../../data/ncaa/sports_reference/player_data/per100_poss/'
        sports_ref_per100.to_csv(parent_directory +
                                                'per100_poss.csv',
                                                index=False)
    else:
        pass
    return sports_ref_per100, missing_players_df

def scrape_advance(save=False):
    """
    Scrape collegiate advance stats for all players that played in the NBA
    between the 2004-2005 and 2018-2019 seasons. Advance stats comes from
    Sports-Reference.com. For each player, individual season and career
    stats are scraped.

    Args:
    save (bool): Indicates whether to write resulting pandas DataFrame to
                 .csv file. Defaults to False.
    Returns:
        sports_ref_advance: pandas DataFrame containing collegiate advance stats
        missing_players_df: pandas DataFrame containing player names,
        sports-reference ID's, basketball-reference ID's, and NBA season debute
        for all players who did not return any stats from sports-reference.
        Used to double-check if the function unexpectidely did not return any data
        for non-international or high-school players.
    """
    sports_ref_advance = pd.DataFrame()
    errors = []
    player_ids_df = pd.read_csv('../../data/player_ids/player_table.csv')
    for index, row in player_ids_df.iterrows():
        sleep(np.random.randint(10, 15))
        url = "https://www.sports-reference.com/cbb/players/{0}.html#players_advanced::none".format(row['sportsref_id'])
        html = requests.get(url).text
        soup = BS(html, 'html.parser')
        placeholders = soup.find_all('div', {'class': 'placeholder'})
        for x in placeholders:
            comment = ''.join(x.next_siblings)
            soup_comment = BS(comment, 'html.parser')
            tables = soup_comment.find_all('table', attrs={"id":"players_advanced"})
            for tag in tables:
                df = pd.read_html(tag.prettify())[0]
                try:
                    df = df[['Season', 'School', 'Conf', 'G', 'GS', 'MP', 'PER', 'TS%', 'eFG%',
                              '3PAr', 'FTr', 'PProd', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%',
                              'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/40',
                              'OBPM', 'DBPM', 'BPM']]
                except:
                    try:
                        df['PER'], df['OBPM'], df['DBPM'], df['BPM'] = np.nan, np.nan, np.nan, np.nan
                        df = df[['Season', 'School', 'Conf', 'G', 'GS', 'MP', 'PER', 'TS%', 'eFG%',
                                  '3PAr', 'FTr', 'PProd', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%',
                                  'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/40',
                                  'OBPM', 'DBPM', 'BPM']]

                    except:
                        df['OWS'], df['DWS'], df['WS'], df['WS/40'] = np.nan, np.nan, np.nan, np.nan
                        df = df[['Season', 'School', 'Conf', 'G', 'GS', 'MP', 'PER', 'TS%', 'eFG%',
                                  '3PAr', 'FTr', 'PProd', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%',
                                  'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/40',
                                  'OBPM', 'DBPM', 'BPM']]
                df.columns = ['SEASON', 'SCHOOL', 'CONFERENCE'] + \
                             [col for col in df.columns if col not in \
                             ['Season', 'School', 'Conf']]
                df['PLAYER'] = row['player_name']
                df['SPORTS_REF_ID'] = row['sportsref_id']
                errors.append((row['player_name'], row['sportsref_id'], row['bbref_id'], row['first_season']))
        sports_ref_advance = sports_ref_advance.append(df, sort=False)
        errors.append((row['player_name'], row['sportsref_id'], row['bbref_id'], row['first_season']))
    missing_players_df = pd.DataFrame([x for x in errors if errors.count(x)==1], columns=['PLAYER_NAME', 'PLAYER_ID', 'BBREF_ID', 'FIRST_SEASON'])
    sports_ref_advance = sports_ref_advance.drop_duplicates()
    if save:
        parent_directory = '../../data/ncaa/sports_reference/player_data/advanced/'
        sports_ref_advance.to_csv(parent_directory + 'advanced.csv', index=False)
    else:
        pass
    return sports_ref_advance, missing_players_df

def scrape_per_40_min(save=False):
    """
    Scrape collegiate Per 40 Minute stats for all players that played in
    the NBA between the 2004-2005 and 2018-2019 seasons. Per 40 Minute stats
    comes from Sports-Reference.com. For each player, individual season and career
    stats are scraped.

    Args:
    save (bool): Indicates whether to write resulting pandas DataFrame to
                 .csv file. Defaults to False.
    Returns:
        sports_ref_per40: pandas DataFrame containing collegiate Per 40
        Minute stats
        missing_players_df: pandas DataFrame containing player names,
        sports-reference ID's, basketball-reference ID's, and NBA season debute
        for all players who did not return any stats from sports-reference.
        Used to double-check if the function unexpectidely did not return any data
        for non-international or high-school players.
    """
    sports_ref_per40 = pd.DataFrame()
    errors = []
    player_ids_df = pd.read_csv('../../data/player_ids/player_table.csv')
    for index, row in player_ids_df.iterrows():
        sleep(np.random.randint(10, 15))
        url = "https://www.sports-reference.com/cbb/players/{0}.html#players_per_min::none".format(row['sportsref_id'])
        html = requests.get(url).text
        soup = BS(html, 'html.parser')
        placeholders = soup.find_all('div', {'class': 'placeholder'})
        for x in placeholders:
            comment = ''.join(x.next_siblings)
            soup_comment = BS(comment, 'html.parser')
            tables = soup_comment.find_all('table', attrs={"id":"players_per_min"})
            for tag in tables:
                df = pd.read_html(tag.prettify())[0]
                df = df[['Season', 'School', 'Conf', 'G', 'GS', 'MP', 'FG', 'FGA',
                'FG%', '2P', '2PA', '2P%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%',
                'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']]
                df.columns = ['SEASON', 'SCHOOL', 'CONFERENCE', 'G', 'GS', 'MP'] + \
                             ['PER40_' + str(col) for col in df.columns if col not in \
                             ['Season', 'School', 'Conf', 'G', 'GS', 'MP']]
                df['PLAYER'] = row['player_name']
                df['SPORTS_REF_ID'] = row['sportsref_id']
                errors.append((row['player_name'], row['sportsref_id'], row['bbref_id'], row['first_season']))
        sports_ref_per40 = sports_ref_per40.append(df, sort=False)
        errors.append((row['player_name'], row['sportsref_id'], row['bbref_id'], row['first_season']))
        print(row['player_name'])
    missing_players_df = pd.DataFrame([x for x in errors if errors.count(x)==1], columns=['PLAYER_NAME', 'PLAYER_ID', 'BBREF_ID', 'FIRST_SEASON'])
    sports_ref_per40 = sports_ref_per40.drop_duplicates()
    if save:
        parent_directory = '../../data/ncaa/sports_reference/player_data/per40_min/'
        sports_ref_per40.to_csv(parent_directory +
                                                'per40_min.csv',
                                                index=False)
    else:
        pass
    return sports_ref_per40, missing_players_df

def create_college_base_table():
    """
    Combine Per 40-Minute, Per 100 Possessions, and Advanced DateFrames
    to create comprehensive base table for college player stats for those players
    who played in the NBA since the 2004-2005 season.

    Args:
        None

    Returns:
        college_stats_df (DataFrame): College statistics for those players who
        played in the NBA between 2004-2005 and 2018-2019.
    """
    sports_ref_per100 = pd.read_csv('../../data/ncaa/sports_reference/player_data/per100_poss/per100_poss.csv')
    sports_ref_advance = pd.read_csv('../../data/ncaa/sports_reference/player_data/advanced/advanced.csv')
    sports_ref_per_40 = pd.read_csv('../../data/ncaa/sports_reference/player_data/per40_min/per40_min.csv')

    college_stats_df = sports_ref_advance.merge(sports_ref_per_40, on=['PLAYER', 'SEASON', 'SCHOOL'], how='left', suffixes=('', '_duplicate'))
    college_stats_df.drop([col for col in college_stats_df.columns if '_duplicate' in col], axis=1, inplace=True)
    college_stats_df = college_stats_df.merge(sports_ref_per100, on=['PLAYER', 'SEASON', 'SCHOOL'], how='left', suffixes=('', '_duplicate'))
    college_stats_df.drop([col for col in college_stats_df.columns if '_duplicate' in col], axis=1, inplace=True)

    college_stats_df = college_stats_df[['PLAYER', 'SEASON', 'SCHOOL', 'CONFERENCE',
       'G', 'GS', 'MP', 'PER', 'TS%', 'eFG%',
       '3PAr', 'FTr', 'PProd', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%',
       'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/40', 'OBPM', 'DBPM', 'BPM',
        'PER40_FG', 'PER40_FGA', 'PER40_FG%', 'PER40_2P', 'PER40_2PA',
       'PER40_2P%', 'PER40_3P', 'PER40_3PA', 'PER40_3P%', 'PER40_FT',
       'PER40_FTA', 'PER40_FT%', 'PER40_TRB', 'PER40_AST', 'PER40_STL',
       'PER40_BLK', 'PER40_TOV', 'PER40_PF', 'PER40_PTS', 'PER100_FG',
       'PER100_FGA', 'PER100_FG%', 'PER100_2P', 'PER100_2PA', 'PER100_2P%',
       'PER100_3P', 'PER100_3PA', 'PER100_3P%', 'PER100_FT', 'PER100_FTA',
       'PER100_FT%', 'PER100_TRB', 'PER100_AST', 'PER100_STL', 'PER100_BLK',
       'PER100_TOV', 'PER100_PF', 'PER100_PTS', 'PER100_ORtg', 'PER100_DRtg', 'SPORTS_REF_ID', ]]

    return college_stats_df

if __name__=='__main__':
    # Scrape Sports-Reference Per 100 Possessions Table
    sports_ref_per100, per100_missing_df = scrape_per_100_possessions(save=False)

    # Scrape Sports-Reference Advance Table
    sports_ref_advance, advance_missing_df = scrape_advance(save=False)

    # Scrape Sports-Reference Per 40 Minutes Tables
    sports_ref_per_40, per40_missing_df = scrape_per_40_min(save=False)

    # Join tables to create individual player base table
    college_stats_df = create_college_base_table()
    college_stats_df.to_csv('../../data/ncaa/sports_reference/player_data/combined/sports_ref_player_data.csv', index=False)
