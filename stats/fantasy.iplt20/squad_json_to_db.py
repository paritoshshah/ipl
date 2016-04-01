# parse fantasy.iplt20.com raw json stats to sqlite3 db

import json
import sqlite3


# create table player_match_stats( player_id INT, match_id INT, opponent_id INT, opponent CHAR(50), batting_pts REAL, bowling_pts REAL, fielding_pts REAL, bonus_pts REAL, total_pts REAL )
conn = sqlite3.connect('player_stats.db')
def persist_player_team(player, team_id, team):
    c = conn.cursor()
    data = [player, team_id, team]
    c.execute("insert into squads_2016 values(?,?,?)", data)
    conn.commit()
    c.close()

squads = json.load(open('raw/2016/squads.json'))["squads"]

for i in range(len(squads)):
    team = squads[i]["team"]["abbreviation"]
    players = squads[i]["players"]

    for p in players:
        player = p["fullName"]
        persist_player_team(player, i, team)
