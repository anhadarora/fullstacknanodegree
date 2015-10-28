-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--

CREATE DATABASE tournament;
\c tournament;


-- -- Creates Table: Members
-- DROP TABLE members;

-- CREATE TABLE members;  ( mem_id serial primary key NOT null,
-- 						 name varchar (25) NOT null,
-- 						 wins real DEFAULT 0,
-- 						 matches int DEFAULT 0, );


-- -- Creates Table: Tournament

DROP TABLE tournament;

CREATE TABLE tournament (t_id serial primary key NOT null,
                         name varchar (25) not null);
                         -- players int NOT NULL );


-- Creates Table: Matches
DROP TABLE matches;

CREATE TABLE matches  ( m_id serial primary key NOT null,
                        winner_id int,
                        loser_id int,
                        t_id int NOT null,
                        foreign key (t_id) references tournament(t_id),                        
                        foreign key (winner_id) references players(p_id),
                        foreign key (loser_id) references players(p_id));


-- Creates Table: Players
DROP TABLE players;

CREATE TABLE players  ( p_id serial primary key NOT null,
                        name varchar (25) NOT null,
                        created_at timestamp default current_timestamp 
                        score real DEFAULT 0,
                        matches int DEFAULT 0, 
                        wins real DEFAULT 0 
                        t_id int NOT null,
                        foreign key (t_id) references tournament(t_id));


--# These are my 'create view' statements
CREATE VIEW standings as SELECT matches.winner_id, count(p_id) as num from matches GROUP BY p_id

    """Returns a list of the players and their win records, sorted by wins, for a 
    single tournament."""

    # c.execute("SELECT players.id, players.wins as Wins, count(matches.id) as Matches"
    #                 from players 
    #                 GROUP BY players.id
    #                 ORDER BY Wins DESC)
# create a view that shows player scores in tournament; these are columns that i pulled from previously set up players table
