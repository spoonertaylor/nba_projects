# Project: Feature Engineering
# Description: Engineer potentential features for player projection model.
# Data Sources: Basketball-Reference and ESPN
# Last Updated: 7/14/2019

import numpy as np
import pandas as pd

import warnings
from pandas.core.common import SettingWithCopyWarning
warnings.filterwarnings(action='ignore', category=SettingWithCopyWarning)

def unweighted_average(df, col):
    """
    Calculate average of previous three seasons for a given statistic. If a player
    has played fewer than three seasons then the calculation returns either the
    two-season average or current season statistic.

    Args:
        df: pandas DataFrame with statistics at the player/season level with
        partial seasons resulting from trades removed.
        col: column on with which to calculate the three-season average.

    Returns:
        df: Original pandas Dataframe with three-season average added as new
        column with the naming convention 'column_3AVG'
    """
    df['3_season_avg'] = df.groupby(['PLAYER', 'BBREF_ID'])[col].apply(lambda x: x.rolling(window=3).mean().round(3))
    df['2_season_avg'] = df.groupby(['PLAYER', 'BBREF_ID'])[col].apply(lambda x: x.rolling(window=2).mean().round(3))
    df['{}_3AVG'.format(col)] = df['3_season_avg'].fillna(df['2_season_avg']).fillna(df[col])
    df.drop(['3_season_avg', '2_season_avg'], axis=1, inplace=True)
    return df

def weight_2seasons(w):
    """
    Helper function to calculate weighted average for previous two seasons of a statistic.
    """
    def g(x):
        return (w*x).sum()/3
    return g

def weight_3season(w):
    """
    Helper function to calculate weighted average for previous three seasons of a statistic.
    """
    def g(x):
        return (w*x).sum()/5
    return g

def weighted_average(df, col):
    """
    Calculate weighted average of previous three seasons for a given statistic.
    If a player has played fewer than three seasons then the calculation returns
    either the two-season weighted average or current season statistic.

    Args:
        df: pandas DataFrame with statistics at the player/season level with
        partial seasons resulting from trades removed
        col: column on with which to calculate the three-season weighted average.

    Returns:
        df: Original pandas Dataframe with three-season weighted average added
        as new column with the naming convention 'column_3WAVG'
    """
    wts3 = np.array([1, 2, 3])
    wts2 = np.array([1, 2])
    df['3_season_avg'] = df.groupby(['PLAYER', 'BBREF_ID'])[col].apply(lambda x: x.rolling(window=3).apply(weight_3season(wts3), raw=True).round(3))
    df['2_season_avg'] = df.groupby(['PLAYER', 'BBREF_ID'])[col].apply(lambda x: x.rolling(window=2).apply(weight_2seasons(wts2), raw=True).round(3))
    df['{}_3WAVG'.format(col)] = df['3_season_avg'].fillna(df['2_season_avg']).fillna(df[col])
    df.drop(['3_season_avg', '2_season_avg'], axis=1, inplace=True)
    return df


if __name__=='__main__':
    # Read in Basketball-Reference data
    bbref_combined = pd.read_csv('../../data/nba/basketball_reference/player_data/combined/bbref_player_data.csv')
    bbref_measurements = pd.read_csv('../../data/nba/basketball_reference/player_data/measurements/player_measurements.csv')
    bbref_percentile = pd.read_csv('../../data/nba/basketball_reference/player_data/percentile/nba_percentile_all.csv')
    bbref_position_percentile = pd.read_csv('../../data/nba/basketball_reference/player_data/percentile/nba_percentile_position.csv')
    bbref_position_estimates = pd.read_csv('../../data/nba/basketball_reference/player_data/positional_estimates/player_position_estimates.csv')
    bbref_salary = pd.read_csv('../../data/nba/basketball_reference/player_data/salary/salary_info.csv')

    # Read in ESPN data
    espn = pd.read_csv('../../data/nba/espn/espn_nba_rpm.csv')

    # Remove partial seasons resulting from in-season trades (TOT only)
    bbref_combined = bbref_combined[((bbref_combined.groupby(['BBREF_ID', 'SEASON'])['TEAM'].transform('size')>1) &
                            (bbref_combined['TEAM']=='TOT')) |
                            (bbref_combined.groupby(['BBREF_ID', 'SEASON'])['TEAM'].transform('size')<=1)]

    espn = espn.groupby(['name', 'pos', 'espn_link', 'season']).mean().reset_index()

    # New metric creation
    bbref_combined['IMPACT_PLAY_RATE'] = (bbref_combined['PER100_BLK'] + bbref_combined['PER100_STL'])/bbref_combined['PER100_PF']
    bbref_combined['PSA'] = (bbref_combined['PER100_PTS'])/(bbref_combined['PER100_FGA'] + bbref_combined['PER100_FTA'])

    # Reformat season columns to YYYY-YYYY format to join on
    bbref_position_estimates['season'] = bbref_position_estimates.apply(lambda row: str(int(row['season'] - 1)) +  '-' +  str(int(row['season'])), axis=1)
    bbref_salary['season'] = bbref_salary[bbref_salary['season'].notnull()].apply(lambda row: str(int(row['season'] - 1)) +  '-' +  str(int(row['season'])), axis=1)

    # Join bbref_id onto espn table to join onto other dataframes
    player_table = pd.read_csv('../../data/player_ids/player_table.csv')
    player_table['draft_class'] = player_table['first_season'] - 1
    espn['season'] = espn.apply(lambda row: str(int(row['season'] - 1)) +  '-' +  str(int(row['season'])), axis=1)
    espn = (pd.merge(espn, player_table, how='left', on='espn_link')
                [['orpm', 'drpm', 'rpm', 'wins', 'bbref_id', 'season']])


    # Join DataFrames
    model_input = (pd.merge(bbref_combined, bbref_measurements, how='left', left_on='BBREF_ID', right_on='bbref_id', suffixes=('', '_duplicate'))
                        .merge(bbref_percentile, how='left', on=['BBREF_ID', 'SEASON'], suffixes=('', '_duplicate'))
                        .merge(bbref_position_percentile, how='left', on=['BBREF_ID', 'SEASON'], suffixes=('', '_duplicate'))
                        .merge(bbref_position_estimates, how='left', left_on=['BBREF_ID', 'SEASON'], right_on=['bbref_id', 'season'], suffixes=('', '_duplicate'))
                        .merge(bbref_salary, how='left', left_on=['BBREF_ID', 'SEASON'], right_on=['bbref_id', 'season'], suffixes=('', '_duplicate'))
                        .merge(espn, how='left', on=['bbref_id', 'season'])
                        .drop(['RANK', 'bbref_id', 'league', 'games_played', 'minutes_played',
                               'position_minutes', 'team_flag', 'team', 'position', 'season', 'contract_type'], axis=1))
    model_input.drop([col for col in model_input.columns if '_duplicate' in col], axis=1, inplace=True)

    # Move bbref_id to front of feature matrix
    cols = model_input.columns.tolist()
    cols.insert(0, cols.pop(cols.index('BBREF_ID')))
    model_input = model_input.reindex(columns= cols)

    # Handle Missing Values
    # Fill missing shooting percentages and attempts w/ zeros
    shooting_fields = ['FG', 'FGA', 'FG%' ,'2P', '2PA', '2P%',
                        '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%',
                        'PER100_FG', 'PER100_FGA',
                        'PER100_FG%', 'PER100_2P', 'PER100_2PA',
                        'PER100_2P%', 'PER100_3P', 'PER100_3PA',
                        'PER100_3P%', 'PER100_FT', 'PER100_FTA',
                        'PER100_FT%', 'eFG%', 'TS%', '3PA_RATE',
                        'FT_RATE', 'fg_percentile_all', 'fga_percentile_all',
                        'fg_percent_percentile_all', 'three_point_made_percentile_all',
                        'three_point_attempt_percentile_all',
                        'three_point_percent_percentile_all',
                        'two_point_made_percentile_all',
                        'two_point_attempt_percentile_all',
                        'two_point_percent_percentile_all',
                        'efg_percent_percentile_all',
                        'true_shooting_percent_percentile_all',
                        'free_throw_made_percentile_all',
                        'free_throw_attempt_percentile_all',
                        'free_throw_percent_percentile_all',
                        'fg_made_per100_percentile_all',
                        'fg_attempted_per100_percentile_all',
                        'three_point_made_per100_percentile_all',
                        'three_point_attempt_per100_percentile_all',
                        'two_point_made_per100_percentile_all',
                        'two_point_attempt_per100_percentile_all',
                        'free_throw_made_per100_percentile_all',
                        'free_throw_attempt_per100_percentile_all',
                        'three_point_attempt_rate_percentile_all',
                        'free_throw_rate_percentile_all',
                        'fg_percentile_position',
                        'fga_percentile_position',
                        'fg_percent_percentile_position',
                        'three_point_made_percentile_position',
                        'three_point_attempt_percentile_position',
                        'three_point_percent_percentile_position',
                        'two_point_made_percentile_position',
                        'two_point_attempt_percentile_position',
                        'two_point_percent_percentile_position',
                        'efg_percent_percentile_position',
                        'true_shooting_percent_percentile_position',
                        'free_throw_made_percentile_position',
                        'free_throw_attempt_percentile_position',
                        'free_throw_percent_percentile_position',
                        'fg_made_per100_percentile_position',
                        'fg_attempted_per100_percentile_position',
                        'three_point_made_per100_percentile_position',
                        'three_point_attempt_per100_percentile_position',
                        'two_point_made_per100_percentile_position',
                        'two_point_attempt_per100_percentile_position',
                        'free_throw_made_per100_percentile_position',
                        'free_throw_attempt_per100_percentile_position',
                        'three_point_attempt_rate_percentile_position',
                        'free_throw_rate_percentile_position']
    model_input.update(model_input[shooting_fields].fillna(0))

    # Fill non-shooting percentages/attempts statistics with average of
    # advanced_position_cluster/season groupby
    box_score_fields = ['AST',
                         'AST%',
                         'BLK',
                         'BLK%',
                         'BPM',
                         'DBPM',
                         'DRB',
                         'DRB%',
                         'DWS',
                         'G',
                         'GS',
                         'IMPACT_PLAY_RATE',
                         'MP',
                         'OBPM',
                         'ORB',
                         'ORB%',
                         'OWS',
                         'PER',
                         'PER100_AST',
                         'PER100_BLK',
                         'PER100_DRB',
                         'PER100_DRtg',
                         'PER100_ORB',
                         'PER100_ORtg',
                         'PER100_PF',
                         'PER100_PTS',
                         'PER100_STL',
                         'PER100_TOV',
                         'PER100_TRB',
                         'PF',
                         'PSA',
                         'PTS',
                         'STL',
                         'STL%',
                         'TOV',
                         'TOV%',
                         'TRB',
                         'TRB%',
                         'USG%',
                         'VORP',
                         'WS',
                         'WS/48',
                         'age',
                         'age_percentile_all',
                         'age_percentile_position',
                         'ast_percent_percentile_all',
                         'ast_percent_percentile_position',
                         'ast_percentile_all',
                         'ast_percentile_position',
                         'blk_percent_percentile_all',
                         'blk_percent_percentile_position',
                         'blk_percentile_all',
                         'blk_percentile_position',
                         'bpm_percentile_all',
                         'bpm_percentile_position',
                         'def_bpm_percentile_all',
                         'def_bpm_percentile_position',
                         'def_win_shares_percentile_all',
                         'def_win_shares_percentile_position',
                         'drb_percent_percentile_all',
                         'drb_percent_percentile_position',
                         'drb_percentile_all',
                         'drb_percentile_position',
                         'experience',
                         'foul_percentile_all',
                         'foul_percentile_position',
                         'games_player_percentile_all',
                         'games_player_percentile_position',
                         'games_started_percentile_all',
                         'games_started_percentile_position',
                         'height',
                         'height_percentile_all',
                         'height_percentile_position',
                         'minutes_c',
                         'minutes_percentile_all',
                         'minutes_percentile_position',
                         'minutes_pf',
                         'minutes_pg',
                         'minutes_sf',
                         'minutes_sg',
                         'off_bpm_percentile_all',
                         'off_bpm_percentile_position',
                         'off_court_plus_minus',
                         'off_win_shares_percentile_all',
                         'off_win_shares_percentile_position',
                         'on_court_plus_minus',
                         'orb_percent_percentile_all',
                         'orb_percent_percentile_position',
                         'oreb_percentile_all',
                         'oreb_percentile_position',
                         'points_percentile_all',
                         'points_percentile_position',
                         'position_numeric',
                         'prop_c',
                         'prop_pf',
                         'prop_pg',
                         'prop_sf',
                         'prop_sg',
                         'salary',
                         'salary_prop_cap',
                         'stl_percent_percentile_all',
                         'stl_percent_percentile_position',
                         'stl_percentile_all',
                         'stl_percentile_position',
                         'total_percentile_all',
                         'total_percentile_position',
                         'tov_percent_percentile_all',
                         'tov_percent_percentile_position',
                         'trb_percent_percentile_all',
                         'trb_percent_percentile_position',
                         'turnover_percentile_all',
                         'turnover_percentile_position',
                         'usg_percent_percentile_all',
                         'usg_percent_percentile_position',
                         'vorp_percentile_all',
                         'vorp_percentile_position',
                         'weight',
                         'weight_percentile_all',
                         'weight_percentile_position',
                         'win_shares_percentile_all',
                         'win_shares_percentile_position',
                         'win_sharres_per_48_percentile_all',
                         'win_sharres_per_48_percentile_position']
    model_input[box_score_fields] = model_input.groupby(['advanced_position_cluster', 'SEASON'])[box_score_fields].transform(lambda x: x.fillna(x.mean()))

    # Fill espn metrics between 2013-2014 and 2018-2019 with average of
    # advanced_position_cluster/season groupby
    model_input[['orpm', 'drpm', 'rpm', 'wins']] = model_input[model_input['SEASON']>='2013-2014'].groupby(['advanced_position_cluster', 'SEASON'])[['orpm', 'drpm', 'rpm', 'wins']].transform(lambda x: x.fillna(x.mean()))

    # Create three-season weighted average columns
    for col in [col for col in model_input.columns if col not in ['BBREF_ID', 'PLAYER', 'SEASON', 'POSITION', 'AGE',
                                                            'TEAM', 'height', 'weight', 'height_percentile_all',
                                                            'weight_percentile_all', 'age_percentile_all',
                                                            'advanced_position_cluster', 'height_percentile_position',
                                                            'weight_percentile_position', 'age_percentile_position', 'age',
                                                            'experience']]:
        weighted_average(model_input, col)




    # Write out feature matrix
    model_input.to_csv('model_input/model_input.csv', index=False)
