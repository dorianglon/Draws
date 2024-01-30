from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from Resources.resources import *
import os
import pandas as pd
from Resources.IO import *
import numpy as np


def Reverse(lst):
    return [ele for ele in reversed(lst)]


def get_historical_odds(seasons, league_link, length_22, prev_length):
    """
    Scrape historical odds and results for certain league
    :param seasons: list of seasons we want to scrape from
    :param league_link: link to the page with historical results
    :param length_22: how many pages of current season's historical results
    :param prev_length: length of previous seasons historical results
    :return: returns list of scraped rows. Each row has team names, odds, and ftr
    """

    driver = webdriver.Safari()
    games = []
    # loop through each given season
    for season in seasons:
        if season == '2023-2024':
            season_url = league_link + '/results/'
            driver.get(season_url)
            page = 1
            while page <= length_22:
                for k in range(4):
                    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                    time.sleep(2)
                table = driver.find_element_by_xpath("//div[@class='flex flex-col px-3 text-sm max-mm:px-0']")
                time.sleep(2)
                trs = table.find_elements_by_xpath("//div[@class='flex flex-col w-full text-xs eventRow']")
                for tr in trs:
                    text_el = tr.find_element_by_xpath(".//div[@class='flex hover:bg-[#f9e9cc] group border-l border-r "
                                                       "border-black-borders']")
                    text_el_text = text_el.text
                    size = len(text_el_text)
                    info_val_length = len(tr.find_element_by_xpath(".//div[@class='height-content text-[10px] "
                                                                   "leading-5 text-black-main']").text)
                    games.append(text_el_text[:size - info_val_length] + season)
                if page < length_22:
                    time.sleep(2)
                    new_url = season_url + '#/page/' + str(page+1) + '/'
                    driver.get(new_url)
                    driver.refresh()
                    time.sleep(2)
                page += 1
            games = Reverse(games)
        else:
            season_url = league_link + '-' + season + '/results/'
            driver.get(season_url)
            page = 1
            while page <= prev_length:
                for k in range(4):
                    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                    time.sleep(2)
                    driver.find_element()
                table = driver.find_element_by_xpath("//div[@class='flex flex-col px-3 text-sm max-mm:px-0']")
                time.sleep(2)
                trs = table.find_elements_by_xpath("//div[@class='flex flex-col w-full text-xs eventRow']")
                for tr in trs:
                    text_el = tr.find_element_by_xpath(
                        ".//div[@class='flex hover:bg-[#f9e9cc] group border-l border-r border-black-borders min-h-["
                        "40px]']")
                    text_el_text = text_el.text
                    size = len(text_el_text)
                    info_val_length = len(tr.find_element_by_xpath(".//div[@class='height-content text-[10px] "
                                                                   "leading-5 text-black-main']").text)
                    games.append(text_el_text[:size - info_val_length] + season)
                if page < prev_length:
                    time.sleep(2)
                    new_url = season_url + '#/page/' + str(page + 1) + '/'
                    print(new_url)
                    driver.quit()
                    driver = webdriver.Safari()
                    driver.get(new_url)
                    # driver.refresh()
                    # time.sleep(3)
                    # driver.get(new_url)
                    # driver.refresh()
                    time.sleep(2)
                page += 1
            games = Reverse(games)
    driver.quit()
    return games


def write_raw(games, save_as):
    """
    Write the scraped data to a text file
    :param games: list containing each row that we scraped
    :param save_as: save data to this file
    """

    with open(save_as, 'a+') as f:
        for game in games:
            f.write(game + '\n')
    f.close()


def get_raw_data(raw_data):
    """
    Read scraped data from the text file
    :param raw_data: file where the data is stored
    :return: list containing this data
    """

    data = []
    with open(raw_data, 'r') as f:
        lines = f.readlines()
        for line in lines:
            new_line = line.replace('\n', '')
            data.append(new_line.replace(' ', ''))
    return data


def extract_season(season):
    """
    Extract season from string
    :param season: string containing the season to extract
    :return: season
    """

    first = season[0:5]
    second = season[7:]
    return first + second


def extract_teams(teams):
    """
    Extract the teams from game
    :param teams: string containing teams
    :return: teams
    """

    teams = teams.split('-')
    return teams[0], teams[1]


def extract_odds(odds):
    """
    Extract odds from string
    :param odds: string containing odds
    :return: odds
    """

    index1 = 0
    index2 = 0
    index3 = 0
    for i in range(len(odds)):
        if i > 0:
            if odds[i] == '+' or odds[i] == '-':
                if index2 == 0:
                    index2 = i
                else:
                    index3 = i
    return odds[index1:index2], odds[index2:index3], odds[index3:]


def extract_data(data):
    """
    Extract team names, odds, and ftr from each line of data
    :param data: list of scraped data
    :return: lists of each data category
    """

    home_teams = []
    away_teams = []
    h_odds = []
    a_odds = []
    d_odds = []
    seasons = []
    ftrs = []
    home_goals = []
    away_goals = []
    for el in data:
        try:
            season = el[-9:]
            el = el[:-9]
            game = el.split(':')
            game.pop(0)
            game[0] = game[0][2:]
            game[0] = game[0].replace(u'\xa0', u'')
            game[0] = game[0].replace(u'\xa0', u'')
            game[1] = game[1].replace(u'\xa0', u'')
            game.append(game[0][-1:])
            game[0] = game[0][:-1]
            game.append(game[1][0:1])
            game[1] = game[1][1:]
            home_team, away_team = extract_teams(game[0])
            home_odds, draw_odds, away_odds = extract_odds(game[1])
            home_teams.append(home_team)
            away_teams.append(away_team)
            h_odds.append(home_odds)
            d_odds.append(draw_odds)
            a_odds.append(away_odds)
            seasons.append(extract_season(season))
            home_goals.append(game[2])
            away_goals.append(game[3])
            if game[2] > game[3]:
                ftrs.append('H')
            elif game[2] < game[3]:
                ftrs.append('A')
            elif game[2] == game[3]:
                ftrs.append('D')
        except Exception:
            pass
    return home_teams, away_teams, h_odds, a_odds, d_odds, seasons, home_goals, away_goals, ftrs


def extract_current_week_data(data):
    home_teams = []
    away_teams = []
    h_odds = []
    a_odds = []
    d_odds = []
    seasons = []
    ftrs = []
    home_goals = []
    away_goals = []
    for el in data:
        try:
            season = el[-9:]
            el = el[:-9]
            game = el.split(':')
            game[0] = game[0].replace(u'\xa0', u'')
            game[0] = game[0].replace(u'\xa0', u'')
            game[1] = game[1].replace(u'\xa0', u'')
            game.append(game[0][-1:])
            game[0] = game[0][:-1]
            game.append(game[1][0:1])
            game[1] = game[1][1:]
            home_team, away_team = extract_teams(game[0])
            home_odds, draw_odds, away_odds = extract_odds(game[1])
            home_teams.append(home_team)
            away_teams.append(away_team)
            h_odds.append(home_odds)
            d_odds.append(draw_odds)
            a_odds.append(away_odds)
            seasons.append(extract_season(season))
            home_goals.append(game[2])
            away_goals.append(game[3])
            if game[2] > game[3]:
                ftrs.append('H')
            elif game[2] < game[3]:
                ftrs.append('A')
            elif game[2] == game[3]:
                ftrs.append('D')
        except Exception:
            pass
    return home_teams, away_teams, h_odds, a_odds, d_odds, seasons, home_goals, away_goals, ftrs


def make_df(home_teams, away_teams, h_odds, a_odds, d_odds, seasons, home_goals, away_goals, ftrs, save_as):
    """
    Create a dataframe with all of the data we now have
    :param home_teams: list of home teams
    :param away_teams: list of away teams
    :param h_odds: list of home odds
    :param a_odds: list of away odds
    :param d_odds: list of draw odds
    :param seasons: list of seasons
    :param home_goals: list of predicted home goals
    :param away_goals: list of predicted away goals
    :param ftrs: list of full time results
    :param save_as: file to save dataframe to as a csv file
    """

    df = pd.DataFrame()
    df['Home Team'] = home_teams
    df['Away Team'] = away_teams
    df['Home Win odds'] = h_odds
    df['Away Win odds'] = a_odds
    df['Draw odds'] = d_odds
    df['FTHG'] = home_goals
    df['FTAG'] = away_goals
    df['Season'] = seasons
    df['FTR'] = ftrs
    write_df(df, save_as)


def clean_df(df, save_as):
    """
    Remove rows that dont belong
    :param df: dataframe
    :param save_as: file for dataframe
    """

    df.drop_duplicates(keep=False, inplace=True)
    df = df[df['Home Win odds'] != '-']
    df = df[df['Home Win odds'] != 'pen.']
    df = df[df['Home Win odds'] != 'ET']
    df = df[df['Home Team'] != 'Granada']
    df = df[df['Away Team'] != 'Granada']
    df = df[df['Home Win odds'].str.len() >= 3]
    df = df[df['Away Win odds'].str.len() >= 3]
    df = df[df['Draw odds'].str.len() >= 3]
    df['Home Win odds'] = pd.to_numeric(df['Home Win odds'])
    df['Away Win odds'] = pd.to_numeric(df['Away Win odds'])
    df['Draw odds'] = pd.to_numeric(df['Draw odds'])
    df['FTHG'] = pd.to_numeric(df['FTHG'])
    df['FTAG'] = pd.to_numeric(df['FTAG'])
    write_df(df, save_as)


def get_past_data(league_link, league_dir):
    """
    Function encompasses above functions to scrape for a certain league and write raw output to text file
    :param league_link: link to website with bookie data for this league
    :param league_dir: directory to league
    """

    raw_data = league_dir + 'historical_odds_raw.txt'
    length_23 = 9
    prev_length = 8
    seasons = ['2022-2023']
    # seasons = ['2005-2006', '2006-2007', '2007-2008', '2008-2009', '2009-2010', '2010-2011'
    # , '2011-2012', '2012-2013', '2013-2014', '2014-2015', '2015-2016'
    # , '2016-2017', '2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023']
    games = get_historical_odds(seasons, league_link, length_23, prev_length)
    write_raw(games, raw_data)


def clean_data_and_make_df(league_dir):
    """
    Function encompasses above functions to clean the raw scraped data and input data into a dataframe
    :param league_dir: directory to league
    """

    raw_data = league_dir + 'historical_odds_raw.txt'
    df_file = league_dir + 'historical_df.csv'
    data = get_raw_data(raw_data)
    new_data = []
    # for el in data:
    #     index = 0
    #     count = 0
    #     for char in el:
    #         if char == ':':
    #             count += 1
    #             if count == 2:
    #                 break
    #         else:
    #             index += 1
    #     new_str = el[:index - 1] + el[index:]
    #     score_sub = new_str[index-1:index+2]
    #     new_str = new_str.replace(score_sub, '–')
    #     new_index = 0
    #     for char in new_str:
    #         if new_index >= index - 1:
    #             if char.isdigit():
    #                 break
    #             else:
    #                 new_index += 1
    #         else:
    #             new_index += 1
    #     final_string = new_str[:new_index] + score_sub + new_str[new_index + 1:]
    #     final_string = final_string.replace('–', '-')
    #     new_data.append(final_string)
    for el in data:
        index = 0
        count = 0
        for char in el:
            if char == '–':
                break
            else:
                index += 1
        new_str = el[:index - 1] + el[index:]
        score_sub = new_str[index-2:index+1]
        new_str = new_str.replace(score_sub, '–')
        score_sub = score_sub.replace('–', ':')
        new_index = 0
        for char in new_str:
            if new_index >= index - 1:
                if char.isdigit():
                    break
                else:
                    new_index += 1
            else:
                new_index += 1
        final_string = new_str[:new_index] + score_sub + new_str[new_index + 1:]
        final_string = final_string.replace('–', '-')
        new_data.append(final_string)
    home_teams, away_teams, h_odds, a_odds, d_odds, seasons, home_goals, away_goals, ftrs = extract_data(
        new_data)
    make_df(home_teams, away_teams, h_odds, a_odds, d_odds, seasons, home_goals, away_goals, ftrs
            , df_file)
    clean_df(read_df(df_file), df_file)


def season_2023():
    league_dir_2023 = EFL_2023
    if not os.path.isdir(league_dir_2023):
        os.mkdir(league_dir_2023)
    league_link = EFL_HIST_ODDS_LINK
    get_past_data(league_link, league_dir_2023)
    clean_data_and_make_df(league_dir_2023)


def reorder_df(league_dir):
    df = read_df(league_dir + 'historical_df.csv')
    grouped = df.groupby(df.Season)
    frames = []
    for group in grouped:
        frames.append(group[1])
    final = pd.concat(frames)
    write_df(final, league_dir + 'historical_df.csv')


def past_data_for_training():
    """
    Function encapsulated scraping, cleaning, and creating dataframe for past matches in league
    """

    league_link = EPL_HIST_ODDS_LINK
    league_dir = EPL
    get_past_data(league_link, league_dir)
    # clean_data_and_make_df(league_dir)
    # reorder_df(league_dir)


def main():
    past_data_for_training()
    # season_2023()


if __name__ == '__main__':
    main()
