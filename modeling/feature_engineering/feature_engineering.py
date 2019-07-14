# Project: Feature Engineering
# Description: Engineer potentential features for player projection model.
# Data Sources: Basketball-Reference and ESPN
# Last Updated: 7/13/2019

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
        partial seasons resulting from trades removed
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
        as new column with the naming convention 'column_3AVG'
    """
    wts3 = np.array([1, 2, 3])
    wts2 = np.array([1, 2])
    df['3_season_avg'] = df.groupby(['PLAYER', 'BBREF_ID'])[col].apply(lambda x: x.rolling(window=3).apply(weight_3season(wts3)).round(3))
    df['2_season_avg'] = df.groupby(['PLAYER', 'BBREF_ID'])[col].apply(lambda x: x.rolling(window=2).apply(weight_2seasons(wts2)).round(3))
    df['{}_3AVG'.format(col)] = df['3_season_avg'].fillna(df['2_season_avg']).fillna(df[col])
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

    # Create column w/ last season stat and avg stat over previous three seasons
    df_test = bbref_combined[['PLAYER',  'BBREF_ID', 'SEASON', 'MP', 'PTS']]

    # Create unweighted average columns
    # for col in ['MP', 'PTS']:
    #     unweighted_average(df_test, col)

    # Create weighted average columns
    for col in ['MP', 'PTS']:
        weighted_average(df_test, col)
