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

# def registerMember(name):
#     """Adds a permanent member to the database.
  
#     Args:
#       name: the player's full name (need not be unique).
#     """
#     db = connect(dbname)
#     c = db.cursor()
#     c.execute("INSERT INTO members "
#               "VALUES (DEFAULT, %s)", (name,))

    # c.execute("SELECT id FROM members WHERE name = %s", (name,))
    # new_id = c.fetchall()
    # db.commit()
    # db.close()
    # return new_id[0][0]
#     db.commit()
#     db.close()


def registerPlayer(name=''):
    """Adds a player to the current tournament database.
  
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

# def registerPlayerTournament(name='', t_id=''):
#     """Adds a player to the current tournament database.
  
#     The database assigns a unique serial id number for the player.  (This
#     should be handled by your SQL database schema, not in your Python code.)
  
#     Args:
#       p_id: the player's member id.
#     """
#     db = connect(dbname)
#     c = db.cursor()
#     c.execute("INSERT INTO players(name, t_id)"
#               "VALUES (%s, %s)", (name, t_id))
#     db.commit()
#     db.close()

# def registerPlayer(p_id):
#     """Adds a player, or list of players, to the current tournament database.
#     Args:
#       p_id: the player's member id.
#     """
#     db, c = connect()
#     c.execute("INSERT INTO players (id, name, seed_score) "
#               "SELECT id, name, "
#               "COALESCE(wins / NULLIF(matches,0), 0) "
#               "FROM members "
#               "WHERE id = %s", (p_id,))
#     db.commit()
#     db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins, for a 
    single tournament.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Arg:
        t_id: tournament id **need to reinsert this t_id='' in the function, and reinsert this in the body of function WHERE tournament_id = %i......(t_id,)

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of msatches the player has played
    """
    db = connect(dbname)
    c = db.cursor()
    c.execute("SELECT players.p_id, players.name, COUNT(matches.winner_id) as winCount, COUNT(matches.m_id) as matchCount "
              "FROM players LEFT JOIN matches ON players.p_id = matches.winner_id OR players.p_id = matches.loser_id "
              "GROUP BY players.p_id "                     
              "ORDER BY winCount DESC, matchCount DESC;")
    # c.execute("SELECT id, name, winCount, matchCount FROM standings WHERE t_id = %s;" (t_id,))
    # q_result = c.fetchall()
    # return results
    #  c.execute("SELECT * FROM standings;") initiate this once i've created this query as a view
    results = []
    for row in c.fetchall():
        if row[2] == None:
            wins = 0
        else:
            wins = row[2]
        results.append((row[0], str(row[1]), wins, row[3])) #why?!?!
        # result.append(row[0], row[1], wins, row[2])
    db.close()
    return results
    
    db.commit()
    db.close()

def reportMatch(win_id='', lose_id=''):
    """Records the outcome of a single match between two players to the matches table.

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

# def reportMatchToTournament(win_id='', lose_id='', t_id=''):
#     """Records the outcome of a single match between two players to the matches table.

#     Args:
#       t_id: tournament id **** insert back into arguments
#       m_id: match(round) id
#       win_id: the id number of the player who won
#       lose_id: the id number of the player who lost

#     """
#     # set records of match both in match table and player table
#     db = connect(dbname)
#     c = db.cursor() 
#     c.execute("INSERT INTO matches (winner_id, "
#               "loser_id, t_id) "
#               "VALUES (%s, %s, %s)", (win_id, lose_id, t_id,))
#     db.commit()
#     db.close()


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
        diff: the absolute difference in players' match points for unique tournament
    """
    db = connect(dbname)
    c = db.cursor()
    standings = [(playerInfo[0], playerInfo[1]) for playerInfo in playerStandings()]
    if len(standings) < 2:
        raise KeyError("Not enough players.")
    i=0
    pairings = []
    while i < len(standings):
        p_id = standings[i][0]
        p_name = standings[i][1]
        o_id = standings[i+1][0]
        o_name = standings[i+1][1]
        pairings.append((p_id, p_name, o_id, o_name))
        i=i+2

    db.commit()
    db.close()

# flatten the pairings and convert back to a tuple
# results = [tuple(list(sum(pairing, ()))) for pairing in pairings]

#     return pairings
#     c.execute("SELECT * FROM matches where tourney_id = {t_id} ; ").format(t_id=t_id) )
#     matchesPlayed = fetchall()
#     c.execute("SELECT p.id, p.name, o.id, o.name FROM playerStandings AS p,"
#               "playerStandings AS o WHERE p.wins = o.wins AND p.id > o.id")
#     result = c.fetchall()
#     return [ row for row in result]
# """
    
#     players, opponents = [], []
#     players = standings[0::2]
#     opponents = standings[1::2]

#     for p_id, opp_id in players, opponents :
#         pairings = []
#         if zip(players[p_id], opponents[id]) in pairings
#             zip(players[p_id], opponents[opp_id])
#     map(zip(players, opponents))
#     in_progress = c.fetchone()
