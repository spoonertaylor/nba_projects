#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 19:25:26 2019

PURPOSE: 
    Function to lead/lag target column out

@author: tspoo1
"""

import pandas as pd
import sys

def pivot_target_column(df, target_name, player_name, id_name, season_name, agg_function):
    '''
    Pivot out the target_name such that for each season we have the metric -4 to +4
        shifted out.
    
    Args:
        df: Data.Frame that contains all the columns
        target_name: Metric to pivot out
        player: Column name for the player's name
        id_name: A unique ID column for players
        season_name: Column name of the season column. Usually 'season' or 'SEASON'
        agg_function: For data frames that might have more than one record
            for a player|season cut, aggregate to just one row
    Return:
        A dataframe with the player name column, id column and 
            columns for the target pivoted out -4 to +4 
    '''
    condition = list(set([target_name, player_name, id_name, season_name]) - set(list(df.columns)))
    if len(condition) > 0:
        sys.exit('Not all inputed column names are columns in df... Come on man!')

    # Filter out total team roles, only take 3 columns
    data_sub = df[df.team != 'TOT'][[player_name, id_name, season_name, target_name]]
    # Remove duplicates by aggregating down
    data_sub = data_sub.groupby([player_name, id_name, season_name]).agg(agg_function).reset_index()

    # Create seperate df for all seasons between they played
    # In case people were in and out of the league
    player_seasons = data_sub.groupby([player_name, id_name]).season.agg(['min', 'max']).reset_index()

    player_seasons_full = pd.DataFrame(columns = [player_name, id_name, season_name])
    for p in range(0, player_seasons.shape[0]):
        min_season = player_seasons['min'][p]
        max_season = player_seasons['max'][p]
        all_seasons = [x for x in range(min_season, max_season+1)]
        df_temp = pd.DataFrame(all_seasons, columns = [season_name])
        df_temp[player_name] = player_seasons[player_name][p]
        df_temp[id_name] = player_seasons[id_name][p]
        player_seasons_full = player_seasons_full.append(df_temp,
                                                         ignore_index = True,
                                                         sort = False)
        # Join together so NA values will people who jump in and out of league
        data_sub = (
            player_seasons_full
                .set_index([player_name, id_name, season_name])
                .join(data_sub.set_index([player_name, id_name, season_name]), how = 'left')
                .reset_index()
        )
    # Lead and Lag the target variable out -4 to +4 
    for m in range(0, 9):
        if m <= 3:
            data_sub['season_minus_{}'.format(m+1)] = (
                data_sub.sort_values(by = [season_name])
                    .groupby([player_name, id_name])[target_name].shift(m+1)
                )
        elif m == 4:
            data_sub['season_plus_0'] = data_sub[target_name]
        else:
            data_sub['season_plus_{}'.format(m-4)] = (
                data_sub.sort_values(by = [season_name])
                    .groupby([player_name, id_name])[target_name].shift(-(m-4))
            )
    # Drop the original target variable
    data_sub = data_sub.drop(target_name, axis = 1)
    return(data_sub)