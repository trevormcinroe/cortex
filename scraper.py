import datetime
import re
from datetime import timedelta

import requests
from bs4 import BeautifulSoup as bs


def power_rankings(link_to_site):
    """Use requests library to extract weekly ESPN MLB Power Rankings for use in Team Watchability Index calculation.

    Args:
        link_to_site: url to ESPN MLB Power Rankings website ('https://www.espn.com/mlb/powerrankings')

    Returns:
        {Date : {Team_1:Ranking, Team_2:Ranking, Team_3:Ranking, ..., Team_30:Ranking}}
    """
    # Retrieves section of website containing team rankings
    req = requests.get(link_to_site)
    soup = bs(req.content, features='lxml')
    power_ranking_team_list = soup.find_all('ol')[0]
    team_rankings = {}

    # Adds team name to team_rankings dict in order of power ranking, creating a numeric value for its position
    for count, item in enumerate(power_ranking_team_list.contents):
        team_name = item.a.text
        team_rankings.update({team_name: count + 1})

    # Creates dictionary of rankings using {date : team_rankings} structure
    dict_of_rankings = {datetime.datetime.today().strftime('%m-%d-%Y'): team_rankings}

    return dict_of_rankings


def team_records(link_to_site):
    """Use requests library to extract weekly ESPN MLB Team Records for use in Team Watchability Index calculation.

    Args:
        link_to_site: url to ESPN MLB Power Rankings website ('https://www.espn.com/mlb/powerrankings')

    Returns:
        {Date : {Team_1 : {Wins:##, Losses:##}, Team_2 : {Wins:##, Losses:##}, ..., Team_30 : {Wins:##, Losses:##}}
    """
    # Retrieves section of website containing team rankings
    req = requests.get(link_to_site)
    soup = bs(req.content, features='lxml')
    records_team_list = soup.find_all('ol')[0]
    team_records_raw = {}

    # Retrieves team record (##-## format), splits into wins and losses,
    # and updates inner dict containing wins and losses
    for count, item in enumerate(records_team_list.contents):
        team_name = item.a.text
        team_record = item.find_all('br')[1].previous_element
        wins, losses = team_record.split('-')
        wins_and_losses = {'Wins': int(wins), 'Losses': int(losses)}
        team_records_raw.update({team_name: wins_and_losses})

    # Creates outer dict using {date : wins_and_losses} format
    dict_of_records = {datetime.datetime.today().strftime('%m-%d-%Y'): team_records_raw}

    return dict_of_records


def team_schedule(link_to_site):
    """Use requests library to extract daily MLB Team Schedules for use in Game Watchability Index calculation

    Args:
        link_to_site: url to Sports Illustrated MLB Schedule website ('https://www.si.com/mlb/schedule')

    Returns:
        {Date : {Home 1: Team_Name, Away 1: Team_Name, ..., Home 8: Team_Name, Away 8: Team_Name}
    """
    # Retrieves section of website containing today's schedule
    req = requests.get(link_to_site)
    soup = bs(req.content, features='lxml')
    schedule_team_list = soup.find('div', attrs={'class': re.compile('component schedule')})
    daily_schedule = {}

    # Retrieves team abbreviations in Away-Home alternating format, then splits overall list into
    # Home and Away lists for the final dictionary
    raw_text = [row.text for row in schedule_team_list.find_all('span', attrs={'class': re.compile('numeric-score')})]
    raw_team_abbreviations = [re.findall(r'\w+', raw_text[i]) for i in range(0, len(raw_text), 2)]
    home_teams = [raw_team_abbreviations[1::2][i][0].upper() for i in range(int(len(raw_team_abbreviations) / 2))]
    away_teams = [raw_team_abbreviations[0::2][i][0].upper() for i in range(int(len(raw_team_abbreviations) / 2))]

    # Updates inner dictionary with Home and Away teams to become values for date key
    for team in range(len(home_teams)):
        daily_schedule.update({'Home ' + str(team): home_teams[team],
                               'Away ' + str(team): away_teams[team]})

    # Creates outer dict using {date : daily_schedule} format
    dict_of_schedule = {datetime.datetime.today().strftime('%m-%d-%Y'): daily_schedule}

    return dict_of_schedule


def box_scores(link_to_site):
    """Use requests library to extract daily MLB box scores for use in Live Game Watchability Index calculation

    Args:
        link_to_site: url to Sports Illustrated MLB Scoreboard website ('https://www.si.com/mlb/scoreboard')

    Returns:
        {Date : {Home-Away Concatenation: {H0: [Box Score], A0: [Box Score]}, ...
         , Home-Away Concatenation: {H8: [Box Score], A8: [Box Score]}}}
    """
    # Define team names for translation to abbreviations
    team_dict = {"Orioles": "BAL", "Red Sox": "BOS", "Yankees": "NYY", "Rays": "TB", "Blue Jays": "TOR",
                 "White Sox": "CWS", "Indians": "CLE", "Tigers": "DET", "Royals": "KC", "Twins": "MIN",
                 "Astros": "HOU", "Angels": "LAA", "Athletics": "OAK", "Mariners": "SEA", "Rangers": "TEX",
                 "Braves": "ATL", "Marlins": "MIA", "Mets": "NYM", "Phillies": "PHI", "Nationals": "WAS",
                 "Cubs": "CHC", "Reds": "CIN", "Brewers": "MIL", "Pirates": "PIT", "Cardinals": "STL",
                 "Diamondbacks": "ARI", "Rockies": "COL", "Dodgers": "LAD", "Padres": "SD", "Giants": "SF"}

    # Retrieves section of website box scores and team names
    req = requests.get(link_to_site)  # CHANGE
    soup = bs(req.content, features='lxml')
    scores = soup.find('div', attrs={'class': re.compile('content padding')})
    daily_scores = {}

    # Extract box score values for each team from each game
    box = [row.text for row in scores.find_all('tr', attrs={'class': re.compile('is-')})]
    box_score_values = [re.findall(r'\d+', box[i]) for i in range(len(box))]

    # Append 0s to innings that were canceled/didn't happen (i.e., bottom of 9th)
    for i in range(len(box_score_values)):
        while len(box_score_values[i]) != 12:
            box_score_values[i].insert(-3, '0')

    # Extract team names from each game
    team_names = [row.text for row in scores.find_all('span', attrs={'class': re.compile('team-name')})]
    teams = team_names[1::2]

    # Populate postponed games with 999 for each inning to allow them to stay in
    # the final dict but not be calculated on
    postponed = [999, 999, 999, 999, 999, 999, 999, 999, 999, 999, 999, 999]
    if len(box_score_values) != len(teams):
        diff = len(teams) - len(box_score_values)
        for i in range(diff):
            box_score_values.append(postponed)

    # Convert team names to abbreviations
    games = [team_dict[i] for i in teams]

    # Concatenate Home + Away to create unique codes for each game
    game_codes = [games[i + 1] + games[i] for i in range(0, len(games), 2)]

    # Create inner dict of Home and Away box scores to become values in outer dict
    for score in range(0, len(box_score_values), 2):
        box_values = ({'Home': box_score_values[score + 1], 'Away': box_score_values[score]})
        daily_scores.update({game_codes[round(score / 2)]: box_values})

    # Create outer dict using {yesterday's date : daily_scores} format because
    # box scores only exist for games already played
    yesterday = (datetime.datetime.today() - timedelta(days=1)).strftime('%m/%d/%Y')
    dict_of_box_scores = {yesterday: daily_scores}

    return dict_of_box_scores
