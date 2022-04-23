"""
*******************************************************************************
main.py
*******************************************************************************

This module contains functions for creating the graph based upon the datas ets.

This file is provided solely for the submission of the final
project of CSC111 at the University of Toronto, St. George Campus.

This file is Copyright (c) 2021 Chris Chan
"""
import pandas as pd
import unidecode
import python_ta
import data_process
from Player import Graph


def create_graph() -> Graph:
    """Return a Graph object containing the players found in the data sets. Takes
    the datasets and filters them for the desired group.
    """
    g = Graph()

    # Read and process 'pergame.csv' for this seasons data.
    bigs = get_br_data('data/pergame.csv')

    # Read and process 'advanced.csv' for this seasons data.
    modern_bigs_adv = get_br_data('data/advanced.csv')

    # Get columns of the advanced stats for the purposes of merging.
    per_game = [list(bigs.columns)[i] for i in range(8, len(list(bigs.columns)))]
    per_game_stats = bigs.copy()[per_game + ['Rk']]

    # Join the two data frames based on 'Rk' which uniquely identifies the players.
    modern_bigs = pd.merge(modern_bigs_adv, per_game_stats, on='Rk')

    # Add all player in modern_bigs to the graph
    _ = [g.add_vertex(unidecode.unidecode(name), pos) for name, pos
         in zip(modern_bigs['Player'], modern_bigs['Pos'])]

    # Add the stats of each player now in the graph.
    stat_headers = [list(modern_bigs.columns)[i] for i in range(5, len(list(modern_bigs.columns)))]

    _ = [g.update_stats(unidecode.unidecode(name), stats, stat_headers)
         for name, stats in zip(modern_bigs['Player'], modern_bigs[stat_headers].values)]

    # Read and process 'Season_Stats.csv' for historical stats.
    temp = data_process.read_csv('data/Seasons_Stats.csv')
    pfs = data_process.filter_df(temp, 'Pos', 'PF', clean=True)
    hybrid = data_process.filter_df(temp, 'Pos', 'PF-C', clean=True)
    c = data_process.filter_df(temp, 'Pos', 'C', clean=True)

    all_bigs = pd.concat([pfs, hybrid, c])

    # List of the names of all "big men". This will be used to filter some
    # of the other data sets, as well as for the average calculation.
    players = list(set(all_bigs['Player']))

    averages = data_process.calculate_average(all_bigs, players)

    # Add averages (from all_bigs) data to the graph
    _ = [g.add_vertex(name.strip('*'), pos, False)
         for name, pos in zip(averages['Player'], averages['Pos'])]
    per_game = [list(averages.columns)[i] for i in range(5, len(list(averages.columns)))]
    _ = [g.update_stats(name.strip('*'), stats, per_game)
         for name, stats in zip(averages['Player'], averages[per_game].values)]

    # Read and process 'basketball.sqlite' for all physical data.
    sql = data_process.read_basketball_sqlite('FIRST_NAME, LAST_NAME, HEIGHT, WEIGHT')

    # Add physical data to existing players in the graph
    in_graph = g.get_all_vertices()

    for f_name, l_name, height, weight in zip(sql['FIRST_NAME'],
                                              sql['LAST_NAME'], sql['HEIGHT'], sql['WEIGHT']):
        name = str(f_name + ' ' + l_name)

        if name in in_graph:
            g.update_physicals(name, height, weight)

        elif name + '*' in in_graph:
            g.update_physicals(name + '*', height, weight)

    return g


def get_br_data(file: str) -> pd.DataFrame:
    """Return a pandas DataFrame containing the fully cleaned and filtered data.

    For the purposes of this project, the DataFrame is filtered for only power forwards
    and centers.

    This function is intended for csv files retrieved from basketball-reference.com"""
    temp = data_process.read_csv(file)
    pfs = data_process.filter_df(temp, 'Pos', 'PF')
    c = data_process.filter_df(temp, 'Pos', 'C')
    df = pd.concat([pfs, c])

    # The dataset records stats for the season, as well as stats per team this season.
    # I only want to keep the overall stats for the season.
    df.drop_duplicates('Rk', inplace=True)

    # Remove empty columns
    df.dropna(axis=1, inplace=True)

    # Edit and fix the 'Player' column
    df['Player'] = df['Player'].apply(lambda x: x.split('\\')[0])

    return df


python_ta.check_all(config={
    'extra-imports': ['pandas', 'unidecode', 'data_process', 'Player'],
    'allowed-io': [],
    'max-line-length': 100,
    'disable': ['E1136']
})
