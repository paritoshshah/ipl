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

blacklist = ["Manpreet Gony", "Dhawal Kulkarni", "Harmeet Singh Bansal",
"Venugopal Rao", "Anand Rajan"]

def fetch_data(url):
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    headers = { 'Cookie': 'session_id_ifl="890:fd25193b-c841-409c-933f-53385da34231"' }
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
        p["weight"] = 0
    else:
        p["point_avg"] = p["vfm"] * p["price"] / vfm_factor
        p["weight"] = float(str(p["point_avg"]) + "." + str(p["id"]))

    p["team_id"] = teams[p["team_name"]]
    player_info[p["id"]] = p

with open('allocation') as f:
    data = f.readlines()
    for i in range(len(data)):
        player_name = data[i].strip()
        player = [p for p in all_players if p["firstname"] == player_name][0]
        fanta_team.append(player["id"])
        print player["firstname"], player["point_avg"]
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
    players = [p for p in all_players if p["team_name"] == teams_list[t] and
            p["id"] not in fanta_team and p["firstname"] not in blacklist]
    return top_players(players, 5)

for i in range(9):
    top_picks[i] = top_picks_for_team(i)


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
    cost = sum([ p["price"] for p in team ])

    return batsmen > 3 and batsmen < 6 and all_rounders > 0 and all_rounders < 5 and keepers == 1 and bowlers > 1 and bowlers < 6 and overseas < 5 and cost < 10000001

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

# given a team t, and a bench b, return the next worse (t', b')
def next_worse_pick(t, bench, err):
    i = 0
    j = 0

    min_delta = 1000
    sub_out = 0
    sub_in = 0


    b = list(bench)
    if err == "TOO_FEW_BATSMEN":
        b = [p for p in bench if p["skill_id"] == 4]
    elif err == "NO_ALL_ROUNDERS":
        b = [p for p in bench if p["skill_id"] == 2]
    elif err == "NEED_A_KEEPER":
        b = [p for p in bench if p["skill_id"] == 1]
    elif err == "NOT_ENOUGH_BOWLERS":
        b = [p for p in bench if p["skill_id"] == 3]
    elif err == "NO_UNCAPPED":
        b = [p for p in bench if p["capped"] == 0]
    elif err == "NO_ALL_ROUNDERS":
        b = [p for p in bench if p["skill_id"] == 2]

    batsmen = len([p for p in t if p["skill_id"] == 4])
    all_rounders = len([p for p in t if p["skill_id"] == 2])
    keepers = len( [p for p in t if p["skill_id"] == 1])
    bowlers = len([p for p in t if p["skill_id"] == 3])
    overseas = len([p for p in t if p["country_id"] == 2])
    uncapped = len([p for p in t if p["capped"] == 0])
 
    for i in range(len(t)):
        for j in range(len(b)):
            delta = t[i]["weight"] - b[j]["weight"]

            making_things_worse = False
            
            if err == "TOO_FEW_BATSMEN":
                making_things_worse = (t[i]["skill_id"] == 4)
            elif err == "TOO_MANY_BATSMEN":
                making_things_worse = (t[i]["skill_id"] != 4)
            elif err == "TOO_MANY_ALL_ROUNDERS":
                making_things_worse = (t[i]["skill_id"] != 2)
            elif err == "TOO_MANY_KEEPERS":
                making_things_worse = (t[i]["skill_id"] != 1)
            elif err == "NOT_ENOUGH_BOWLERS":
                making_things_worse = (t[i]["skill_id"] == 3)
            elif err == "TOO_MANY_BOWLERS":
                making_things_worse = (t[i]["skill_id"] != 3)
            elif err == "TOO_MANY_OVERSEAS":
                making_things_worse = (t[i]["country_id"] != 2)
 
            if not making_things_worse and delta > 0 and delta < min_delta:
                min_delta = delta
                sub_out = i
                sub_in = j

    player_out = t[sub_out]
    player_in = b[sub_in]

    i = 0
    del t[sub_out]
    while i < len(t) and t[i]["weight"] > player_in["weight"]:
        i = i + 1
    t.insert(i, player_in)


    for i in range(len(bench)):
        if bench[i]["id"] == player_in["id"]:
            break

    del bench[i]

    i = 0
    while i < len(bench) and bench[i]["weight"] > player_out["weight"]:
        i = i + 1
    bench.insert(i, player_out)

    return t, bench

def check_for_errors(team, teams_playing):
    batsmen = len([p for p in team if p["skill_id"] == 4])
    all_rounders = len([p for p in team if p["skill_id"] == 2])
    keepers = len( [p for p in team if p["skill_id"] == 1])
    bowlers = len([p for p in team if p["skill_id"] == 3])
    overseas = len([p for p in team if p["country_id"] == 2])
    uncapped = len([p for p in team if p["capped"] == 0])
    players_from_each_team = [len([p for p in team if p["team_name"] ==
            teams_list[t]]) for t in teams_playing]
    cost = sum([ p["price"] for p in team ])
    
    if batsmen < 4:
        return "TOO_FEW_BATSMEN"
    elif batsmen > 5:
        return "TOO_MANY_BATSMEN"
    elif all_rounders == 0:
        return "NO_ALL_ROUNDERS"
    elif all_rounders > 4:
        return "TOO_MANY_ALL_ROUNDERS"
    elif keepers == 0:
        return "NEED_A_KEEPER"
    elif keepers > 1:
        return "TOO_MANY_KEEPERS"
    elif bowlers < 2:
        return "NOT_ENOUGH_BOWLERS"
    elif bowlers > 5:
        return "TOO_MANY_BOWLERS"
    elif uncapped == 0:
        return "NO_UNCAPPED"
    elif max(players_from_each_team) > 6:
        return "TOO_MANY_FROM_ONE_TEAM"
    elif cost > 10000000:
        return "TOO_COSTLY"
    elif overseas > 4:
        return "TOO_MANY_OVERSEAS"

    return None


import time

def daily_challenge(teams_playing):
    pool = [p for p in all_players if teams[p["team_name"]] in teams_playing and p["point_avg"] > 0 and p["firstname"] not in blacklist]
    pool = sorted(pool, key=lambda(x): -1 * x["weight"])

    t = pool[:11]

    print [[p["firstname"], p["point_avg"]] for p in t]

    b = pool[11:]

    err = check_for_errors(t, teams_playing)

    while err != None:
        t, b = next_worse_pick(t, b, err)
        err = check_for_errors(t, teams_playing)
        print sum([ p["point_avg"] for p in t]), err

    return t


#print [[p["firstname"], p["point_avg"]] for p in daily_challenge(s[0])]
print potential(sorted(fanta_team), 0)
#print base_potential(sorted(fanta_team), s, 0)
for t in s[0]:
    print teams_list[t]
    print [ [p["firstname"], p["point_avg"]] for p in top_picks_for_team(t) ]

#print [ [p["firstname"], p["point_avg"]] for p in top_players([ p for p in all_players if p["country_id"] == 2 ], 15) ]

#print [ [p["firstname"], p["point_avg"]] for p in top_players([ p for p in all_players if p["country_id"] == 1 ], 10) ]
