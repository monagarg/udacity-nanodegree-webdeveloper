-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create the tournament database
CREATE DATABASE tournament;

CREATE TABLE  players (id SERIAL PRIMARY KEY, name TEXT);

CREATE TABLE matches (id SERIAL, winner INTEGER REFERENCES players(id), loser INTEGER REFERENCES players(id));

INSERT INTO players (name) VALUES ('mona');

INSERT INTO matches (winner,loser) VALUES (31,32)

CREATE VIEW standings AS select p.id,p.name,(select count(winner) from matches m where m.winner = p.id) as wins, (SELECT (select count(winner) from matches m where m.winner = p.id)+(select count(loser) from matches m where m.loser=p.id)) as matches from players p;

select id, sum(wins) as total_wins from standings group by id order by total_wins desc;

psql
\c tournament
\q
\dt 