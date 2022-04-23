"""
*******************************************************************************
Player.py
*******************************************************************************

This is module contains the _Vertex and Graph-equivalent classes for my final project.

This file is provided solely for the submission of the final
project of CSC111 at the University of Toronto, St. George Campus.

This file is Copyright (c) 2021 Chris Chan
"""
from __future__ import annotations
from typing import Any, Dict, Optional, List
import python_ta


class Player:
    """A class representing a basketball player in the NBA.

    Instance Attributes:
        - name: The name of the player
        - position: The position that the player is officially listed at.
        - height: The height of the player in feet and inches.
        - weight: The weight of the player in pounds (lbs).
        - stats: The stats of the player, including per game and advanced stats.
        - neighbours: The player objects adjacent to this player.
        """
    name: str
    position: str
    era: str
    height: Optional[int]
    weight: Optional[int]
    stats: Optional[Dict]
    big_man_score: Optional[float]
    neighbours: set[Player]

    def __init__(self, name: str, position: str, modern: bool = True) -> None:
        """Initialize a player object with the given attributes."""
        self.name = name
        self.position = position
        self.height = None
        self.weight = None
        self.stats = None
        self.big_man_score = None
        self.neighbours = set()

        if modern:
            self.era = 'modern'
        else:
            self.era = 'traditional'

    def update_stats(self, stats: dict[str, float], headers: List[str]) -> None:
        """Update the 'stats' attribute of this player."""
        assert len(stats) == len(headers)

        self.stats = {}
        for i in range(len(stats)):
            if headers[i] not in self.stats.keys():
                self.stats[headers[i]] = stats[i]

    def update_physicals(self, height: int, weight: int) -> None:
        """Update the 'stats' attribute of this player."""
        self.height = height
        self.weight = weight

    def calculate_big_man_score(self) -> None:
        """Update the big_man_score of a player.

        This is a metric I devised myself based on the categories encompassed by self.stats
        This metric is the weighted average of scores given to areas of the game. The
        weights are based on what I consider most important for a traditional center.

        Each category is designed to be 'good' at a value around 10"""
        stats = self.stats.copy()

        defense = (stats['BLK'] + stats['BLK%']) + ((stats['DRB'] + stats['DRB%']) / 10) +\
                  (stats['STL'] + stats['STL%']) - stats['PF']

        offense = (stats['PTS'] + ((stats['ORB'] + stats['ORB%']) / 10)) - \
                  (stats['TOV'] * 10 - stats['TOV%'])

        # This is low if you shoot a lot of threes and pass more than typical.
        degree_traditional = 9 - stats['3PA'] + (3 - stats['AST'])

        misc = (stats['PER'] / 3) + (stats['WS'] / 10)

        try:
            physicality = stats['FT'] * (self.weight / self.height)
        except TypeError:
            physicality = None

        if physicality is not None:
            self.big_man_score = (degree_traditional * 0.3) + (physicality * 0.3) +\
                                 (offense * 0.2) + (defense * 0.15) + (misc * 0.05)
        else:
            self.big_man_score = (degree_traditional * 0.4) + (offense * 0.35) +\
                                 (defense * 0.2) + (misc * 0.05)


class Graph:
    """A graph used to represent the players of the NBA.
    """
    # Private Instance Attributes:
    #     - _players:
    #         A collection of the vertices contained in this graph,
    #         Maps a player name to their Player object.,
    _players: Dict[Any, Player]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._players = {}

    def add_vertex(self, name: str, position: str, modern: bool = True) -> None:
        """Add a player with the given information to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        """
        if name not in self._players and modern:
            self._players[name] = Player(name, position)
        elif name not in self._players:
            self._players[name] = Player(name, position, False)

    def add_edge(self, player1: Any, player2: Any) -> None:
        """Add an edge between the two players with the given names in this graph.

        Raise a ValueError if player1 or player2 do not appear as vertices in this graph.

        Preconditions:
            - player1 != player2
        """
        if player1 in self._players and player2 in self._players:
            v1 = self._players[player1]
            v2 = self._players[player2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def adjacent(self, player1: Any, player2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if player1 in self._players and player2 in self._players:
            v1 = self._players[player1]
            return any(v2.name == player2 for v2 in v1.neighbours)
        else:
            return False

    def get_info(self, player: str) -> Dict:
        """Return the information about a player stored in their object."""
        mapping = self._players
        return {
            'name': mapping[player].name,
            'position': mapping[player].position,
            'height': mapping[player].height,
            'weight': mapping[player].weight
        }

    def get_stats(self, player: str) -> Dict[str: float]:
        """Return the stats of a player."""
        return self._players[player].stats

    def get_neighbours(self, player: Any) -> set:
        """Return a set of the neighbours of the given player.

        Note that the *player names* are returned, not the Player objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if player in self._players:
            v = self._players[player]
            return {neighbour.name for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self) -> set:
        """Return a set of all player names in this graph.
        """
        return set(self._players.keys())

    def update_stats(self, player: str, new_stats: dict[str, float], headers: List[str]) -> None:
        """Update the stats of the given player. This can only occur once."""
        if player in self._players and self._players[player].stats is None:
            self._players[player].update_stats(new_stats, headers)

        elif self._players[player].stats is not None:
            return

        else:
            raise ValueError

    def update_physicals(self, player: str, height: int, weight: int) -> None:
        """Update physical measurements of the given player."""
        if player in self._players:
            self._players[player].update_physicals(height, weight)

        else:
            raise ValueError

    def calculate_big_man_scores(self) -> None:
        """Calculate the scores of all players in this graph.
        """
        for player in self._players:
            self._players[player].calculate_big_man_score()

    def connect_graph(self) -> None:
        """Connect a graph by creating edges based on individual big_man_score values."""
        self.calculate_big_man_scores()
        mapping = self._players.copy()

        for player in self._players:
            for other in self._players:
                difference = abs(mapping[player].big_man_score - mapping[other].big_man_score)
                if player != other and difference < 0.5:
                    self.add_edge(player, other)


python_ta.check_all(config={
    'extra-imports': ['__future', 'typing'],
    'allowed-io': [],
    'max-line-length': 100,
    'disable': ['E1136']
})
