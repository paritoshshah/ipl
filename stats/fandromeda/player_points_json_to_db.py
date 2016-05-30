# parse fantasy.iplt20.com raw json stats to sqlite3 db

import json
import sqlite3

all_players = json.load(open('raw/2016/player_points_champ.json'))["player_points"]

# create table player_matches_2016_raw( player_id INT, team_id INT, match_id INT );
conn = sqlite3.connect('player_stats.db')
def persist_player_stats(stats):
    c = conn.cursor()
    data = [stats['player_id'], stats['team_id'], stats['match_id']]

    c.execute("insert into player_matches_2016_raw values(?,?,?)", data)
    conn.commit()
    c.close()

for p in all_players:
    persist_player_stats(p)
