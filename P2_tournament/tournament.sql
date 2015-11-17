-- Table definitions for the tournament project.

DROP DATABASE tournament;
CREATE DATABASE tournament;
\c tournament;


-- -- Creates Table: Tournament
-- DROP TABLE tournament;
CREATE TABLE tournament (t_id serial primary key NOT null,
                         name varchar (25) not null);
                         -- players int NOT NULL );


-- Creates Table: Players
-- DROP TABLE players;
CREATE TABLE players  ( p_id serial primary key NOT null,
                        name varchar (25) NOT null,
                        created_at timestamp default current_timestamp, 
                        t_id int,
                        foreign key (t_id) references tournament(t_id));

-- Creates Table: Matches
-- DROP TABLE matches;
CREATE TABLE matches  ( m_id serial primary key NOT null,
                        winner_id int,
                        loser_id int,
                        t_id int,
                        foreign key (t_id) references tournament(t_id),                        
                        foreign key (winner_id) references players(p_id),
                        foreign key (loser_id) references players(p_id));


CREATE VIEW v_wincounts AS (
    SELECT winner_id, count(*) as wins
    FROM matches
    GROUP BY winner_id );

CREATE VIEW v_matchcount AS (
    SELECT p_id, name, count(p_id=winner_id) as matches
    FROM players left join matches on winner_id = p_id or loser_id = p_id
    group by p_id );

CREATE VIEW v_standings AS (
    SELECT id, name
       case when wins is NULL then 0 else wins end, matches
    FROM v_matchcount left join v_wincounts
    on p_id = winner_id
    order by wins );


--Creates a view that shows player standings in tournament;
CREATE VIEW standings as (
    SELECT p.p_id, p.name, COUNT(m.winner_id) as winCount, COUNT(m.m_id) as matchCount
    FROM players p LEFT JOIN matches m ON p.p_id = m.winner_id OR p.p_id = m.loser_id
    GROUP BY p.p_id                        
    ORDER BY winCount DESC, matchCount DESC 
);

--# create a view that shows player aggregate matches across 
-- https://github.com/DavyK/udacityFSWD_p2/blob/master/tournament.sql
-- https://github.com/ghunt03/P2---Swiss-Tournament/blob/master/tournament.py


-- --Creates a view that counts the number of wins each player has in a tournament;
-- CREATE VIEW player_wins AS (
--     SELECT players.id, players.name, COUNT(winner_id) as num_wins, players_in_tournaments.tournament_id
--     FROM players LEFT JOIN matches ON players.id = matches.winner_id OR (players.id = matches.looser_id and draw = 't')
--     LEFT JOIN players_in_tournaments ON players.id = players_in_tournaments.player_id
--     GROUP BY players.id, players_in_tournaments.tournament_id
--     ORDER BY num_wins DESC
-- );

-- --Creates a view that counts the number of matches each player has in a tournament;
-- CREATE VIEW player_matches AS (
--     SELECT p.p_id, p.name, COUNT(m.m_id) as matchCount, m.t_id
--     FROM players p LEFT JOIN matches m ON p.p_id = m.winner_id OR p.p_id = m.loser_id
--     LEFT JOIN players_in_tournaments ON p.p_id = players_in_tournaments.player_id
--     ORDER BY matchCount DESC
-- ); sum(count(m.winner_id) + count(m.loser_id))
