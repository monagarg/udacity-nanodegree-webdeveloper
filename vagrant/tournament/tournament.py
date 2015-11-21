#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""

    # Create database connection
    conn = connect()
    db_cursor = conn.cursor()

    # Create query to delete all data from the matches table
    query = "DELETE FROM matches;"

    # Execute the query
    db_cursor.execute(query)

    # Commit and close the connection
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""

    # Create database connection
    conn = connect()
    db_cursor = conn.cursor()

    # Create query to delete all data registered players from the players table
    query = "DELETE FROM players;"

    # Execute the query
    db_cursor.execute(query)

    # Commit and close the connection
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""

    # Create database connection
    conn = connect()
    db_cursor = conn.cursor()

    query = "SELECT count(*) FROM players;"

    # Execute the query
    db_cursor.execute(query)

    for record in db_cursor:
        return record[0]

    # Commit and close the connection
    conn.commit()
    conn.close()


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """

    # Create database connection
    conn = connect()
    db_cursor = conn.cursor()

    query = "INSERT INTO players (name) VALUES (%s);"

    # Execute the query
    db_cursor.execute(query,(name,))

    # Commit and close the connection
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    # Create database connection
    conn = connect()
    db_cursor = conn.cursor()

    query = "SELECT * FROM standings;"

    # Execute the query
    db_cursor.execute(query)

    records = db_cursor.fetchall()
    
    return records

    # Commit and close the connection
    conn.commit()
    conn.close()


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    # Create database connection
    conn = connect()
    db_cursor = conn.cursor()

    query = "INSERT INTO matches (winner,loser) VALUES (%s,%s);"

    # Execute the query
    db_cursor.execute(query,(winner,loser,))

    # Commit and close the connection
    conn.commit()
    conn.close()
 
 
def swissPairings():
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
    """

    # Create database connection
    conn = connect()
    db_cursor = conn.cursor()

    query = "SELECT DISTINCT total_wins FROM initial_pairing;"

    final_paring = []

    # Execute the query
    db_cursor.execute(query)
    records = db_cursor.fetchall()
    for row in records:
        query = "SELECT DISTINCT ip.id,p.name FROM initial_pairing ip, players p WHERE total_wins = (%s) AND ip.id = p.id;"

        # Execute the query
        db_cursor.execute(query,(row))
        record = db_cursor.fetchall()
        random.shuffle(record)
        print record
        if len(record)%2 == 0:
            i=0
            while(i<len(record)):
                record1 = record[i]+record[i+1]
                final_paring.append(record1)
                i = i+2

    return final_paring

    # Commit and close the connection
    conn.commit()
    conn.close()

