-- Table definitions for the tournament project.

DROP DATABASE tournament;
CREATE DATABASE tournament;
\c tournament;


-- -- Creates Table: Tournament
-- DROP TABLE tournament;
CREATE TABLE tournament (t_id serial primary key NOT null,
                         name varchar (25) not null);
                         -- players int NOT NULL );


CREATE TABLE participant ( p_id int, 
                           t_id int,
                           foreign key (p_id) references players (p_id) on delete cascade,
                           foreign key (t_id) references tournament (t_id) on delete cascade,
                           primary key (p_id, t_id));


-- Creates Table: Players
-- DROP TABLE players;
CREATE TABLE players  ( p_id serial primary key NOT null,
                        name varchar (25) NOT null,
                        created_at timestamp default current_timestamp );

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
    SELECT winner_id, count(*) as wins, t_id
    FROM matches
    GROUP BY winner_id );

# don't remember why count(p_id=winner_id) doesn't return only winner_ids
CREATE VIEW v_matchcount AS (
    SELECT p_id, name, count(p_id=winner_id or p_id=loser_id) as matches, t_id
    FROM players left join matches on winner_id = p_id or loser_id = p_id
    group by p_id );

CREATE VIEW v_standings AS (
    SELECT p_id, name, t_id
       case when wins is NULL then 0 else wins end, matches
    FROM v_matchcount left join v_wincounts
    ON p_id = winner_id
    ORDER BY wins );


