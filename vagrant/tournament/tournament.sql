-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create the tournament database
CREATE DATABASE tournament;

-- Create a table 'players' to register players
CREATE TABLE  players (id SERIAL PRIMARY KEY, name TEXT);

-- Create a table 'matches' to report the outcome of a single match between two players
CREATE TABLE matches (id SERIAL, winner INTEGER REFERENCES players(id), loser INTEGER REFERENCES players(id));

-- Create a view 'standings' to return the current position of players, total wins, and total matches
CREATE VIEW standings AS SELECT p.id,p.name,(SELECT count(winner) FROM matches m WHERE m.winner = p.id) AS wins, (SELECT (SELECT count(winner) FROM matches m WHERE m.winner = p.id)+(SELECT count(loser) FROM matches m WHERE m.loser=p.id)) AS matches FROM players p;

-- Create a view of 'initial_pairing' to help create swiss pairing
CREATE VIEW initial_pairing AS SELECT id, sum(wins) AS total_wins FROM standings GROUP BY id ORDER BY total_wins DESC;

