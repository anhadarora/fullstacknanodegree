#!/usr/bin/env python

# tournament.py -- implementation of a Swiss-system tournament
#referring to these projects below and reverse engineering in a way that I understand
#basic:https://github.com/allanbreyes/udacity-full-stack/blob/master/p2/vagrant/tournament/tournament.py
#medium: https://github.com/shteeven/fullstack/blob/master/vagrant/tournament/tournament.py
#convoluted: https://github.com/rajputss/FSND_Project2_RelationalDatabase_Tournament

import psycopg2

dbname = 'tournament'

def connect(dbname):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deletePlayers():
    """Removes all the player records from the database."""
    db = connect(dbname)
    c = db.cursor()
    c.execute("DELETE FROM Players;")
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
    c.execute("SELECT COUNT(id) from players;")
    result = c.fetchone()[0] # <---figure out why this works
    db.close()
    return result

def registerMember(name):
    """Adds a permanent member to the database.
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect(dbname)
    c = db.cursor()
    c.execute("INSERT INTO members "
              "VALUES (DEFAULT, %s)", (name,))
    db.commit()
    db.close()

def registerPlayer(p_id):
    """Adds a player to the current tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      p_id: the player's member id.
    """
    db = connect(dbname)
    c = db.cursor()
    c.execute("INSERT INTO players (id, name, score)"
              "VALUES (DEFAULT, %s)", (name,))
    db.commit()
    db.close()


def playerStandings(t_id):
    """Returns a list of the players and their win records, sorted by wins, for a 
    single tournament.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Arg:
        t_id: tournament id

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect(dbname)
    c = db.cursor()
    c.execute("SELECT players.id, players.wins as Wins, count(matches.id) as Matches"
                    from players 
                    GROUP BY players.id
                    ORDER BY Wins DESC)
    result = c.fetchall()
    db.commit()
    db.close()
    return result


def reportMatch(t_id='', m_id='', win_id='', lose_id='', outcome='', draw=False, bye=False):
    """Records the outcome of a single match between two players to the matches and 
    players' tables; it does not update the members table, the members table is 
    updated with match results in the endTournament function.


    Args:
      t_id: tournament id
      m_id: match(round) id
      win_id: the id number of the player who won
      lose_id: the id number of the player who lost
      draw: draw if True; can accept False (optional)
      bye: bye if True; can accept False (optional)
    """

    db = connect(dbname)
    c = db.cursor() 
    # set records with 'draw' points
    if draw is True:
        # update player 1 record [need to change to update ]
        c.execute("UPDATE players "
                  "SET wins = (wins + .5), matches = (matches + 1) "
                  "WHERE id = %s", (lose_id,))
        # update player 2 record
        c.execute("UPDATE players "
                  "SET wins = (wins + .5), matches = (matches + 1) "
                  "WHERE id = %s", (win_id,))
        # update player 1 tourney card
        c.execute("INSERT INTO matches (t_id, m_id, p_id, "
                  "opp_id, outcome) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (t_id, m_id, win_id, lose_id, .5))
        # update player 2 tourney card
        c.execute("INSERT INTO matches (t_id,m_id, p_id, "
                  "opp_id, outcome) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (t_id, m_id, lose_id, win_id, .5))
    
    # set records of match both in match table and player table
    elif draw is False:
        
        if bye is True: 
            # update p_id record with 'BYE' listed as the opponent
            c.execute("UPDATE players "
                      "SET matches = (matches + 1)"
                      "WHERE id = %s;", (p_id,)) # or (win_id,)?
            c.execute("INSERT INTO matches (t_id, m_id, p_id, opp_id, outcome)"
                      "VALUES (%s, %s, %s, 'BYE', 0)",
                      (t_id, m_id, p_id)

        elif bye is False:
            # update lose_id record
            c.execute("UPDATE players "
                      "SET matches = (matches + 1) and bye = TRUE "
                      "WHERE id = %s;", (lose_id,))
            c.execute("INSERT INTO matches (t_id, m_id, p_id, "
                      "opp_id, outcome) "
                      "VALUES (%s, %s, %s, %s, %s)",
                      (t_id, m_id, lose_id, win_id, 0))
            
            # update win_id record
            c.execute("UPDATE players "
                      "SET wins = (wins + 1), matches = (matches + 1) "
                      "WHERE id = %s;", (win_id,))
            c.execute("INSERT INTO matches (t_id, m_id, p_id, "
                      "opp_id, outcome) "
                      "VALUES (%s, %s, %s, %s, %s)",
                      (t_id, m_id, win_id, lose_id, 1))
 
def swissPairings(t_id):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
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
    c.execute("SELECT * FROM matches where tourney_id = {t_id} ; ").format(t_id=t_id) )
    matchesPlayed = fetchall()
    
    c.execute("SELECT id,name,wins FROM Players ORDER BY wins DESC;")
    standings = c.fetchall()

"""
    # player receives a bye if odd number of players [figure this out at the end]
    if len(standings) % 2 != 0:
        c.execute("INSERT INTO players (id, name, seed_score) "
                      "VALUES (2147483647, 'BYE', 0)")
OR USE
        reportMatch(t_id='t_id', m_id='', win_id='p_id', lose_id='BYE', outcome=0, bye=True):
        standings.pop()

        db.commit()
        db.close()

        for standing in reversed(standings):
            player, _ = standing
            if not player_has_received_bye(player, tournament):
                report_match_bye(player, tournament)
                standings.pop(standings.index(standing))
                break

OR USE

    c.execute("SELECT p.id, p.name, o.id, o.name FROM playerSTANDINGS AS p,"
              "playerSTANDINGS AS o WHERE p.wins = o.wins AND p.id > o.id")
    result = c.fetchall()
    return [ row for row in result]
"""
    
    players, opponents = [], []
    players = standings[0::2]
    opponents = standings[1::2]

    for p_id, opp_id in players, opponents :
        pairings = []
        if zip(players[p_id], opponents[id]) in pairings
            zip(players[p_id], opponents[opp_id])
 

    map(zip(players, opponents))

    in_progress = c.fetchone()
    db.commit()
    db.close()


    i=0
    pairings = []
    while i < len(standings):
        p_id = standings[i][0]
        p_name = standings[i][1]
        o_id = standings[i+1][0]
        o_name = standings[i+1][1]
        pairings.append((p_id, p_name, o_id, o_name))
        i=i+2

    return pairings

OR USE

pairs = []
    for p in players:
        opp = remainingOpp(t_id, i)
        for x in opp:
            opp = x[1]
            if opp in players and p in players:
                pairs.append(players.pop(p))
                pairs.append(players.pop(opp))


"""
    if in_progress == None:
        # initial pairings
        if num_players % 2 != 0:
            db = connect(dbname)
            c = db.cursor()
            c.execute("INSERT into players (id, name, score"
                      "VALUES (?, 'BYE', 0)")
            db.commit
        num_players = countPlayers()
        players = [row[0] for row in playerStandings(t_id)]
        pairs_list = []
        for i in range(num_players/2):
            pairs_list.append((players[i], players[i + num_players/2], 0)) #returns a tuple of the two participants
    else:
        #subsequent pairing
        players = [row[0] for row in playerStandings(t_id)]
        pairs_list = pairFinder(t_id, players, num_players)
    if len(pairs_list) == (num_players / 2): #why does this have to be put in? to make sure there are no errors?
        return pairs_list
    else:
        raise ValueError("swissPairings is not returning the expected number of pairs.")

"""
def remainingOpp(t_id, p_id): 
    """
    Returns a list of opponents that a player has not yet had a match with.

    The first entry in the list should be the opponent with the closest amount of wins.

    Returns:
        A list of tuples, each of which contains (id, opponent_id, diff):
        id: the player's unique id (assigned by the database)
        opponent_id: the opponent's unique id (assigned by the database)
        diff: absolute difference in win totals
    """

    db = connect(dbname)
    c = db.cursor()
    c.execute(  "SELECT p.p_id, o.p_id"
                "FROM players p, players o"
                "WHERE p.p_id = {p_id} AND o.p_id != p.p_id AND o.p_id NOT IN"
                "(SELECT opp_id FROM matches"
                "WHERE p_id = p.p_id AND t_id = {t_id}) "
                "ORDER BY wins DESC, ; ").format(p_id = 'p_id', t_id = 't_id')
    remainingOpp = c.fetchall
    db.commit()
    db.close
    return remainingOpp
