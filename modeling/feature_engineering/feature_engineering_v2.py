# Project: Feature Engineering
# Description: Engineer potentential features for player projection model.
# Data Sources: Basketball-Reference and ESPN
# Last Updated: 7/15/2019

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

def create_model_input(data_source):
    # Source of data source paths
    data_source_dict = {'targets': '../../data/nba/modeling_targets/modeling_targets.csv',
                        'bbref_combined': '../../data/nba/basketball_reference/player_data/combined/bbref_player_data.csv',
                        'bbref_measurements': '../../data/nba/basketball_reference/player_data/measurements/player_measurements.csv',
                        'bbref_percentile': '../../data/nba/basketball_reference/player_data/percentile/nba_percentile_all.csv',
                        'bbref_position_percentile': '../../data/nba/basketball_reference/player_data/percentile/nba_percentile_position.csv',
                        'bbref_position_estimates': '../../data/nba/basketball_reference/player_data/positional_estimates/player_position_estimates.csv',
                        'bbref_salary': '../../data/nba/basketball_reference/player_data/salary/salary_info.csv',
                        'espn': '../../data/nba/espn/espn_nba_rpm.csv'}

    # Read in Targets, Measurements, Salary, Position Estimates, and ESPN Data
    targets = pd.read_csv(data_source_dict['targets'])
    bbref_measurements = pd.read_csv(data_source_dict['bbref_measurements'])
    bbref_salary = pd.read_csv(data_source_dict['bbref_salary'])
    bbref_position_estimates = pd.read_csv(data_source_dict['bbref_position_estimates'])
    espn = pd.read_csv(data_source_dict['espn'])

    # Reformat season columns to YYYY-YYYY format to join on
    bbref_position_estimates['season'] = bbref_position_estimates.apply(lambda row: str(int(row['season'] - 1)) +  '-' +  str(int(row['season'])), axis=1)
    bbref_salary['season'] = bbref_salary[bbref_salary['season'].notnull()].apply(lambda row: str(int(row['season'] - 1)) +  '-' +  str(int(row['season'])), axis=1)
    targets['season'] = targets[targets['season'].notnull()].apply(lambda row: str(int(row['season'] - 1)) +  '-' +  str(int(row['season'])), axis=1)

    # Remove partial seasons resulting from in-season trades (TOT only)
    espn = espn.groupby(['name', 'pos', 'espn_link', 'season']).mean().reset_index()

    # Join bbref_id onto espn table to join onto other dataframes
    player_table = pd.read_csv('../../data/player_ids/player_table.csv')
    player_table['draft_class'] = player_table['first_season'] - 1
    espn['season'] = espn.apply(lambda row: str(int(row['season'] - 1)) +  '-' +  str(int(row['season'])), axis=1)
    espn = (pd.merge(espn, player_table, how='left', on='espn_link')
                [['orpm', 'drpm', 'rpm', 'wins', 'bbref_id', 'season']])

    if data_source == 'bbref_combined':
        bbref_combined = pd.read_csv(data_source_dict[data_source])
        # Remove partial seasons resulting from in-season trades (TOT only)
        bbref_combined = bbref_combined[((bbref_combined.groupby(['BBREF_ID', 'SEASON'])['TEAM'].transform('size')>1) &
                                (bbref_combined['TEAM']=='TOT')) |
                                (bbref_combined.groupby(['BBREF_ID', 'SEASON'])['TEAM'].transform('size')<=1)]

        # Join DataFrames
        model_input = (pd.merge(targets, bbref_combined, how='left', left_on=['bbref_id', 'season'], right_on=['BBREF_ID', 'SEASON'], suffixes=('', '_duplicate'))
                         .merge(bbref_position_estimates[['bbref_id', 'season', 'advanced_position_cluster']], how='left', on=['bbref_id', 'season'], suffixes=('', '_duplicate'))
                         .drop(['RANK', 'BBREF_ID', 'SEASON'], axis=1))
        model_input.drop([col for col in model_input.columns if '_duplicate' in col], axis=1, inplace=True)

        # Handle Missing Values
        # Fill missing shooting percentages and attempts w/ zeros
        shooting_fields = ['FG', 'FGA', 'FG%' ,'2P', '2PA', '2P%',
                            '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%',
                            'PER100_FG', 'PER100_FGA',
                            'PER100_FG%', 'PER100_2P', 'PER100_2PA',
                            'PER100_2P%', 'PER100_3P', 'PER100_3PA',
                            'PER100_3P%', 'PER100_FT', 'PER100_FTA',
                            'PER100_FT%', 'eFG%', 'TS%', '3PA_RATE',
                            'FT_RATE']
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
                             'WS/48']
        model_input[box_score_fields] = model_input.groupby(['advanced_position_cluster', 'season'])[box_score_fields].transform(lambda x: x.fillna(x.mean()))

    elif data_source == 'bbref_percentile':
        bbref_percentile = pd.read_csv(data_source_dict[data_source])

        # Join DataFrames
        model_input = (pd.merge(targets, bbref_percentile, how='left', left_on=['bbref_id', 'season'], right_on=['BBREF_ID', 'SEASON'], suffixes=('', '_duplicate'))
                         .merge(bbref_position_estimates[['bbref_id', 'season', 'advanced_position_cluster']], how='left', on=['bbref_id', 'season'], suffixes=('', '_duplicate'))
                         .drop(['BBREF_ID', 'SEASON'], axis=1))
        model_input.drop([col for col in model_input.columns if '_duplicate' in col], axis=1, inplace=True)


        # Handle Missing Values
        # Fill missing shooting percentages and attempts w/ zeros
        shooting_fields = ['fg_percentile_all', 'fga_percentile_all',
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
                            'free_throw_rate_percentile_all']
        model_input.update(model_input[shooting_fields].fillna(0))

        # Fill non-shooting percentages/attempts statistics with average of
        # advanced_position_cluster/season groupby
        box_score_fields = ['age_percentile_all',
                             'ast_percent_percentile_all',
                             'ast_percentile_all',
                             'blk_percent_percentile_all',
                             'blk_percentile_all',
                             'bpm_percentile_all',
                             'def_bpm_percentile_all',
                             'def_win_shares_percentile_all',
                             'drb_percent_percentile_all',
                             'drb_percentile_all',
                             'foul_percentile_all',
                             'games_player_percentile_all',
                             'games_started_percentile_all',
                             'height_percentile_all',
                             'minutes_percentile_all',
                             'off_bpm_percentile_all',
                             'off_win_shares_percentile_all',
                             'orb_percent_percentile_all',
                             'oreb_percentile_all',
                             'points_percentile_all',
                             'stl_percent_percentile_all',
                             'stl_percentile_all',
                             'total_percentile_all',
                             'tov_percent_percentile_all',
                             'trb_percent_percentile_all',
                             'turnover_percentile_all',
                             'usg_percent_percentile_all',
                             'vorp_percentile_all',
                             'weight_percentile_all',
                             'win_shares_percentile_all',
                             'win_sharres_per_48_percentile_all']
        model_input[box_score_fields] = model_input.groupby(['advanced_position_cluster', 'season'])[box_score_fields].transform(lambda x: x.fillna(x.mean()))

    elif data_source == 'bbref_position_percentile':
        bbref_position_percentile = pd.read_csv(data_source_dict[data_source])

        # Join DataFrames
        model_input = (pd.merge(targets, bbref_position_percentile, how='left', left_on=['bbref_id', 'season'], right_on=['BBREF_ID', 'SEASON'], suffixes=('', '_duplicate'))
                         .merge(bbref_position_estimates[['bbref_id', 'season', 'advanced_position_cluster']], how='left', on=['bbref_id', 'season'], suffixes=('', '_duplicate'))
                         .drop(['BBREF_ID', 'SEASON'], axis=1))
        model_input.drop([col for col in model_input.columns if '_duplicate' in col], axis=1, inplace=True)

        # Handle Missing Values
        # Fill missing shooting percentages and attempts w/ zeros
        shooting_fields = ['fg_percentile_position',
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
        box_score_fields = ['age_percentile_position',
                             'ast_percent_percentile_position',
                             'ast_percentile_position',
                             'blk_percent_percentile_position',
                             'blk_percentile_position',
                             'bpm_percentile_position',
                             'def_bpm_percentile_position',
                             'def_win_shares_percentile_position',
                             'drb_percent_percentile_position',
                             'drb_percentile_position',
                             'foul_percentile_position',
                             'games_player_percentile_position',
                             'games_started_percentile_position',
                             'height_percentile_position',
                             'minutes_percentile_position',
                             'off_bpm_percentile_position',
                             'off_win_shares_percentile_position',
                             'orb_percent_percentile_position',
                             'oreb_percentile_position',
                             'points_percentile_position',
                             'stl_percent_percentile_position',
                             'stl_percentile_position',
                             'total_percentile_position',
                             'tov_percent_percentile_position',
                             'trb_percent_percentile_position',
                             'turnover_percentile_position',
                             'usg_percent_percentile_position',
                             'vorp_percentile_position',
                             'weight_percentile_position',
                             'win_shares_percentile_position',
                             'win_sharres_per_48_percentile_position']
        model_input[box_score_fields] = model_input.groupby(['advanced_position_cluster', 'season'])[box_score_fields].transform(lambda x: x.fillna(x.mean()))

    return model_input




if __name__=='__main__':
    # Create model input containing one of three dataframes: basketball-reference box scores, percentiles, positional percentiles
    model_input = create_model_input('bbref_combined')
    # model_input = create_model_input('bbref_percentile')
    # model_input = create_model_input('bbref_position_percentile')


    # Create three-season weighted average columns
    for col in [col for col in model_input.columns if col not in ['BBREF_ID', 'PLAYER', 'SEASON', 'POSITION', 'AGE',
                                                            'TEAM', 'height', 'weight', 'height_percentile_all',
                                                            'weight_percentile_all', 'age_percentile_all',
                                                            'advanced_position_cluster', 'height_percentile_position',
                                                            'weight_percentile_position', 'age_percentile_position', 'age',
                                                            'experience']]:
        weighted_average(model_input, col)
