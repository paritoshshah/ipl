# scrape fantasy.iplt20.com for player stats

import sys
import urllib
import httplib2
import json
import sqlite3

def fetch_data(url):
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    headers = { 'Cookie': 'session_id_ifl="64609:a91b2faf-6814-4094-b4db-125ac236d34c"' }
    return json.loads(http.request(url, 'GET', headers=headers)[1])

all_players = fetch_data('https://fantasy.iplt20.com/ifl/research/get_res_data_list.json?json')["players"]

def get_player_stats(player_id):
    return fetch_data('https://fantasy.iplt20.com/ifl/research/get_player_stats.json?player_id=' + str(player_id) + '&json')["player_stats"]

# create table player_match_stats( player_id INT, match_id INT, opponent_id INT, opponent CHAR(50), batting_pts REAL, bowling_pts REAL, fielding_pts REAL, bonus_pts REAL, total_pts REAL )
conn = sqlite3.connect('player_match_stats_2014.db')
def persist_player_match_stats(stats):
    c = conn.cursor()
    data = [stats['player_id'], stats['match_id'], stats['bteam'], stats['longname'], stats['batting_pts'], stats['bowling_pts'], stats['fielding_pts'], stats['bonus_pts'], stats['total_pts']]

    c.execute("insert into player_match_stats values(?,?,?,?,?,?,?,?,?)", data)
    conn.commit()
    c.close()

for p in all_players:
    player_stats = get_player_stats(p['id'])
    for stat in player_stats:
        persist_player_match_stats(stat)
