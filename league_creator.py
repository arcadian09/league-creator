#! /usr/bin/env python3
"""
D.D.O League Creator
Input csv for players.
"""

__author__ = "Oleg Tarassov"
__email__ = "oleg.tarassov@outlook.com"
__version__ = "1.0"
__status__ = "Final"
__date__ = "30-03-2017"

import csv
import sys
import logging

FILE_PLAYERS = 'soccer_players.csv'
FILE_TEAMS = 'soccer_teams.csv'

class Player:
    """ Holds Player information
        mandatory: name, parent/responsible,
        optional : preference (team, player, coach)
        In the end: team assigned
    """
    __slots__ = ['name', 'guardian', 'team', 'pref']

    def __init__(self, name=None, guardian=None, pref=None, team=None):
        """Initialize all variables"""
        self.name = name
        self.guardian = guardian
        self.team = team

        if pref == '':
            self.pref = None
        else:
            req, cond = tuple(pref.split(":"))
            self.pref = dict()
            self.pref[req] = cond

    def __str__(self):
        """Print Players attributes"""
        return '(name:%s, parent:%s, team:%s, preference:%s)' \
                % (self.name, self.guardian, self.team, self.pref)


class League:
    """ Contains: teams, coaches, players """

    __slots__ = ['teams', 'coaches', 'players']

    def __init__(self):
        self.teams = dict()
        self.coaches = dict()
        self.players = list()
        logging.basicConfig(filename='league_creator.log', filemode='w', level=logging.INFO)

    def __str__(self):
        buff = list()
        buff.append("============================================")
        buff.append("Coach\tTeam")
        buff.append("---------------")

        for key in self.coaches:
            buff.append("{}\t{}".format(key, self.coaches[key]))

        buff.append("")
        buff.append("Team\tPlayers")
        buff.append("---------------")

        for key in self.teams:
            buff.append("{}\t{}".format(key, self.teams[key]))

        buff.append("============================================")

        return "\n".join(buff)


    def load_from_file(self, filename, load):
        """Read CSV and loads the appropriate type of data
           into the corresponding attributes
        """

        with open(filename, 'r') as csvfile:
            data_extract = csv.DictReader(csvfile, delimiter=',')

            if load == 'teams':
                for team in data_extract:
                    if team['Coach'] != '':
                        self.coaches[team['Coach']] = team['Team']

                    self.teams[team['Team']] = list()

            elif load == 'players':
                for player in data_extract:
                    player_details = Player(player['Name'], player['Guardian Name(s)'],
                                            player['Preference'])

                    self.players.append(player_details)
            else:
                sys.exit("ERROR: Incorrect load type:{}".format(load))


    def list_filter(self, req):
        """ Split list based on player requirements"""
        return [free_agent for free_agent in self.players
                if free_agent.pref is not None and req in free_agent.pref]


    def add_player(self, new_player, cond=None):
        """ Adds Player to a team
            Uses condition type or randam add.
        """

        #TODO: need to add try catch for incorrect team return

        if cond is not None:
            req_team = self.get_team(new_player, cond)
            logging.info('%s Pref Added: %s to %s', cond, new_player.name, new_player.pref[cond])
        else:
            req_team = self.get_team(new_player)
            logging.info('Added: %s to %s', new_player.name, req_team)

        #Adds player to team and team to player
        self.teams[req_team].append(new_player.name)
        new_player.team = req_team


    def get_team(self, pl, cond=None):
        """ Return team
            random or based on preference.
        """

        #TODO need to add try catch for cond which is preference type.

        if cond == 'team':
            return pl.pref[cond]
        elif cond == 'coach':
            return self.coaches[pl.pref[cond]]
        elif cond == 'friend':
            match = next((l for l in self.players if pl.pref[cond] in l.name), None)

            if match is not None and match.team is not None:
                return match.team
            else:
                logging.info('Failed to find friend: %s for %s', pl.pref[cond], pl.name)

        #Gets Random team if no condition or friend is not found
        team_sizes = {len(value):key for key, value in self.teams.items()}
        return team_sizes[min(team_sizes, key=int)]


def main():
    """ Main Program"""

    u7 = League()

    u7.load_from_file(FILE_TEAMS, 'teams')
    u7.load_from_file(FILE_PLAYERS, 'players')

    players_team_pref = u7.list_filter('team')
    players_coach_pref = u7.list_filter('coach')
    players_friend_pref = u7.list_filter('friend')

    #Load players that want to be in a particular team
    for free_agent in players_team_pref:
        u7.add_player(free_agent, 'team')
    #Load players that want to be in coach team
    for free_agent in players_coach_pref:
        u7.add_player(free_agent, 'coach')
    #Load players that do not have any requirements
    for free_agent in u7.players:
        if free_agent.pref is None:
            u7.add_player(free_agent)
    #Load players that want to be in friend team
    for free_agent in players_friend_pref:
        u7.add_player(free_agent, 'friend')

    #Executive Summary
    print(u7)

    #Clean Up
    del u7


if __name__ == '__main__':
    main()
