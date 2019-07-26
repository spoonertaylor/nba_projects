# Project: Player Projection Model (Chris)
# Description: Build model(s) to predict a player's RPM/BPM blend one season in the
# future. Investigate feature importances.
# Data Sources: Basketball-Reference and ESPN
# Last Updated: 7/25/2019

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error



if __name__=='__main__':
    # Read in featurized Basketball-Reference Box Score Data
    bbref_box_score = pd.read_csv('featurized_inputs/bbref_box_scores.csv')
    # Filter to SEASON_PLUS_1 target variable
    # Drop other target variables and raw total columns
    bbref_box_score = (bbref_box_score[bbref_box_score['SEASON_PLUS_1'].notnull()]
                        .drop(['BLEND', 'SEASON_PLUS_2', 'SEASON_PLUS_3',
                               'SEASON_PLUS_4', 'SEASON_PLUS_5', 'TEAM',
                               'G', 'GS', 'FG', 'FGA', 'FG%', '3P',
                               '3PA', '3P%', '2P', '2PA', '2P%', 'FT', 'FTA',
                               'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK',
                               'TOV', 'PF', 'PTS'], axis=1))
