import datetime
import re

import requests
from bs4 import BeautifulSoup as bs

url = 'https://www.espn.com/mlb/powerrankings'


def power_rankings(link_to_site):
    """Use requests library to extract weekly ESPN MLB Power Rankings for use in Team Watchability Index calculation.

    Args:
        link_to_site: url to ESPN MLB Power Rankings website

    Returns:
        {Date : {Team_1:Ranking, Team_2:Ranking, Team_3:Ranking, ..., Team_30:Ranking}}
    """
    req = requests.get(url)
    soup = bs(req.content, features='lxml')
    team_list = soup.find_all('ol')[0]
    team_rankings = {}

    for count, item in enumerate(team_list.contents):
        team_name = item.a.text
        team_rankings.update({team_name: count + 1})

    dict_of_rankings = {datetime.datetime.today().strftime('%m-%d-%Y'): team_rankings}

    return dict_of_rankings


def team_records(link_to_site):
    """Use requests library to extract MLB team records from weekly ESPN rankings article.

    Args:
        link_to_site: url to ESPN MLB Power Rankings website

    Returns:
        {Date : {Team_1 : {Wins:##, Losses:##}, Team_2 : {Wins:##, Losses:##}, ..., Team_30 : {Wins:##, Losses:##}}
    """
    req = requests.get(url)
    soup = bs(req.content, features='lxml')
    team_list = soup.find_all('ol')[0]
    team_records_raw = {}

    for count, item in enumerate(team_list.contents):
        team_name = item.a.text
        team_record = item.find_all('br')[1].previous_element
        wins, losses = team_record.split('-')
        wins_and_losses = {'Wins': int(wins), 'Losses': int(losses)}
        team_records_raw.update({team_name: wins_and_losses})

    dict_of_records = {datetime.datetime.today().strftime('%m-%d-%Y'): team_records_raw}

    return dict_of_records


def schedule(url):
    """jfjhg

    Args:
        url: jhgjhg, str

    Returns:
        hjghjg
    """
    # Here is what the next two lines are doing
    url = "https://www.si.com/mlb/schedule"
    page = requests.get(url)

    # Grabs the soup
    soup = BeautifulSoup(page.text, 'html.parser')
    full_schedule = soup.find('div', attrs={'class': re.compile('component schedule')})
    team_schedule = [row.text for row in full_schedule.find_all('span', attrs={'class': re.compile('numeric-score')})]
    team_abbreviations = [re.findall(r'\w+', team_schedule[i]) for i in range(len(team_schedule))]
    return team_abbreviations
