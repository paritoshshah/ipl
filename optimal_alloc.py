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

for i in range(len(all_players)):
    p = all_players[i]
    if p["vfm"] == None:
        p["point_avg"] = 0
    else:
        p["point_avg"] = p["vfm"] * p["price"] / vfm_factor

with open('allocation') as f:
    data = f.readlines()
    for i in range(len(data)):
        player_id = int(data[i].strip())
        fanta_team.append(player_id)
        player = [p for p in all_players if p["id"] == player_id][0]
        t = player["team_name"]
        ga[teams[t]].append(player)
        
    print ga

with open('schedule') as f:
    data = f.readlines()
    for i in range(len(data)):
        mstr = data[i].split()
        m = [teams[mstr[0]], teams[mstr[1]]]
        s.append(m)

cache = {}

def make_key(a, k):
    return "".join(str(x) for x in a) + str(k)

def top_picks_for_team(t):
    players = [p for p in all_players if p["team_name"] == teams_list[t]]
    return top_players(players, 5)

def top_indian_batsmen():
    players = [p for p in all_players if p["country_id"] == 1 and p["skill_id"] == 4]
    return top_players(players, 4)

def top_players(players, n):
    temp = sorted(players, key=lambda(x): -1 * x["point_avg"])[:n]
    return map(lambda p: [p["firstname"], p["point_avg"]], temp)

print "top_indian_batsmen"
print top_indian_batsmen()

print "top_players"
print top_players(all_players, 11)

for i in range(len(teams_list)):
    print teams_list[i]
    print top_picks_for_team(i)


def potential(a, k):

    if (make_key(a, k) in cache):
        return cache[make_key(a, k)]

    if (k == len(s)-1):
        return a[s[k][0]] + a[s[k][1]], -1, -1

    max_potential = a[s[k][0]] + a[s[k][1]] + potential(a, k+1)[0]
    sub_from = [s[k][0]]
    sub_to = [s[k][0]]

    for i in range(len(a)):
        if i != s[k][0] and i != s[k][1] and a[i] != 0:
            a0 = list(a)
            a0[s[k][0]] = a0[s[k][0]] + 1
            a0[i] = a0[i] - 1
            p0 = a0[s[k][0]] + a0[s[k][1]] + potential(a0, k+1)[0]

            a1 = list(a)
            a1[s[k][1]] = a1[s[k][1]] + 1
            a1[i] = a1[i] - 1
            p1 = a1[s[k][0]] + a1[s[k][1]] + potential(a1, k+1)[0]

            if p0 > p1:
                p = p0
                to_idx = s[k][0]
            else:
                p = p1
                to_idx = s[k][1]

            if p == max_potential:
                sub_from.append(i)
                sub_to.append(to_idx)
                if p0 == p1:
                    sub_from.append(i)
                    sub_to.append(s[k][0])

            if p > max_potential:
                max_potential = p
                sub_from = [i]
                sub_to = [to_idx]

                if p0 == p1:
                    sub_from.append(i)
                    sub_to.append(s[k][0])

    cache[make_key(a, k)] = max_potential, sub_from, sub_to

    return max_potential, [teams_list[x] for x in sub_from], [teams_list[y] for y in sub_to]

#print potential(ga, 0)
