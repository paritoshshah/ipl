# parse fantasy.iplt20.com raw json stats to sqlite3 db

import json
import sqlite3

all_players = json.load(open('raw/2014/player_researchall.json'))["players"]

vfm_factor = 24.0*750000*12/119

# create table player_match_stats( player_id INT, match_id INT, opponent_id INT, opponent CHAR(50), batting_pts REAL, bowling_pts REAL, fielding_pts REAL, bonus_pts REAL, total_pts REAL )
conn = sqlite3.connect('player_stats.db')
def persist_player_stats(stats):
    c = conn.cursor()
    if stats['vfm'] == None:
        num_games = 0
    else:
        num_games = int(round(vfm_factor * stats['fanta_points']/ (stats['price'] * stats['vfm'])))
    data = [stats['id'], stats['firstname'], stats['bat_points'], stats['bol_points'], stats['field_points'], stats['bonus_points'], stats['fanta_points'], num_games, 2014]

    c.execute("insert into player_stats values(?,?,?,?,?,?,?,?,?)", data)
    conn.commit()
    c.close()

for p in all_players:
    persist_player_stats(p)
