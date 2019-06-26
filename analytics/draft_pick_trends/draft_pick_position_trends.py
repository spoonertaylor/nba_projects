# Project: Draft Pick Position Trends
# Description: Visualize positional trend of NBA draft picks since 2006.
# Data Sources: RealGM
# Last Updated: 6/24/2019

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Plotting Style
plt.style.use('fivethirtyeight')

def clean_position(row):
    '''
    Clean RealGM positional designations transforming edge cases of FC and GF to
    PF and SF.

    Args:
        row: Individual player record.

    Returns:
        row: Individual player record with transformed position.
    '''
    if row=='FC':
        return 'PF'
    elif row=='GF':
        return 'SF'
    else:
        return row

def group_position(row):
    '''
    Classify cleaned RealGM positional designations into positional
    grouping of guard, wing, center.

    Args:
        row: Individual player record.

    Returns:
        row: Individual player record with positional grouping.
    '''
    if row in ['PG', 'G']:
        return 'Guards: (PG and G)'
    elif row in ['SG', 'SF', 'F']:
        return 'Wings: (SG, SF, and F)'
    elif row in ['PF', 'C']:
        return 'Bigs: (PF, C)'
    else:
        return 'MISSING'

if __name__=='__main__':
    # Read in draft data (2006-2019)
    draft_df = pd.read_csv('../../data/nba/real_gm/draft_selections.csv')[['Year', 'Rnd', 'Pick', 'Player',
    'Team', 'Pos', 'Height', 'Weight','Age']]


    # Clean Positional Classification
    draft_df['Position_Long'] = draft_df['Pos']
    draft_df['Position_Short'] = draft_df['Position_Long'].str.split('/').str[0]
    draft_df['Position_Short'] = draft_df['Position_Short'].str.split('-').str[0]
    draft_df['Position_Short'] = draft_df['Position_Short'].apply(clean_position)
    draft_df['Position_Group'] = draft_df['Position_Short'].apply(group_position)

    # Position Counts
    pos_short = draft_df.groupby(['Year', 'Position_Short']).count().reset_index()[['Year', 'Position_Short', 'Player']]
    pos_short.columns = ['Year', 'Position', 'Count']
    pos_group = draft_df.groupby(['Year', 'Position_Group']).count().reset_index()[['Year', 'Position_Group', 'Player']]
    pos_group.columns = ['Year', 'Position', 'Count']

    # Color Palettes
    fivethirtyeight = ['#30a2da', '#fc4f30', '#e5ae38']
    fivethirtyeight_reorder = ['#30a2da', '#e5ae38', '#fc4f30', ]
    all_positions = ['#956cb4', '#8b8b8b', '#fd9a42', '#6d904f', '#30a2da', '#e5ae38', '#d65f5f']
    bigs = ['#956cb4', '#6d904f']
    wings = ['#8b8b8b', '#e5ae38', '#d65f5f']
    guards = ['#fd9a42', '#30a2da']

    # Plot Draft Picks by Position (All Positions)
    fig, ax = plt.subplots(figsize=(18, 5))
    sns.lineplot(x='Year', y='Count', hue='Position', data=pos_short, palette=all_positions)
    ax.set_xticks(np.arange(2006, 2020))
    ax.set_yticks(np.arange(0, 21, 3))
    ax.set_xlabel('Draft')
    ax.set_ylabel('Draft Picks')
    plt.legend(prop={'size': 8})
    plt.title('Draft Picks by Position')
    plt.tight_layout()
    plt.show()

    # Plot Draft Picks by Position (C and PF)
    fig, ax = plt.subplots(figsize=(18, 5))
    sns.lineplot(x='Year', y='Count', hue='Position', data=pos_short[pos_short['Position'].isin(['C', 'PF'])], palette=bigs)
    ax.set_xticks(np.arange(2006, 2020))
    ax.set_yticks(np.arange(0, 21, 3))
    ax.set_xlabel('Draft')
    ax.set_ylabel('Draft Picks')
    plt.legend(prop={'size': 8})
    plt.title('Centers, and Power Forwards')
    plt.tight_layout()
    plt.show()

    # Plot Draft Picks by Position (PG and G)
    fig, ax = plt.subplots(figsize=(18, 5))
    sns.lineplot(x='Year', y='Count', hue='Position', data=pos_short[pos_short['Position'].isin(['PG', 'G'])], palette=guards)
    ax.set_xticks(np.arange(2006, 2020))
    ax.set_yticks(np.arange(0, 21, 3))
    ax.set_xlabel('Draft')
    ax.set_ylabel('Draft Picks')
    plt.legend(prop={'size': 8})
    plt.title('Point Guards and Guards (Combo)')
    plt.tight_layout()
    plt.show()

    # Plot Draft Picks by Position (SG, SF, F)
    fig, ax = plt.subplots(figsize=(18, 5))
    sns.lineplot(x='Year', y='Count', hue='Position', data=pos_short[pos_short['Position'].isin(['SG', 'SF', 'F'])], palette=wings)
    ax.set_xticks(np.arange(2006, 2020))
    ax.set_yticks(np.arange(0, 21, 3))
    ax.set_xlabel('Draft')
    ax.set_ylabel('Draft Picks')
    plt.legend(prop={'size': 8})
    plt.title('Shooting Guards, Small Forwards, and Forwards')
    plt.tight_layout()
    plt.show()

    # Plot Draft Picks by Positional Groupings
    fig, ax = plt.subplots(figsize=(18, 5))
    sns.lineplot(x='Year', y='Count', hue='Position', data=pos_group, palette=fivethirtyeight)
    ax.set_xticks(np.arange(2006, 2020))
    ax.set_yticks(np.arange(0, 35, 5))
    ax.set_xlabel('Draft')
    ax.set_ylabel('Draft Picks')
    plt.legend(prop={'size': 10})
    plt.title('Draft Picks by Positional Grouping')
    plt.tight_layout()
    plt.show()

    # Picks by Positional Grouping Across Time
    fig, ax = plt.subplots(figsize=(18, 5))
    sns.swarmplot(x='Year', y='Pick', hue='Position_Group', data=draft_df, palette=fivethirtyeight_reorder)
    ax.set_xlabel('Draft')
    plt.legend(loc=2, prop={'size': 8})
    plt.title('Draft Picks by Positional Grouping')
    plt.tight_layout()
    plt.show()

    # Average Pick by Positional Grouping
    fig, ax = plt.subplots(figsize=(18, 5))
    sns.lineplot(x='Year', y='Pick', hue='Position_Group', data=draft_df, ci=None, palette=fivethirtyeight_reorder)
    ax.set_xticks(np.arange(2006, 2020))
    plt.legend(prop={'size': 10})
    plt.title('Average Pick by Positional Grouping')
    plt.tight_layout()
    plt.show()

    # Picks by Round (PG and G)
    fig, ax = plt.subplots(figsize=(18, 5))
    df = draft_df.groupby(['Year', 'Position_Group', 'Rnd']).count().reset_index()
    sns.barplot(x='Year', y='Pick', hue='Rnd', data=df[df['Position_Group']=='Guards: (PG and G)'])
    ax.legend(prop={'size': 10}, title='Round')
    ax.set_yticks(np.arange(0, 21, 3))
    ax.set_ylabel('Draft Picks')
    plt.title('Draft Picks by Round\nGuards: (PG and G)')
    plt.tight_layout()
    plt.show()

    # Picks by Round (SG, SF, and F)
    fig, ax = plt.subplots(figsize=(18, 5))
    df = draft_df.groupby(['Year', 'Position_Group', 'Rnd']).count().reset_index()
    sns.barplot(x='Year', y='Pick', hue='Rnd', data=df[df['Position_Group']=='Wings: (SG, SF, and F)'])
    ax.legend(prop={'size': 10}, title='Round')
    ax.set_yticks(np.arange(0, 21, 3))
    ax.set_ylabel('Draft Picks')
    plt.title('Draft Picks by Round\nWings: (SG, SF, and F)')
    plt.tight_layout()
    plt.show()

    # Picks by Round (PF and C)
    fig, ax = plt.subplots(figsize=(18, 5))
    df = draft_df.groupby(['Year', 'Position_Group', 'Rnd']).count().reset_index()
    sns.barplot(x='Year', y='Pick', hue='Rnd', data=df[df['Position_Group']=='Bigs: (PF, C)'])
    ax.legend(prop={'size': 10}, title='Round')
    ax.set_yticks(np.arange(0, 21, 3))
    ax.set_ylabel('Draft Picks')
    plt.title('Draft Picks by Round\nBigs: (PF, C)')
    plt.tight_layout()
    plt.show()
