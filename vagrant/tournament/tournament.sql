-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create the tournament database
CREATE DATABASE tournament;

CREATE TABLE  players (ID serial primary key, name text);

CREATE TABLE matches (ID serial references players(ID), win int, match int);

insert into players (name) values ('mona');

select count(ID) from players;
