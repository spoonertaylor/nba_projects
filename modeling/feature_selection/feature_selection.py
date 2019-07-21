# Project: Feature Selection
# Description: Investigate relationships between various predictor
# variables and the player projection target variable. Determine best subset
# of predictors to use in the model.
# Data Sources: Basketball-Reference and ESPN
# Last Updated: 7/19/2019

import numpy as np
import pandas as pd
import imgkit
import random
import os

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

def dataFrame_to_image(data, css, outputfile="corr_df.png", format="png"):
    '''
    Render a Pandas DataFrame as an image. Adopted from :
    https://medium.com/@andy.lane/convert-pandas-dataframes-to-images-using-imgkit-5da7e5108d55

    Args:
        data: a pandas DataFrame
        css: a string containing rules for styling the output table. This must
             contain both the opening an closing <style> tags.
    Return:
        *outputimage: filename for saving of generated image
        *format: output format, as supported by IMGKit. Default is "png"
    '''
    fn = str(random.random()*100000000).split(".")[0] + ".html"

    try:
        os.remove(fn)
    except:
        None
    text_file = open(fn, "a")

    # write the CSS
    text_file.write(css)
    # write the HTML-ized Pandas DataFrame
    text_file.write(data.to_html(index=False))
    text_file.close()

    # See IMGKit options for full configuration,
    # e.g. cropping of final image
    imgkitoptions = {"format": format}

    imgkit.from_file(fn, outputfile, options=imgkitoptions)
    os.remove(fn)


if __name__=='__main__':
    # Read in featurized Basketball-Reference Box Score Data
    bbref_box_score = pd.read_csv('featurized_inputs/bbref_box_scores.csv')
    # Filter to SEASON_PLUS_1 target variable and drop other targets
    bbref_box_score = (bbref_box_score[bbref_box_score['SEASON_PLUS_1'].notnull()]
                        .drop(['BLEND', 'SEASON_PLUS_2', 'SEASON_PLUS_3',
                               'SEASON_PLUS_4', 'SEASON_PLUS_5'], axis=1))

    # Calculate predictor correlations with target variable
    corr_df = calculate_target_correlations(bbref_box_score, 'SEASON_PLUS_1')

    # Save .png of correlations with background gradient
    styled_table = (corr_df[['STATISTIC', 'PEARSON_CORRELATION', 'SPEARMAN_CORRELATION', 'AVERAGE_RANK']]
                     .style
                     .hide_index()
                    #  .background_gradient(subset=['PEARSON_CORRELATION', 'SPEARMAN_CORRELATION'], cmap='RdBu_r')
                     .background_gradient(subset=['AVERAGE_RANK'], cmap='RdBu'))
    html = styled_table.render()
    imgkit.from_string(html, 'plots/correlation_table_gradient.png')

    # Save .png of correlations w/o background gradient
    css = """
        <style type=\"text/css\">
        table {
        color: #333;
        font-family: Helvetica, Arial, sans-serif;
        width: 640px;
        border-collapse:
        collapse;
        border-spacing: 0;
        }
        td, th {
        border: 1px solid transparent; /* No more visible border */
        height: 30px;
        }
        th {
        background: #DFDFDF; /* Darken header a bit */
        font-weight: bold;
        }
        td {
        background: #FAFAFA;
        text-align: center;
        }
        table tr:nth-child(odd) td{
        background-color: white;
        }
        </style>
        """
    dataFrame_to_image(corr_df, css, outputfile="plots/correlation_table.png", format="png")
