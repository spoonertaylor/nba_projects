# Project: Feature Selection
# Description: Investigate relationships between various predictor
# variables and the player projection target variable. Determine best subset
# of predictors to use in the model.
# Data Sources: Basketball-Reference and ESPN
# Last Updated: 7/18/2019

import numpy as np
import pandas as pd

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

# Correlation Table
# Correlation Matrix
# LR Coefficients
# Dependency Plots
# Drop-One Importance (eli5)


if __name__=='__main__':
    # Read in featurized Basketball-Reference Box Score Data
    bbref_box_score = pd.read_csv('featurized_inputs/bbref_box_scores.csv')
    # Filter to SEASON_PLUS_1 target variable and drop other targets
    bbref_box_score = (bbref_box_score[bbref_box_score['SEASON_PLUS_1'].notnull()]
                        .drop(['BLEND', 'SEASON_PLUS_2', 'SEASON_PLUS_3',
                               'SEASON_PLUS_4', 'SEASON_PLUS_5'], axis=1))

    corr_df = calculate_target_correlations(bbref_box_score, 'SEASON_PLUS_1')
