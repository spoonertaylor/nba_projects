# Project: Player Projection Model (Chris)
# Description: Build model to predict a player's RPM/BPM blend one season in the
# future. Investigate feature importances.
# Data Sources: Basketball-Reference and ESPN
# Last Updated: 7/31/2019

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
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error

# Avoid XGBoost Initialization Error
os.environ['KMP_DUPLICATE_LIB_OK']='True'

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

if __name__=='__main__':
    # Read in featurized Basketball-Reference Totals, Per 100, and Advanced Data
    bbref_box_score = pd.read_csv('../feature_selection/featurized_inputs/box_score_inputs.csv')
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
              GradientBoostingRegressor(),

              'XGBoost':
              XGBRegressor(),

              'CatBoost':
              CatBoostRegressor()}

    plot_cross_validation(X_train, y_train, models, 'neg_mean_squared_error')

    # Gridsearch Ridge Model
    # (Best performing regularized regression model in CV process above)
    ridge = Ridge()
    param_list = {'alpha': np.arange(0.5, 5, 0.1),
                  'tol': np.arange(0.00001, 0.1, 0.001),
                  'solver': ['auto', 'svd', 'cholesky', 'lsqr',
                  'sparse_cg', 'sag', 'saga']}
    ridge_grid = GridSearchCV(ridge, param_list, scoring='neg_mean_squared_error',
                     cv=5, n_jobs=-1, verbose=0)
    ridge_grid.fit(X_train, y_train)
    print('Model: {}, Best Params: {}, Best Score: {}'\
            .format(ridge, ridge_grid.best_params_, np.sqrt(abs(ridge_grid.best_score_))))
    # Best Params: {'alpha': 4.1, 'solver': 'sag', 'tol': 0.07901}
    # Best Score: 1.8190340847310862

    # Gridsearch Gradient Boosted Model
    # (Best performing model overall in CV process above)
    gb = GradientBoostingRegressor()
    param_list = {'loss': ['ls', 'lad', 'huber', 'quantile'],
                  'learning_rate':np.arange(0.1, 1.0, 0.2),
                  'n_estimators': np.arange(10, 1000, 100),
                  'max_depth': np.arange(2, 6, 2),
                  'warm_start': [True, False]}
    gb_grid = GridSearchCV(gb, param_list, scoring='neg_mean_squared_error',
                     cv=5, n_jobs=-1, verbose=1)
    gb_grid.fit(X_train, y_train)
    print('Model: {}, Best Params: {}, Best Score: {}'\
        .format(gb, gb_grid.best_params_, np.sqrt(abs(gb_grid.best_score_))))
    # Best Params: {'learning_rate': 0.1, 'loss': 'huber', 'max_depth': 2, 'n_estimators': 110, 'warm_start': True}
    # Best Score: 1.8422979097062397

    # Re-fit Final Ridge Model to examine coefficients
    final_ridge = Ridge(alpha=4.1, solver='sag', tol=0.07901)
    final_ridge.fit(X_train, y_train)
    y_pred = final_ridge.predict(X_test)
    print('Test RMSE Score: {}'.format(np.sqrt(mean_squared_error(y_test, y_pred))))
    # Test RMSE Score: 1.95

    # Create table of coefficients from final ridge model to examine feature
    # importance.
    coefs = list(final_ridge.coef_)
    features = list(X.columns)
    importances = [[x, y] for x, y in zip(features, coefs)]
    importances.sort(key=lambda row: abs(row[1]), reverse=True)
    feature_importances = pd.DataFrame(importances)
    feature_importances.columns = ['FEATURE', 'COEFFICIENT']
    # Save table in pandas styling format
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
    imgkit.from_string(html, 'plots/feature_importance.png', {'width': 1})

    # Make Predictions on Final Gradient Boosted Model
    final_gb = GradientBoostingRegressor(learning_rate=0.1,
                                         loss='huber',
                                         max_depth=2,
                                         n_estimators=110,
                                         warm_start=True)
    final_gb.fit(X_train, y_train)
    # Save model to pickle file
    # Can load same model via `loaded_model = pickle.load(open(filename, 'rb'))`
    pickle.dump(final_gb, open('model/chris_player_projection_model.sav', 'wb'))
    y_pred = final_gb.predict(X_test)
    print('Test RMSE Score: {}'.format(np.sqrt(mean_squared_error(y_test, y_pred))))
    # Test RMSE Score: 1.8997970102036106

    # Make predictions for 2019-2020 season
    most_recent_season = pd.read_csv('../feature_selection/featurized_inputs/bbref_box_scores.csv')
    most_recent_season = most_recent_season[most_recent_season['SEASON']=='2018-2019']
    X = most_recent_season[['AGE', 'MP', 'EFG%', 'PER100_FG', 'PER100_FGA', 'PER100_FG%',
       'PER100_3P', 'PER100_3PA', 'PER100_3P%', 'PER100_2P', 'PER100_2PA',
       'PER100_2P%', 'PER100_FT', 'PER100_FTA', 'PER100_FT%', 'PER100_ORB',
       'PER100_DRB', 'PER100_TRB', 'PER100_AST', 'PER100_STL', 'PER100_BLK',
       'PER100_TOV', 'PER100_PF', 'PER100_PTS', 'PER100_ORTG', 'PER100_DRTG',
       'PER', 'TS%', '3PA_RATE', 'FT_RATE', 'ORB%', 'DRB%', 'TRB%', 'AST%',
       'STL%', 'BLK%', 'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/48', 'OBPM',
       'DBPM', 'BPM', 'VORP']]
    # Scale data
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    season_plus1_predictions = final_gb.predict(X)
    most_recent_season['PREDICTION'] = season_plus1_predictions
    most_recent_season.sort_values(by='PREDICTION',
                                      ascending=False, inplace=True)
    most_recent_season = most_recent_season[['BBREF_ID', 'PLAYER', 'AGE', 'SEASON', 'ADVANCED_POSITION_CLUSTER', 'PREDICTION']]
    # Save full predictions table
    most_recent_season.to_csv('predictions/predictions.csv', index=False)
    # Save top-25 predictions table in pandas styling format
    styled_top25 = (most_recent_season.iloc[0:25, 1:]
                     .style
                     .set_table_styles(
                     [{'selector': 'tr:nth-of-type(odd)',
                       'props': [('background', '#eee')]},
                      {'selector': 'tr:nth-of-type(even)',
                       'props': [('background', 'white')]},
                      {'selector':'th, td', 'props':[('text-align', 'center')]}])
                     .set_properties(subset=['BBREF_ID',
                                            'PLAYER',
                                            'AGE',
                                            'SEASON',
                                            'ADVANCED_POSITION_CLUSTER'],
                                    **{'text-align': 'left'})
                     .hide_index()
                     .background_gradient(subset=['PREDICTION'], cmap='Reds'))
    html = styled_top25.render()
    imgkit.from_string(html, 'plots/top_25predictions.png', {'width': 1})

    # Save bottom-25 predictions table in pandas styling format
    styled_bottom25 = (most_recent_season.iloc[-25:, 1:]
                     .style
                     .set_table_styles(
                     [{'selector': 'tr:nth-of-type(odd)',
                       'props': [('background', '#eee')]},
                      {'selector': 'tr:nth-of-type(even)',
                       'props': [('background', 'white')]},
                      {'selector':'th, td', 'props':[('text-align', 'center')]}])
                     .set_properties(subset=['BBREF_ID',
                                            'PLAYER',
                                            'AGE',
                                            'SEASON',
                                            'ADVANCED_POSITION_CLUSTER'],
                                    **{'text-align': 'left'})
                     .hide_index()
                     .background_gradient(subset=['PREDICTION'], cmap='Blues_r'))
    html = styled_bottom25.render()
    imgkit.from_string(html, 'plots/bottom_25predictions.png', {'width': 1})
