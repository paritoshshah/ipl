# parse fantasy.iplt20.com raw json stats to sqlite3 db

import json
import sqlite3

# create table player_match_stats( player_id INT, match_id INT, opponent_id INT, opponent CHAR(50), batting_pts REAL, bowling_pts REAL, fielding_pts REAL, bonus_pts REAL, total_pts REAL )
conn = sqlite3.connect('player_stats.db')
def persist_player_stats(stats):
    c = conn.cursor()
    data = [stats['playerName'], stats['score']]
    c.execute("insert into player_stats_2016_raw values(?,?)", data)
    conn.commit()
    c.close()


for i in range(33, 35):
    all_players = json.load(open('raw/2016/' + str(i) + '.json'))
    for p in all_players:
        if p["matchCount"] == 1:
            persist_player_stats(p)
