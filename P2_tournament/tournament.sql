-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--

CREATE DATABASE tournament;
\c tournament;


-- Creates Table: Members
DROP TABLE members;

CREATE TABLE members;  ( mem_id serial primary key NOT null,
						 name varchar (25) NOT null,
						 wins real DEFAULT 0,
						 matches int DEFAULT 0, );

-- Creates Table: Tournament

DROP TABLE tournament;

CREATE TABLE tournament ( t_id serial primary key NOT null,
                         name varchar (25) not null,
                         players int NOT NULL );

-- Creates Table: Matches
DROP TABLE matches;

CREATE TABLE matches  ( m_id serial primary key NOT null,
                        winner_id int,
                        loser_id int,
                        t_id int NOT null,
                        foreign key (winner_id) references players(id),
                        foreign key (loser_id) references players(id),
                        foreign key (t_id) references tournament(t_id) );

-- Creates Table: Players

DROP TABLE players;

CREATE TABLE players  ( p_id serial primary key NOT null,
						score real DEFAULT 0,
                        name varchar (25) NOT null,
                        matches int DEFAULT 0, # pulls and inserts into members.matches?
                        wins real DEFAULT 0, # pulls and inserts into members.wins?
                        created_at timestamp default current_timestamp );


--# These are my 'create view' statements
