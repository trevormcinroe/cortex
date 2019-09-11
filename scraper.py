import datetime
from datetime import timedelta

import requests
import statsapi
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, url):
        self.soup = self.get_soup(url)
        pass

    def get_soup(self, url):
        req = requests.get(url)
        return BeautifulSoup(req.content, features='lxml')


def power_rankings(link_to_site):
    """ Use requests library to extract weekly ESPN MLB Power Rankings for use in Team Watchability Index calculation.
    Args:
        link_to_site: url to ESPN MLB Power Rankings website ('https://www.espn.com/mlb/powerrankings')
    Returns:
        {Date: {Team_1: Ranking, Team_2: Ranking, Team_3: Ranking, ..., Team_30: Ranking}}
    """
    # Retrieves section of website containing team rankings
    soup = Scraper(url=link_to_site).soup
    power_ranking_team_list = soup.find_all('ol')[0]
    team_rankings = {}

    # Adds team name to team_rankings dict in order of power ranking, creating a numeric value for its position
    for count, item in enumerate(power_ranking_team_list.contents):
        team_name = item.a.text
        team_rankings.update({team_name: count + 1})

    # Creates dictionary of rankings using {date : team_rankings} structure
    dict_of_rankings = {datetime.datetime.today().strftime('%m-%d-%Y'): team_rankings}

    return dict_of_rankings


def team_records():
    """ Use MLB Stats API to extract daily MLB Team Records for use in Game Watchability Index calculation

    Returns:
        {Date: {Team_Name: (Wins, Losses), Team_Name: (Wins, Losses), ..., Team_Name: (Wins, Losses)}}
    """
    # Retrieve today's league standings
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    standings = statsapi.standings_data()

    # League Codes:
    # 200 - AL West
    # 201 - AL East
    # 202 - AL Center
    # 203 - NL West
    # 204 - NL East
    # 205 - NL Central

    # Use League Codes to extract team name, wins, and losses
    records = {}
    for league in range(200, 206):
        for team in range(len(standings[league]['teams'])):
            teams = standings[league]['teams'][team]['name']
            wins = standings[league]['teams'][team]['w']
            losses = standings[league]['teams'][team]['l']

            records.update({teams: (wins, losses)})

    # Create main dictionary using date as key and records dictionary as value
    records_dict = {today: records}

    return records_dict


def team_schedule():
    """ Use MLB Stats API to extract daily MLB Team Schedules for use in Game Watchability Index calculation

    Returns:
        {Date: {H1: Team_Name, A1: Team_Name, ..., H8: Team_Name, A8: Team_Name}}
    """
    # Retrieve schedule of today's games
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    schedule = statsapi.schedule(today)

    # Team Codes:
    # 108	LAA	Angels
    # 109	ARI	D-backs
    # 110	BAL	Orioles
    # 111	BOS Red Sox
    # 112	CHC Cubs
    # 113	CIN	Reds
    # 114	CLE	Indians
    # 115	COL	Rockies
    # 116	DET	Tigers
    # 117	HOU Astros
    # 118	KC	Royals
    # 119	LAD	Dodgers
    # 120	WSH Nationals
    # 121	NYM Mets
    # 133	OAK Athletics
    # 134	PIT	Pirates
    # 135	SD	Padres
    # 136	SEA	Mariners
    # 137	SF	Giants
    # 138	STL	Cardinals
    # 139	TB	Rays
    # 140	TEX	Rangers
    # 141	TOR	Blue Jays
    # 142	MIN Twins
    # 143	PHI	Phillies
    # 144	ATL	Braves
    # 145	CWS White Sox
    # 146	MIA	Marlins
    # 147	NYY	Yankees
    # 158	MIL	Brewers

    # Convert Team Codes into Abbreviations and use as new dictionary values
    daily_schedule = {}
    for team in range(len(schedule)):
        home_team = statsapi.lookup_team(schedule[team]['home_id'])[0]['fileCode'].upper()
        away_team = statsapi.lookup_team(schedule[team]['away_id'])[0]['fileCode'].upper()
        daily_schedule.update({'H' + str(team): home_team,
                               'A' + str(team): away_team})

    # Append previous dictionary to main dictionary
    team_schedules = {today: daily_schedule}

    return team_schedules


def box_scores():
    """ Use MLB Stats API to extract daily MLB box scores for use in Live Game Watchability Index calculation

    Returns:
        {Date: {Home-Away First Code: (Home Score, Away Score), ..., Home-Away Last Code: (Home Score, Away Score)}}
    """
    # Create dynamic variable to get yesterday's box scores
    yesterday = (datetime.datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    schedule = statsapi.schedule(yesterday)

    # Retrieve values from schedule dictionary
    game_info = [list(schedule[i].values()) for i in range(len(schedule))]

    # Extract game codes from schedule dictionary values
    game_codes = [game_info[i][0] for i in range(len(game_info))]

    # Use game codes to retrieve all info for correct games
    home_away = []
    for i in range(len(game_codes)):
        home_away.append(statsapi.boxscore_data(game_codes[i]))

    # Use game codes to retrieve box scores for correct games
    boxes = []
    for i in range(len(game_codes)):
        home_box = (statsapi.linescore(game_codes[i]).splitlines()[2])
        away_box = (statsapi.linescore(game_codes[i]).splitlines()[1])
        boxes.extend([home_box, away_box])

    # Create dictionary with Home-Away concatenation as key and scores as values
    box_score = {}
    for i in range(len(home_away)):
        home_away_codes = (list(home_away[i]['teamInfo']['home'].values())[1] +
                           list(home_away[i]['teamInfo']['away'].values())[1])
        box_score.update({home_away_codes: (boxes[i * 2], boxes[(i * 2) + 1])})

    # Create main dictionary with date as key and box score dictionary as value
    score_dict = {yesterday: box_score}

    return score_dict
