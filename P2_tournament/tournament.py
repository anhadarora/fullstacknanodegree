#!/usr/bin/env python

# tournament.py -- implementation of a Swiss-system tournament
import psycopg2

dbname = 'tournament'


def connect(dbname):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deletePlayers():
    """Removes all the player records from the database."""
    db = connect(dbname)
    c = db.cursor()
    c.execute("DELETE FROM players;")
    db.commit()
    db.close()
    return db


def deleteMatches(t_id='', m_id=''):
    """Removes match records of a round from the database. If no match id is given,
    all matches from a tourney are deleted. If no argument is given,
    all matches will be deleted.

    Args:
    t_id: tournament id
    m_id: match round id
    """
    db = connect(dbname)
    c = db.cursor()
    if t_id != '' and m_id != '':
        c.execute("DELETE FROM matches"
                  "WHERE t_id = %s AND m_id = %s", (t_id, m_id,))
    elif t_id != '' and m_id == '':
        c.execute("DELETE FROM matches"
                  "WHERE t_id = %s", (t_id,))
    else:
        c.execute("DELETE FROM matches;")

    db.commit()
    db.close()
    return db


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect(dbname)
    c = db.cursor()
    c.execute("SELECT COUNT(p_id) from players;")
    result = c.fetchone()[0]
    db.close()
    return result

# extra credit
# """Support more than one tournament in the database, so matches do not have
# to be deleted between tournaments. This will require distinguishing between
# player and a player who has entered in tournament (a participant) """


def registerTournament(name):
    """Add a tournament to the tournament database.
    Args:
      name: name of tournament to register

      Returns:
    t_id: id of the registered tournament

    """
    db = connect(dbname)
    c = db.cursor()
    c.execute("INSERT INTO tournament(name)"
              "VALUES (%s)", (name,))
    db.commit()
    db.close()


def registerPlayer(name=''):
    """Adds a player to the overall league.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      p_id: the player's member id.
    """
    db = connect(dbname)
    c = db.cursor()
    c.execute("INSERT INTO players(name)"
              "VALUES (%s)", (name,))
    db.commit()
    db.close()


def registerParticipant(player, tournament):
    """Register a player in a tournament as a participant.
    Args:
        player: p_id of the player to register
      tournament: t_id of the tournament to register player in
    returns: rowcount of the player inserted, 0 | 1
    """
    db = connect(dbname)
    c = db.cursor()
    c.execute("INSERT INTO participant(p_id, t_id)"
              "VALUES (%s, %s)", (player, tournament))
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of msatches the player has played
    """
    db = connect(dbname)
    c = db.cursor()
    c.execute("SELECT * FROM v_standings;")
    results = []
    for row in c.fetchall():
        if row[2] is None:
            wins = 0
        else:
            wins = row[2]
        results.append((row[0], str(row[1]), wins, row[3]))
    db.close()
    return results


def playerStandingsTournament(tournament):
    """
    Returns a list of the players and their win records, sorted by wins, for a
    single tournament.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Arg:
        tournament: tournament's t_id

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of msatches the player has played
    """
    db = connect(dbname)
    c = db.cursor()
    c.execute("SELECT * FROM v_standings"
              "WHERE t_id = tournament;")
    results = []
    for row in c.fetchall():
        if row[2] is None:
            wins = 0
        else:
            wins = row[2]
        results.append((row[0], str(row[1]), wins, row[3]))
    db.close()
    return results


def reportMatch(win_id='', lose_id=''):
    """Records the outcome of a single match between two players to the matches
    table.

    Args:
      win_id: the id number of the player who won
      lose_id: the id number of the player who lost

    """
    # set records of match both in match table and player table
    db = connect(dbname)
    c = db.cursor()
    c.execute("INSERT INTO matches (winner_id, "
              "loser_id) "
              "VALUES (%s, %s)", (win_id, lose_id))
    db.commit()
    db.close()


def reportMatchToTournament(win_id='', lose_id='', t_id=''):
    """Records the outcome of a single match between
    two players to the matches table.

    Args:
      t_id: tournament id
      win_id: the id number of the player who won
      lose_id: the id number of the player who lost

    """
    # set records of match both in match table and player table
    db = connect(dbname)
    c = db.cursor()
    c.execute("INSERT INTO matches (winner_id, "
              "loser_id, t_id) "
              "VALUES (%s, %s, %s)", (win_id, lose_id, t_id,))
    db.commit()
    db.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player
    adjacent to him or her in the standings.

    Given the existing set of registered players and the matches they have
    played, generates and returns a list of pairings according to the
    Swiss system. Each pairing is a tuple (id1, name1, id2, name2), giving
    the ID and name of the paired players. For instance, if there are eight
    registered players, this function should return four pairings. This
    function should use playerStandings to find the ranking of players.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db = connect(dbname)
    standings = [(playerInfo[0], playerInfo[1])
                 for playerInfo in playerStandings()]
    if len(standings) < 2:
        raise KeyError("Not enough players.")
    i = 0
    pairings = []
    while i < len(standings):
        p_id = standings[i][0]
        p_name = standings[i][1]
        o_id = standings[i + 1][0]
        o_name = standings[i + 1][1]
        pairings.append((p_id, p_name, o_id, o_name))
        i = i + 2

    db.commit()
    db.close()
    return pairings
