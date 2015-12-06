-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

\c postgres

SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'tournament'
AND pid <> pg_backend_pid();

-- Drop view, tables, and database if already exists with the same names as the below create statements
DROP DATABASE IF EXISTS tournament;

-- Create the tournament database
CREATE DATABASE tournament;

-- Connect to the database
\c tournament

-- Create a table 'players' to register players
CREATE TABLE players (id SERIAL PRIMARY KEY, name TEXT NOT NULL);

-- Create a table 'matches' to report the outcome of a single match between two players
CREATE TABLE matches (id SERIAL PRIMARY KEY, winner INTEGER REFERENCES players(id) ON DELETE CASCADE, loser INTEGER REFERENCES players(id) ON DELETE CASCADE, CHECK (winner <> loser));

-- Create a view 'standings' to return the current position of players, total wins, and total matches
CREATE VIEW standings AS SELECT p.id,p.name,(SELECT count(winner) FROM matches m WHERE m.winner = p.id) AS wins, (SELECT (SELECT count(winner) FROM matches m WHERE m.winner = p.id)+(SELECT count(loser) FROM matches m WHERE m.loser=p.id)) AS matches FROM players p order by wins desc;
