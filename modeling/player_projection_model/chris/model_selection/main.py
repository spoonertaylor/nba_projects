# Project: Player Projection Model (Chris)
# Description: Build model to predict a player's RPM/BPM blend one season in the
# future.
# Data Sources: Basketball-Reference and ESPN
# Last Updated: 8/1/2019

import numpy as np
import pandas as pd
import pickle
import os
import imgkit
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso, Ridge, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error

# Plotting Style
plt.style.use('fivethirtyeight')

# Supress various warnings. ConvergenceWarning won't surpress when gradient boosting
# is run in parallel.
import warnings
from sklearn.exceptions import DataConversionWarning, ConvergenceWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)
warnings.filterwarnings(action='ignore', category=ConvergenceWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)

def plot_cross_validation(X, y, models, scoring):
    """
    Return 10-Fold Cross Validation scores for various models in addition to
    box plots for each of the 10 fold models.

    Args:
        X: Feature matrix
        y: Target vector
        models: Dictionary of models with the model name as the key and the
        instantiated model as the value.
        scoring: Str of the scoring to use (i.e., 'accuracy')
    Returns:
        Scores: 10-Fold Cross Validation scores for all models.
        Plot: Boxplot of all 5-fold model scores.
    """
    seed = 123
    results = []
    names = []
    all_scores = []
    print('Mod - Avg - Std Dev')
    print('---   ---   -------')
    for name, model in models.items():
        kfold = KFold(n_splits=10, random_state=seed)
        cv_results = cross_val_score(model, X, y, cv=kfold, scoring=scoring)
        results.append([np.sqrt(abs(x)) for x in cv_results])
        names.append(name)
        all_scores.append(np.array([np.sqrt(abs(x)) for x in cv_results]).mean())
        print('{}: {:.2f} ({:2f})'.format(name, np.array([np.sqrt(abs(x)) for x in cv_results]).mean(),
                                                np.array([np.sqrt(abs(x)) for x in cv_results]).std()))
    print('Avg of all: {:.3f}'.format(np.mean(all_scores)))
    fig = plt.figure(figsize=(20, 7))
    fig.suptitle('Model Selection\nCross Validation Scores')
    ax = fig.add_subplot(111)
    plt.boxplot(results)
    ax.set_xticklabels(names, rotation=20, fontsize=10)
    # ax.set_ylim([0.5,1])
    ax.set_ylabel('10-Fold CV RMSE Score')
    ax.set_xlabel('Model')
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.show()

def load_model_input(source):
    """
    box_score_inputs
    box_score_3WAVG_inputs
    box_score_league_percentiles
    box_score_position_percentiles
    other_inputs
    """
    # Read in Data
    model_input = pd.read_csv('../feature_selection/featurized_inputs/{0}.csv'.format(source))
    # Filter to Season+1 target
    model_input = model_input[model_input['SEASON_PLUS_1'].notnull()]
    # Drop Irrelevant Columns
    drop_columns = ['BLEND', 'SEASON_PLUS_2', 'SEASON_PLUS_3',
           'SEASON_PLUS_4', 'SEASON_PLUS_5', 'TEAM',
           'G', 'GS', 'FG', 'FGA', 'FG%', '3P',
           '3PA', '3P%', '2P', '2PA', '2P%', 'FT', 'FTA',
           'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK',
           'TOV', 'PF', 'PTS', 'G_3WAVG', 'GS_3WAVG',
       'MP_3WAVG', 'FG_3WAVG', 'FGA_3WAVG', 'FG%_3WAVG', '3P_3WAVG',
       '3PA_3WAVG', '3P%_3WAVG', '2P_3WAVG', '2PA_3WAVG', '2P%_3WAVG',
       'EFG%_3WAVG', 'FT_3WAVG', 'FTA_3WAVG', 'FT%_3WAVG', 'ORB_3WAVG',
       'DRB_3WAVG', 'TRB_3WAVG', 'AST_3WAVG', 'STL_3WAVG', 'BLK_3WAVG',
       'TOV_3WAVG', 'PF_3WAVG', 'PTS_3WAVG', 'GAMES_PLAYER_PERCENTILE_ALL', 'GAMES_STARTED_PERCENTILE_ALL',
       'MINUTES_PERCENTILE_ALL', 'FG_PERCENTILE_ALL', 'FGA_PERCENTILE_ALL',
       'FG_PERCENT_PERCENTILE_ALL', 'THREE_POINT_MADE_PERCENTILE_ALL',
       'THREE_POINT_ATTEMPT_PERCENTILE_ALL',
       'THREE_POINT_PERCENT_PERCENTILE_ALL', 'TWO_POINT_MADE_PERCENTILE_ALL',
       'TWO_POINT_ATTEMPT_PERCENTILE_ALL', 'TWO_POINT_PERCENT_PERCENTILE_ALL',
       'EFG_PERCENT_PERCENTILE_ALL', 'TRUE_SHOOTING_PERCENT_PERCENTILE_ALL',
       'FREE_THROW_MADE_PERCENTILE_ALL', 'FREE_THROW_ATTEMPT_PERCENTILE_ALL',
       'FREE_THROW_PERCENT_PERCENTILE_ALL', 'OREB_PERCENTILE_ALL',
       'DRB_PERCENTILE_ALL', 'TOTAL_PERCENTILE_ALL', 'AST_PERCENTILE_ALL',
       'STL_PERCENTILE_ALL', 'BLK_PERCENTILE_ALL', 'TURNOVER_PERCENTILE_ALL',
       'FOUL_PERCENTILE_ALL', 'POINTS_PERCENTILE_ALL', 'GAMES_PLAYER_PERCENTILE_POSITION',
       'GAMES_STARTED_PERCENTILE_POSITION', 'MINUTES_PERCENTILE_POSITION',
       'FG_PERCENTILE_POSITION', 'FGA_PERCENTILE_POSITION',
       'FG_PERCENT_PERCENTILE_POSITION',
       'THREE_POINT_MADE_PERCENTILE_POSITION',
       'THREE_POINT_ATTEMPT_PERCENTILE_POSITION',
       'THREE_POINT_PERCENT_PERCENTILE_POSITION',
       'TWO_POINT_MADE_PERCENTILE_POSITION',
       'TWO_POINT_ATTEMPT_PERCENTILE_POSITION',
       'TWO_POINT_PERCENT_PERCENTILE_POSITION',
       'EFG_PERCENT_PERCENTILE_POSITION',
       'TRUE_SHOOTING_PERCENT_PERCENTILE_POSITION',
       'FREE_THROW_MADE_PERCENTILE_POSITION',
       'FREE_THROW_ATTEMPT_PERCENTILE_POSITION',
       'FREE_THROW_PERCENT_PERCENTILE_POSITION', 'OREB_PERCENTILE_POSITION',
       'DRB_PERCENTILE_POSITION', 'TOTAL_PERCENTILE_POSITION',
       'AST_PERCENTILE_POSITION', 'STL_PERCENTILE_POSITION',
       'BLK_PERCENTILE_POSITION', 'TURNOVER_PERCENTILE_POSITION',
       'FOUL_PERCENTILE_POSITION', 'POINTS_PERCENTILE_POSITION',
       'GAMES_PLAYED', 'MINUTES_PLAYED',
       'ON_COURT_PLUS_MINUS', 'OFF_COURT_PLUS_MINUS', 'POSITION_MINUTES']
    model_input.drop([col for col in drop_columns if col in model_input.columns], axis=1, inplace=True)
    return model_input


if __name__=='__main__':
    model_input = load_model_input('other_inputs')

    # Train/Test Split
    y = model_input.pop('SEASON_PLUS_1')
    X = model_input.drop([col for col in ['BBREF_ID', 'SEASON', 'PLAYER', 'POSITION', 'ADVANCED_POSITION_CLUSTER'] if col in model_input], axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25, random_state=10)

    # Standardize Data
    train_scaler, test_scaler = StandardScaler(), StandardScaler()
    X_train, X_test = train_scaler.fit_transform(X_train), test_scaler.fit_transform(X_test)

    # Perform 10-fold cross validation across five seperate model types
    # using default parameters
    models = {'Ridge Regularized Regression':
              Ridge(),

              'Lasso Regularized Regression':
              Lasso(),

              'Elastic Net Regularized Regression':
              ElasticNet(),

              'Random Forest':
              RandomForestRegressor(),

              'Gradient Boosting':
              GradientBoostingRegressor()}

    plot_cross_validation(X_train, y_train, models, 'neg_mean_squared_error')
