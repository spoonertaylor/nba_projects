import numpy as np
import pandas as pd
from functools import reduce
from datetime import datetime, timedelta
# Read in pbp data
pbp_data = pd.read_csv('Documents/nba_projects/data/nba/pbp/pbp_season2020_month_november.csv')
pbp_data = pbp_data.drop(['home_score', 'away_score'], axis = 1)
# Global list of team abbrv
team_list = [team for team in list(pbp_data.home_team_abbrev.unique()) + list(pbp_data.away_team_abbrev.unique())]
teams = pd.DataFrame(set(team_list),
            columns=['team_abbrv'])

def point_diff_to_expected_wins(point_diff):
    return (point_diff*2.7)+41

'''
Calc possessions
Use event_type_de to remove
- period start
- jump-ball
- foul (maybe) (offensive fouls get two lines one for the foul and one for the turnover)
- goal-tending
- team-timeout
- substitution
- instant-replay
-

Keeps: rebound, shot, missed-shot, turnover, period-end (only if it changes teams)
'''
def calc_possessions(data, remove_projected_heaves=True):
    '''
    To do: Garbage Time
    To do: Heave possessions -- when possession starts (so last possession ends) with 4 or less seconds left
    '''
    if data.shape[0] == 0:
        raise ValueError("No rows in the data")
    else:
        stat_data = data.copy()

    pbp = data.copy()
    # Remove projected heaves by cleaning the glass filter
    # CTG defines these possessions as those that start with 4 or fewer seconds
    # on the game clock at the end of one of the first three quarters.
    if remove_projected_heaves:
        # Previous time on the clock
        pbp['prev_time_str'] = pbp.groupby(['game_id', 'period'])['pctimestring'].shift(1, fill_value='12:00:00')
        def new_split(row):
            return row['prev_time_str'].split(':')
        # String to number
        time = [int(t[0]) * 60 + int(t[1]) for t in pbp.apply(new_split, axis=1)]
        pbp['prev_time'] = time # Time as a number

    # Only get events that will show change in possession
    pbp = pbp.query("event_type_de in ('rebound', 'shot', 'missed_shot', 'turnover', 'free-throw')").copy()
    # Remove technical fouls
    pbp = pbp.query("not (homedescription.str.contains('Technical') or visitordescription.str.contains('Technical'))")
    pbp = pbp.sort_values(['period','pctimestring', 'eventnum'], ascending=[True, False, True])
    pbp['next_team'] = pbp.groupby(['game_id', 'period'])['event_team'].shift(-1, fill_value="XXX")
    pbp['prev_team'] = pbp.groupby(['game_id', 'period'])['event_team'].shift(1, fill_value="YYY")
    if remove_projected_heaves:
        # Filter
        pbp = pbp.query("(not (prev_time < 4 and period < 4 and event_team != prev_team)) or period >= 4")
    # Calc home possessions
    pbp['home_team_possession'] = list(map(
        lambda home_team, team, next_team, event: 1 if team == home_team and team != next_team
                                                        else 0,
        pbp.home_team_abbrev, pbp.event_team, pbp.next_team, pbp.event_type_de))
    # Calc away possessions
    pbp['away_team_possession'] = list(map(
        lambda away_team, team, next_team, prev_team: 1 if team == away_team and team != next_team
                                                        else 0,
        pbp.away_team_abbrev, pbp.event_team, pbp.next_team, pbp.prev_team))
    # Now aggregate and join
    home_poss = pbp.groupby('home_team_abbrev')['home_team_possession'].sum().reset_index().\
        rename(columns={'home_team_abbrev': 'team_abbrv'})
    away_poss = pbp.groupby('away_team_abbrev')['away_team_possession'].sum().reset_index().\
        rename(columns={'away_team_abbrev': 'team_abbrv'})
    poss_df = pd.merge(pd.merge(teams, home_poss, on='team_abbrv', how='left'),
                      away_poss, on='team_abbrv', how='left').fillna(0)
    poss_df['possessions'] = poss_df['home_team_possession'] + poss_df['away_team_possession']

    return poss_df[['team_abbrv', 'possessions']]


def calc_points_W_L(data):
    '''
    NEED TO DO: Techincal Foul Points vs non technical foul points
    Calculate Wins, Losses, Points For and Points Against for PBP Data
    Input: PBP Data
    Output: DF each row is a team
    '''
    if data.shape[0] == 0:
        raise ValueError("No rows in the data")
    else:
        stat_data = data.copy()
    # Get the last row of each game
    stat_data['max_period'] = stat_data.groupby('game_id')['period'].transform(max)
    end_game = stat_data.query("period == max_period")
    end_game = end_game[end_game['score'].notnull()]
    end_game = end_game.groupby('game_id').tail(1)
    # Split up the score
    score = end_game['score'].str.split('-', n=1, expand = True)
    end_game['home_score'] = [int(x) for x in score[0]]
    end_game['away_score'] = [int(x) for x in score[1]]
    # Calculate teams wins and losses
    home_wins = end_game.query("home_score > away_score").groupby('home_team_abbrev').size()\
        .reset_index(name='W_home').rename(columns={'home_team_abbrev':'team_abbrv'})
    home_losses = end_game.query("home_score < away_score").groupby('home_team_abbrev').size()\
        .reset_index(name='L_home').rename(columns={'home_team_abbrev':'team_abbrv'})
    away_wins = end_game.query("home_score < away_score").groupby('away_team_abbrev').size()\
        .reset_index(name='W_away').rename(columns={'away_team_abbrev':'team_abbrv'})
    away_losses = end_game.query("home_score > away_score").groupby('away_team_abbrev').size()\
        .reset_index(name='L_away').rename(columns={'away_team_abbrev':'team_abbrv'})
    win_loss = pd.merge(teams, home_wins, on='team_abbrv', how='left')
    win_loss = reduce(lambda left,right: pd.merge(left,right,on='team_abbrv', how='left'),
                      [win_loss, home_losses, away_wins, away_losses]).fillna(0)
    win_loss['GP'] = win_loss['W_home'] + win_loss['L_home'] + win_loss['W_away'] + win_loss['L_away']
    win_loss['GP_home'] = win_loss['W_home'] + win_loss['L_home']
    win_loss['GP_away'] = win_loss['W_away'] + win_loss['L_away']
    win_loss['W'] = win_loss['W_home'] + win_loss['W_away']
    win_loss['L'] = win_loss['L_home'] + win_loss['L_away']
    # Calculate points for and against
    home_points = end_game.groupby('home_team_abbrev').agg({
        'home_score': 'sum',
        'away_score': 'sum'
    }).reset_index().rename(columns={'home_team_abbrev':'team_abbrv',
                                     'home_score': 'home_points_for',
                                     'away_score': 'home_points_against'})
#    home_technical_points = stat_data.query("homedescription.str.contains('Technical')").\
#        groupby('home_team_abbrev').agg({'points_made':'sum'})
    away_points = end_game.groupby('away_team_abbrev').agg({
        'home_score': 'sum',
        'away_score': 'sum'
    }).reset_index().rename(columns={'away_team_abbrev':'team_abbrv',
                                     'home_score': 'away_points_against',
                                     'away_score': 'away_points_for'})
    points = pd.merge(pd.merge(teams, home_points, on='team_abbrv', how='left'),
                      away_points, on='team_abbrv', how='left').fillna(0)
    points['points_for'] = points['home_points_for'] + points['away_points_for']
    points['points_against'] = points['home_points_against'] + points['away_points_against']

    fin_df = pd.merge(win_loss, points, on ='team_abbrv')
    fin_df = fin_df[['team_abbrv', 'GP', 'W', 'L', 'points_for', 'points_against',
                     'GP_home', 'W_home', 'L_home', 'home_points_for', 'home_points_against',
                     'GP_away', 'W_away', 'L_away', 'away_points_for', 'away_points_against']]
    return fin_df

def calc_last_n_days(data, start_date = None, end_date = None, last_n_days = None):
    # Convert game date to date
    data['game_date'] = pd.to_datetime(data['game_date'])
    # If nothing is given, calculate last two weeks from current date
    if start_date is None and end_date is None and last_n_days is None:
        two_weeks_ago = (datetime.now() - timedelta(days=14)).replace(minute = 0, hour = 0, second = 0, microsecond=0)
        filt_pbp = data.loc[data.game_date >= two_weeks_ago].copy()
    # If no start date but an end date, calculate from current date to end date
    elif start_date is None and end_date is not None:
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        elif not isinstance(end_date, datetime):
            raise TypeError("Date Error: Input a datetime object or date as a string of form YYYY-DD-MM or DD-MM-YYYY")
        filt_pbp = data.loc[(data.game_date >= end_date)].copy()
    # If no start date but last n days given, calc for last n days
    elif start_date is None and last_n_days is not None:
        if not isinstance(last_n_days, int):
            raise TypeError("Last N Error: last_n_days should be inputed as an integer")
        last_date = (datetime.now() - timedelta(days=last_n_days)).replace(minute = 0, hour = 0, second = 0, microsecond=0)
        filt_pbp = data.loc[data.game_date >= last_date].copy()
    # If a start date but no end date and no last n days, 2 weeks from start date
    elif start_date is not None and end_date is None and last_n_days is None:
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        elif not isinstance(start_date, datetime):
            raise TypeError("Date Error: Input a datetime object or date as a string of form YYYY-DD-MM or DD-MM-YYYY")
        two_weeks_from_date = (start_date - timedelta(days=14)).replace(minute = 0, hour = 0, second = 0, microsecond=0)
        filt_pbp = data.loc[(data.game_date <= start_date) & (data.game_date >= two_weeks_from_date)].copy()
    # If given a start date and an end date calculate the date range
    elif start_date is not None and end_date is not None:
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        elif not isinstance(start_date, datetime):
            raise TypeError("Date Error: Input a datetime object or date as a string of form YYYY-DD-MM or DD-MM-YYYY")
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        elif not isinstance(end_date, datetime):
            raise TypeError("Date Error: Input a datetime object or date as a string of form YYYY-DD-MM or DD-MM-YYYY")
        filt_pbp = data.loc[(data.game_date >= start_date) & (data.game_date <= end_date)].copy()
    # If given a start date and last n days calculate from start to last n
    elif start_date is not None and last_n_days is not None:
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        elif not isinstance(start_date, datetime):
            raise TypeError("Date Error: Input a datetime object or date as a string of form YYYY-DD-MM or DD-MM-YYYY")
        if not isinstance(last_n_days, int):
            raise TypeError("Last N Error: last_n_days should be inputed as an integer")
        two_weeks_from_date = (start_date - timedelta(days=last_n_days)).replace(minute = 0, hour = 0, second = 0, microsecond=0)
        filt_pbp = data.loc[(data.game_date <= start_date) & (data.game_date >= two_weeks_from_date)].copy()
        return filt_pbp
    # After all that (are there more cases?)
    return calc_points_W_L(filt_pbp)
