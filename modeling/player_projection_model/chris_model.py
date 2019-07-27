# Project: Player Projection Model (Chris)
# Description: Build model(s) to predict a player's RPM/BPM blend one season in the
# future. Investigate feature importances.
# Data Sources: Basketball-Reference and ESPN
# Last Updated: 7/26/2019

import numpy as np
import pandas as pd
import imgkit
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso, Ridge, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error

import warnings
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)

if __name__=='__main__':
    # Read in featurized Basketball-Reference Box Score Data
    bbref_box_score = pd.read_csv('../feature_selection/featurized_inputs/bbref_box_scores.csv')
    # Filter to SEASON_PLUS_1 target variable
    # Drop other target variables and raw total columns
    bbref_box_score = (bbref_box_score[bbref_box_score['SEASON_PLUS_1'].notnull()]
                        .drop(['BLEND', 'SEASON_PLUS_2', 'SEASON_PLUS_3',
                               'SEASON_PLUS_4', 'SEASON_PLUS_5', 'TEAM',
                               'G', 'GS', 'FG', 'FGA', 'FG%', '3P',
                               '3PA', '3P%', '2P', '2PA', '2P%', 'FT', 'FTA',
                               'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK',
                               'TOV', 'PF', 'PTS'], axis=1))

    # Train/Test Split
    y = bbref_box_score.pop('SEASON_PLUS_1')
    X = bbref_box_score.drop(['BBREF_ID', 'SEASON', 'PLAYER', 'POSITION', 'ADVANCED_POSITION_CLUSTER'], axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.25, random_state=10)

    # Standardize Data
    train_scaler, test_scaler = StandardScaler(), StandardScaler()
    X_train, X_test = train_scaler.fit_transform(X_train), test_scaler.fit_transform(X_test)

    # Regularized Regression
    ridge = Ridge()
    param_list = {'alpha': np.linspace(.1, 1, 10),
                    'solver': ['auto', 'svd', 'lsqr', 'cholesky']}
    ridge_grid = GridSearchCV(ridge, param_list, scoring='neg_mean_squared_error',
                     cv=5)
    ridge_grid.fit(X_train, y_train)
    print('Model: {}, Best Params: {}, Best Score: {}'\
            .format(ridge, ridge_grid.best_params_, np.sqrt(abs(ridge_grid.best_score_))))

    # Lasso Regression
    lasso = Lasso()
    param_list = {'alpha': np.linspace(.1, 1, 10)}
    lasso_grid = GridSearchCV(lasso, param_list, scoring='neg_mean_squared_error',
                     cv=5)
    lasso_grid.fit(X_train, y_train)
    print('Model: {}, Best Params: {}, Best Score: {}'\
        .format(lasso, lasso_grid.best_params_, np.sqrt(abs(lasso_grid.best_score_))))

    # ElasticNet Model
    elastic = ElasticNet()
    param_list = {'alpha': np.linspace(0.5, 0.9, 20),
                  'l1_ratio': np.linspace(0.9, 1.0, 10)}
    elastic_grid = GridSearchCV(elastic, param_list, scoring='neg_mean_squared_error',
                     cv=5)
    elastic_grid.fit(X_train, y_train)
    print('Model: {}, Best Params: {}, Best Score: {}'\
        .format(elastic, elastic_grid.best_params_, np.sqrt(abs(elastic_grid.best_score_))))

    # Re-fit Lasso w/o Cross-Validation
    final_model = Lasso(alpha=0.1)
    final_model.fit(X_train, y_train)
    y_pred = final_model.predict(X_test)
    print('Validation RMSE Score: {}'.format(np.sqrt(mean_squared_error(y_test, y_pred))))
    # Validation MSE Score: 1.91

    # Examine Coefficients
    coefs = list(final_model.coef_)
    features = list(X.columns)
    importances = [[x, y] for x, y in zip(features, coefs)]
    importances.sort(key=lambda row: abs(row[1]), reverse=True)
    feature_importances = pd.DataFrame(importances)
    feature_importances.columns = ['FEATURE', 'COEFFICIENT']

    styled_feature_importances = (feature_importances
                     .style
                     .set_table_styles(
                     [{'selector': 'tr:nth-of-type(odd)',
                       'props': [('background', '#eee')]},
                      {'selector': 'tr:nth-of-type(even)',
                       'props': [('background', 'white')]},
                      {'selector':'th, td', 'props':[('text-align', 'center')]}])
                     .set_properties(subset=['FEATURE'], **{'text-align': 'left'})
                     .hide_index()
                     .background_gradient(subset=['COEFFICIENT'], cmap='Reds'))
    html = styled_feature_importances.render()
    imgkit.from_string(html, 'feature_importance.png', {'width': 1})
