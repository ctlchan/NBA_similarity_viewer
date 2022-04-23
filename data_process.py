"""
*******************************************************************************
data_process.py
*******************************************************************************

This module contains the functions for reading the data sets for my final project.

This file is provided solely for the submission of the final
project of CSC111 at the University of Toronto, St. George Campus.

This file is Copyright (c) 2021 Chris Chan
"""
from typing import List
import sqlite3
import python_ta
import pandas as pd


def read_csv(filename: str) -> pd.DataFrame:
    """Read a csv file and return it as a pandas dataframe."""
    return pd.read_csv(filename)


def filter_df(frame: pd.DataFrame, column: str, target: str, compare: bool = False,
              clean: bool = False) -> pd.DataFrame:
    """Return a data frame which is a subset of the given dataframe.

    This function searches the given column and filters the data frame
    for the provided filter.

    Optional value 'compare' changes this function to return the rows that are
    greater than or equal to the target value.

    Preconditions:
        - column in df.column
        - if compare is True, then a comparison with 'target' is valid.
    """
    df = frame.copy()
    if clean:
        df.dropna(axis=1, how='all', inplace=True)
        df.dropna(axis=0, how='any', inplace=True)

    if compare:
        is_target = df[column] >= target
        return df[is_target]

    else:
        is_target = df[column] == target
        return df[is_target]


def read_basketball_sqlite(columns: str) -> pd.DataFrame:
    """Return a pandas dataframe containing data from kaggle.com/wyattowalsh/basketball

    The returned dataframe encompasses data from the table titled 'Player_Attributes', and
    only keeps 4 of the 37 columns.

    Preconditions:
        - Every item in columns.split(', ') is a column of table 'Player_Attributes'

    Example input for columns:
        columns = 'FIRST_NAME, LAST_NAME, HEIGHT, WEIGHT'
    """
    connection = sqlite3.connect('data/basketball.sqlite')
    df = pd.read_sql_query('SELECT ' + columns + ' FROM Player_Attributes', connection)
    connection.close()
    return df


def calculate_average(target: pd.DataFrame, players: List[str]) -> pd.DataFrame:
    """Return a dataframe containing the average stats per season of every player
    found in the dataframe.

    This function was implemented with file 'data/Seasons_Stats.csv' in mind, where
    each player has data for each season they played."""

    global categories
    data = []
    for player in players:
        # Filter for entries of the player and remove rows with missing stats
        # and rows that are duplicated. Rows are duplicated when the player
        # plays for multiple teams in a season. The first entry is kept
        # because it represents their stats for the ENTIRE season.
        temp = filter_df(target, 'Player', player)
        df = temp.drop_duplicates('Year')
        # Keep track of position, which is dropped when calculating the mean.
        position = df.iloc[len(df) - 1]['Pos']

        averages = df.mean(axis=0, skipna=True, numeric_only=True)
        categories = list(averages.keys())

        # I only want to calculate the per_game values of stats typically expressed
        # as such.

        pergame_categories = [categories[i] for i in range(len(categories)) if i >= 26 or i == 5]
        avg_games = averages[3]

        pergame_stats = [round(averages[key] / avg_games, 1) for key in pergame_categories
                         if key != avg_games]

        # Put the stats back together to match the column headers
        mpg = pergame_stats.pop(0)
        stats = [averages[i] for i in range(2)]
        stats.append(player)
        stats.append(position)
        stats.extend(averages[i] for i in range(2, 5))
        stats.append(mpg)
        stats.extend(averages[i] for i in range(6, 26))
        stats += pergame_stats

        categories.insert(2, 'Player')
        categories.insert(3, 'Pos')
        assert len(stats) == len(categories)

        data.append(stats)

    return pd.DataFrame(data, columns=categories)


python_ta.check_all(config={
    'extra-imports': ['pandas', 'typing', 'sqlite3'],
    'allowed-io': [],
    'max-line-length': 100,
    'disable': ['E1136']
})
