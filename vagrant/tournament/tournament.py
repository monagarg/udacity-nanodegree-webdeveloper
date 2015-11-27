#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("Unable to connect to the database")

def disconnect(db):
    db.commit()
    db.close()

def deleteMatches():
    """Remove all the match records from the database."""

    # Connect to the database
    db, cursor = connect()

    # Create query to delete all data from the matches table
    query = "TRUNCATE matches;"

    # Execute the query
    cursor.execute(query)

    # Commit and close the connection
    disconnect(db)


def deletePlayers():
    """Remove all the player records from the database."""

    # Connect to the database
    db, cursor = connect()

    # Create query to delete all registered players from the players table
    query = "DELETE FROM players;"

    # Execute the query
    cursor.execute(query)

    # Commit and close the connection
    disconnect(db)


def countPlayers():
    """Returns the number of players currently registered."""

    # Connect to the database
    db, cursor = connect()

    # Create query to count the total number of registered users
    query = "SELECT count(*) FROM players;"

    # Execute the query
    cursor.execute(query)

    for record in cursor:
        return record[0]

    # Commit and close the connection
    disconnect(db)
    

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """

    # Connect to the database
    db, cursor = connect()

    # Create query to insert players in the players table by dynamically passing the name of the player
    query = "INSERT INTO players (name) VALUES (%s);"

    # Execute the query
    cursor.execute(query, (name, ))

    # Commit and close the connection
    disconnect(db)


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

    # Connect to the database
    db, cursor = connect()

    # Create query to select all data from standings
    query = "SELECT * FROM standings;"

    # Execute the query
    cursor.execute(query)

    records = cursor.fetchall()
    return records

    # Commit and close the connection
    disconnect(db)


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    # Connect to the database
    db, cursor = connect()

    # Create query to insert a match between two players in the matches table
    query = "INSERT INTO matches (winner,loser) VALUES (%s,%s);"

    # Execute the query
    cursor.execute(query, (winner, loser, ))

    # Commit and close the connection
    disconnect(db)
 
 
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

    # Connect to the database
    db, cursor = connect()

    # Create query to select the sum of wins of players from all the recorded matches
    query = "SELECT DISTINCT wins FROM standings;"

    final_paring = []

    # Execute the query and create query to select the players with a particular number of wins
    cursor.execute(query)
    records = cursor.fetchall()
    for row in records:
        query = "SELECT id,name FROM standings WHERE wins = (%s);"

        # Execute the query; randomize the same win players; create pairs and return the final pairs list
        cursor.execute(query, (row))
        record = cursor.fetchall()
        random.shuffle(record)

        for p1, p2 in zip(record[0::2], record[1::2]):
            final_paring.append((p1[0], p1[1], p2[0], p2[1]))

    # Commit and close the connection
    disconnect(db)
    return final_paring
