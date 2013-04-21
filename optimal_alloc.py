# optimal allocation for fantasy IPL
# 9 teams, 10 players to be picked for a given match
# 1 substitution allowed before each match
# given a schedule of matches and a starting lineup print the optimal
# next substitute

import sys
import urllib
import httplib2
import json

ga = [[] for i in range(9)]
fanta_team = []
teams = { 'CSK':0,'DD':1,'KKR':2,'KXIP':3,'MI':4,'PWI':5,'RCB':6,'RR':7,'SH':8 }
teams_list = ['CSK','DD','KKR','KXIP','MI','PWI','RCB','RR','SH']
s = []
top_picks = [[] for i in range(9)]

def fetch_data(url):
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    headers = { 'Cookie': 'session_id_ifl="966:4c650ae2-0b1b-4e77-ac1b-4c6222b0e136"' }
    return json.loads(http.request(url, 'GET', headers=headers)[1])

all_players = fetch_data('https://fantasy.iplt20.com/ifl/research/get_res_data_list.json?json')["players"]

def num_games_played(p):
    return len(fetch_data('https://fantasy.iplt20.com/ifl/research/get_player_stats.json?player_id='+ p + '&json')["player_stats"])

ref_player = [p for p in all_players if p["id"] == 1][0]
ref_num_of_games = num_games_played("1")
vfm_factor = ref_player["vfm"] * ref_player["price"] * ref_num_of_games / ref_player["fanta_points"]

player_info = {}

for i in range(len(all_players)):
    p = all_players[i]
    if p["vfm"] == None:
        p["point_avg"] = 0
    else:
        p["point_avg"] = p["vfm"] * p["price"] / vfm_factor

    p["team_id"] = teams[p["team_name"]]
    player_info[p["id"]] = p

with open('allocation') as f:
    data = f.readlines()
    for i in range(len(data)):
        player_name = data[i].strip()
        player = [p for p in all_players if p["firstname"] == player_name][0]
        fanta_team.append(player["id"])
        t = player["team_name"]
        ga[teams[t]].append(player)
        
with open('schedule') as f:
    data = f.readlines()
    for i in range(len(data)):
        mstr = data[i].split()
        m = [teams[mstr[0]], teams[mstr[1]]]
        s.append(m)


def top_players(players, n):
    return sorted(players, key=lambda(x): -1 * x["point_avg"])[:n]

def top_picks_for_team(t):
    players = [p for p in all_players if p["team_name"] == teams_list[t] and p["id"] not in fanta_team]
    return top_players(players, 5)

for i in range(9):
    top_picks[i] = top_picks_for_team(i)

#print [ [p["firstname"], p["point_avg"]] for p in top_players([ p for p in all_players if p["country_id"] == 2 ], 15) ]

#print [ [p["firstname"], p["point_avg"]] for p in top_players([ p for p in all_players if p["country_id"] == 1 and p["skill_id"] == 4 ], 15) ]

#print "top_players"
#print top_players(all_players, 11)

def accum(players):
    return reduce(lambda x,s: x + s["point_avg"], players, 0)

def accum_ids(players):
    return reduce(lambda x,s: x + player_info[s]["point_avg"], players, 0)

cache = {}

def make_key(a, k):
    return ".".join(str(x) for x in a) + str(k)

def is_valid(t):
    team = [[] for i in range(len(t))]
    for i in range(len(t)):
        team[i] = player_info[t[i]]

    batsmen = len([p for p in team if p["skill_id"] == 4])
    all_rounders = len([p for p in team if p["skill_id"] == 2])
    keepers = len( [p for p in team if p["skill_id"] == 1])
    bowlers = len([p for p in team if p["skill_id"] == 3])
    overseas = len([p for p in team if p["country_id"] == 2])

    return batsmen > 3 and batsmen < 6 and all_rounders > 0 and all_rounders < 5 and keepers == 1 and bowlers > 1 and bowlers < 6 and overseas < 5

def base_potential(t, s, k):
    return accum_ids( [p for p in t if player_info[p]["team_id"] in [s[k][0], s[k][1]]] )

def potential(t, k):
    if (make_key(t, k) in cache):
        return cache[make_key(t, k)]

    sub_out = "SKIP"
    sub_in = "SKIP"
    
    if (k == len(s)):
        return 0, sub_out, sub_in

    max_potential = base_potential(t, s, k) + potential(t, k+1)[0]

    hopefuls = top_picks[s[k][0]] 

    for i in range(len(t)):
        for j in range(len(hopefuls)):
            t1 = list(t)
            t1[i] = hopefuls[j]["id"]
            if is_valid(t1):
                p1 = base_potential(t1, s, k) + potential(sorted(t1), k+1)[0]

                if p1 > max_potential:
                    max_potential = p1
                    sub_out = player_info[t[i]]["firstname"]
                    sub_in = hopefuls[j]["firstname"]
                
                break

    hopefuls = top_picks[s[k][1]] 
    
    for i in range(len(t)):
        for j in range(len(hopefuls)):
            t1 = list(t)
            t1[i] = hopefuls[j]["id"]
            if is_valid(t1):
                p1 = base_potential(t1, s, k) + potential(sorted(t1), k+1)[0]

                if p1 > max_potential:
                    max_potential = p1
                    sub_out = player_info[t[i]]["firstname"]
                    sub_in = hopefuls[j]["firstname"]
                
                break



    cache[make_key(t, k)] = max_potential, sub_out, sub_in

    return max_potential, sub_out, sub_in

#print potential(sorted(fanta_team), 0)
#print base_potential(sorted(fanta_team), s, 0)
#print base_potential(sorted(fanta_team), s, 1)
#for t in s[0]:
#    print teams_list[t]
#    print [ [p["firstname"], p["point_avg"]] for p in top_picks_for_team(t) ]

