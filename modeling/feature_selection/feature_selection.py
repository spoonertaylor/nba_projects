# Project: Feature Selection
# Description: Investigate relationships between various predictor
# variables and the player projection target variable. Determine best subset
# of predictors to use in the model.
# Data Sources: Basketball-Reference and ESPN
# Last Updated: 7/19/2019

import numpy as np
import pandas as pd
import imgkit
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

def calculate_target_correlations(df, target):
    # Calculate pearson correlation of all numerical metrics in df
    pearson_corr_df = df.corr(method='pearson')
    # Select only correlations with target variable
    pearson_corr_df = pearson_corr_df[target].reset_index()
    pearson_corr_df.columns = ['STATISTIC', 'PEARSON_CORRELATION']
    # Calculate absolute value of pearson correlation to create rank order of metrics
    pearson_corr_df['PEARSON_CORRELATION_ABS'] = abs(pearson_corr_df['PEARSON_CORRELATION'])

    # Calculate spearman correlation of all numberical metrics in df
    spearman_corr_df = df.corr(method='spearman')
    # Select only correlations with target variable
    spearman_corr_df = spearman_corr_df[target].reset_index()
    spearman_corr_df.columns = ['STATISTIC', 'SPEARMAN_CORRELATION']
    # Calculate absolute value of spearman correlation to create rank order of metrics
    spearman_corr_df['SPEARMAN_CORRELATION_ABS'] = abs(spearman_corr_df['SPEARMAN_CORRELATION'])

    # Join pearson and spearman correlations
    corr_df = (pearson_corr_df.merge(spearman_corr_df, on='STATISTIC')
                              .sort_values(by='PEARSON_CORRELATION_ABS', ascending=False)
                              .dropna()
                              .round(3))
    # Remove irrelivent metric RANK and target variable as that will always have
    # a perfect correlation with itself
    corr_df = corr_df[~corr_df['STATISTIC'].isin(['RANK', target])]
    # Create rank of relationship strength based on absolute value of pearson correlation
    corr_df['PEARSON_CORRELATION_RANK'] = range(1, 1+len(corr_df))
    corr_df.sort_values(by='SPEARMAN_CORRELATION_ABS', ascending=False, inplace=True)
    # Create rank of relationship strength based on absolute value of spearman correlation
    corr_df['SPEARMAN_CORRELATION_RANK'] = range(1, 1+len(corr_df))
    # Create an average rank based on correlation ranks
    corr_df['AVERAGE_RANK'] = (corr_df[['PEARSON_CORRELATION_RANK',
                                        'SPEARMAN_CORRELATION_RANK']]
                                            .mean(axis=1)
                                            .round(1))
    corr_df.sort_values(by='AVERAGE_RANK', inplace=True)
    corr_df = corr_df[['STATISTIC', 'PEARSON_CORRELATION',
                       'PEARSON_CORRELATION_ABS', 'SPEARMAN_CORRELATION',
                       'SPEARMAN_CORRELATION_ABS', 'PEARSON_CORRELATION_RANK',
                       'SPEARMAN_CORRELATION_RANK', 'AVERAGE_RANK']]

    return corr_df

def plot_correlation_matrix(df, title):
    """
    Plot correlation matrix of top-15 features that are most correlated with
    NBA_VORP
    Args:
        df: cleaned training dataframe
    Returns:
        Plotted correlation matrix of top-15 features that are most correlated
        with NBA_VORP
    """
    corr = df.corr()
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
    f, ax = plt.subplots(figsize=(12,8))
    cmap = sns.color_palette('coolwarm')
    sns.heatmap(corr, mask=mask, cmap=cmap, center=0, square=True, linewidths=.5,
                yticklabels=True, annot=True, fmt='.2f', cbar_kws={'shrink':.5},
                annot_kws={"size": 7})
    plt.title(title)
    plt.xticks(rotation=90, fontsize=7)
    plt.yticks(rotation=0, fontsize=7)
    plt.tight_layout()
    plt.show()

def permutation_importance(df, target, predictors):
    # Train/Test Split
    df_train, df_test = train_test_split(df, test_size=0.2)
    X_train, y_train = df_train[predictors], df_train['SEASON_PLUS_1']
    X_test, y_test = df_test[predictors], df_test['SEASON_PLUS_1']

    # Add random column
    X_train['RANDOM'] = np.random.random(size=len(X_train))
    X_test['RANDOM'] = np.random.random(size=len(X_test))
    predictors.append('RANDOM')

    # Fit and score baseline model
    rf = RandomForestRegressor()
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    baseline_score = np.sqrt(mean_squared_error(y_test, y_pred))

    scores = {}
    # Loop through columns, randomizing each and re-scoring model
    for col in predictors:
        temp_df = X_test.copy()
        temp_df[[col]] = np.random.permutation(temp_df[[col]].values)
        y_pred = rf.predict(temp_df)
        scores[col] = round(np.sqrt(mean_squared_error(y_test, y_pred)), 4)

    scores_df = pd.DataFrame.from_dict(scores, orient='index')\
                            .reset_index()
    scores_df['baseline_diff'] = round(scores_df[0] - baseline_score, 4)
    scores_df.columns = ['FIELD', 'RMSE', 'BASELINE_DIFFERENCE']
    scores_df.sort_values(by='BASELINE_DIFFERENCE', ascending=False, inplace=True)
    return scores_df


if __name__=='__main__':
    # Read in featurized Basketball-Reference Box Score Data
    bbref_box_score = pd.read_csv('featurized_inputs/bbref_box_scores.csv')
    # Filter to SEASON_PLUS_1 target variable and drop other targets
    bbref_box_score = (bbref_box_score[bbref_box_score['SEASON_PLUS_1'].notnull()]
                        .drop(['BLEND', 'SEASON_PLUS_2', 'SEASON_PLUS_3',
                               'SEASON_PLUS_4', 'SEASON_PLUS_5'], axis=1))


    # Calculate predictor correlations with target variable
    corr_df = calculate_target_correlations(bbref_box_score, 'SEASON_PLUS_1')

    # # Save .png of correlations with background gradient
    styled_table = (corr_df[['STATISTIC', 'PEARSON_CORRELATION', 'SPEARMAN_CORRELATION', 'AVERAGE_RANK']]
                     .style
                     .set_table_styles(
                    [{'selector': 'tr:nth-of-type(odd)',
                      'props': [('background', '#eee')]},
                     {'selector': 'tr:nth-of-type(even)',
                      'props': [('background', 'white')]},
                     {'selector':'th, td', 'props':[('text-align', 'center')]}])
                     .set_properties(subset=['STATISTIC'], **{'text-align': 'left'})
                     .hide_index()
                     .background_gradient(subset=['AVERAGE_RANK'], cmap='RdBu'))
    html = styled_table.render()
    imgkit.from_string(html, 'plots/correlation_table.png', {'width': 1})

    plot_correlation_matrix(bbref_box_score[['SEASON_PLUS_1', 'G', 'GS', 'MP',
                                                'FG', 'FGA', 'FG%', '3P', '3PA',
                                                '3P%', '2P','2PA', '2P%', 'EFG%',
                                                'FT', 'FTA', 'FT%', 'ORB', 'DRB',
                                                'TRB', 'AST', 'STL', 'BLK', 'TOV',
                                                'PF', 'PTS']], 'Totals Correlation Matrix')

    plot_correlation_matrix(bbref_box_score[['SEASON_PLUS_1', 'PER100_FG', 'PER100_FGA',
       'PER100_FG%', 'PER100_3P', 'PER100_3PA', 'PER100_3P%', 'PER100_2P',
       'PER100_2PA', 'PER100_2P%', 'PER100_FT', 'PER100_FTA', 'PER100_FT%',
       'PER100_ORB', 'PER100_DRB', 'PER100_TRB', 'PER100_AST', 'PER100_STL',
       'PER100_BLK', 'PER100_TOV', 'PER100_PF', 'PER100_PTS', 'PER100_ORTG',
       'PER100_DRTG']], 'Per 100 Possessions Correlation Matrix')

    plot_correlation_matrix(bbref_box_score[['SEASON_PLUS_1', 'PER', 'TS%', '3PA_RATE', 'FT_RATE',
                                            'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%',
                                            'BLK%', 'TOV%', 'USG%', 'OWS', 'DWS', 'WS',
                                            'WS/48', 'OBPM', 'DBPM', 'BPM', 'VORP']],
                                            'Advanced Correlation Matrix')

    # Drop-One Feature Importance
    predictors = ['G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P',
       '2PA', '2P%', 'EFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST',
       'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PER100_FG', 'PER100_FGA',
       'PER100_FG%', 'PER100_3P', 'PER100_3PA', 'PER100_3P%', 'PER100_2P',
       'PER100_2PA', 'PER100_2P%', 'PER100_FT', 'PER100_FTA', 'PER100_FT%',
       'PER100_ORB', 'PER100_DRB', 'PER100_TRB', 'PER100_AST', 'PER100_STL',
       'PER100_BLK', 'PER100_TOV', 'PER100_PF', 'PER100_PTS', 'PER100_ORTG',
       'PER100_DRTG', 'PER', 'TS%', '3PA_RATE', 'FT_RATE', 'ORB%', 'DRB%',
       'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'OWS', 'DWS', 'WS',
       'WS/48', 'OBPM', 'DBPM', 'BPM', 'VORP']
    scores = permutation_importance(bbref_box_score, 'SEASON_PLUS_1', predictors)
    styled_scores = (scores
                     .style
                     .set_table_styles(
                     [{'selector': 'tr:nth-of-type(odd)',
                       'props': [('background', '#eee')]},
                      {'selector': 'tr:nth-of-type(even)',
                       'props': [('background', 'white')]},
                      {'selector':'th, td', 'props':[('text-align', 'center')]}])
                     .set_properties(subset=['FIELD'], **{'text-align': 'left'})
                     .hide_index()
                     .background_gradient(subset=['BASELINE_DIFFERENCE'], cmap='Reds'))
    html = styled_scores.render()
    imgkit.from_string(html, 'plots/permutation_importance.png', {'width': 1})
