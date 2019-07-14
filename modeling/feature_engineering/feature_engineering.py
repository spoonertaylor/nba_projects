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
    bbref_draft = pd.read_csv('../../data/nba/basketball_reference/draft/draft_selections.csv')

    # Read in ESPN data
    espn = pd.read_csv('../../data/nba/espn/espn_nba_rpm.csv')

    # Remove partial seasons (TOT only)
    bbref_combined = bbref_combined[((bbref_combined.groupby(['BBREF_ID', 'SEASON'])['TEAM'].transform('size')>1) &
                            (bbref_combined['TEAM']=='TOT')) |
                            (bbref_combined.groupby(['BBREF_ID', 'SEASON'])['TEAM'].transform('size')<=1)]

    espn = espn.groupby(['name', 'pos', 'espn_link', 'season']).mean().reset_index()

    # New metric creation
    bbref_combined['IMPACT_PLAY_RATE'] = (bbref_combined['PER100_BLK'] + bbref_combined['PER100_STL'])/bbref_combined['PER100_PF']

    # Reformat join columns particularly season to YYYY-YYYY to join on
    bbref_position_estimates['season'] = bbref_position_estimates.apply(lambda row: str(int(row['season'] - 1)) +  '-' +  str(int(row['season'])), axis=1)
    bbref_salary['season'] = bbref_salary[bbref_salary['season'].notnull()].apply(lambda row: str(int(row['season'] - 1)) +  '-' +  str(int(row['season'])), axis=1)

    # Join bbref_id onto draft table to join onto other dataframes
    player_table = pd.read_csv('../../data/player_ids/player_table.csv')
    player_table['draft_class'] = player_table['first_season'] - 1
    bbref_draft = (pd.merge(player_table, bbref_draft, how='left', left_on=['player_name', 'draft_class'], right_on=['PLAYER', 'YEAR'])
                        .rename({'AGE': 'DRAFT_AGE'}, axis=1)
                      [['bbref_id', 'PICK', 'ROUND']])

    # Join bbref_id onto espn table to join onto other dataframes
    espn['season'] = espn.apply(lambda row: str(int(row['season'] - 1)) +  '-' +  str(int(row['season'])), axis=1)
    espn = (pd.merge(espn, player_table, how='left', on='espn_link')
                [['orpm', 'drpm', 'rpm', 'wins', 'bbref_id', 'season']])


    # # Join DataFrames
    feature_matrix = (pd.merge(bbref_combined, bbref_measurements, how='left', left_on='BBREF_ID', right_on='bbref_id', suffixes=('', '_duplicate'))
                        .merge(bbref_percentile, how='left', on=['BBREF_ID', 'SEASON'], suffixes=('', '_duplicate'))
                        .merge(bbref_position_percentile, how='left', on=['BBREF_ID', 'SEASON'], suffixes=('', '_duplicate'))
                        .merge(bbref_position_estimates, how='left', left_on=['BBREF_ID', 'SEASON'], right_on=['bbref_id', 'season'], suffixes=('', '_duplicate'))
                        .merge(bbref_salary, how='left', left_on=['BBREF_ID', 'SEASON'], right_on=['bbref_id', 'season'], suffixes=('', '_duplicate'))
                        .merge(bbref_draft, how='left', on='bbref_id', suffixes=('', '_duplicate'))
                        .merge(espn, how='left', on=['bbref_id', 'season'])
                        .drop(['RANK', 'bbref_id', 'league', 'games_played', 'minutes_played', 'position_minutes', 'team_flag', 'team', 'position', 'season'], axis=1))
    feature_matrix.drop([col for col in feature_matrix.columns if '_duplicate' in col], axis=1, inplace=True)

    # Move bbref_id to front of feature matrix
    cols = feature_matrix.columns.tolist()
    cols.insert(0, cols.pop(cols.index('BBREF_ID')))
    feature_matrix = feature_matrix.reindex(columns= cols)

    # Create weighted average columns
    for col in [col for col in feature_matrix.columns if col not in ['BBREF_ID', 'PLAYER', 'SEASON', 'POSITION', 'AGE',
                                                            'TEAM', 'height', 'weight', 'height_percentile_all',
                                                            'weight_percentile_all', 'age_percentile_all',
                                                            'advanced_position_cluster', 'height_percentile_position',
                                                            'weight_percentile_position', 'age_percentile_position', 'age',
                                                            'experience', 'contract_type', 'PICK', 'ROUND']]:
        weighted_average(feature_matrix, col)




    # Write out feature matrix
    feature_matrix.to_csv('feature_matrix/feature_matrix.csv', index=False)
