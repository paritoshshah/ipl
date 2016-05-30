# parse fantasy.iplt20.com raw json stats to sqlite3 db

import json
import sqlite3

all_players = json.load(open('raw/2016/champ_player_price_2.json'))["player"]

# create table player_stats_2016_raw( player_id INT, team_id INT, points INT, full_name TEXT)
conn = sqlite3.connect('player_stats.db')
def persist_player_stats(stats):
    c = conn.cursor()
    data = [stats['player_id'], stats['team_id'], stats['points'], stats['full_name']]

    c.execute("insert into player_stats_2016_raw values(?,?,?,?)", data)
    conn.commit()
    c.close()

for p in all_players:
    persist_player_stats(p)
