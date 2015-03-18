#Knapsack problem: Given a roster of n players, with cost Ci, point average Pi, construct a team of 11 staying under budget B, with maximum total point average.

# M[i][C][k] = best team of size k, given budget C, and roster limited to first i players

import csv

best_team_cache = {}
players = []

with open('2015_prices_2014_point_averages.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        players += [row]

# normalize player costs, point averages
for i in range(len(players)):
    players[i][1] = int(players[i][1]) / 50000
    players[i][2] = int(players[i][2])

def best_team(i, B, k):
    if (i, B, k) in best_team_cache:
        return best_team_cache[i, B, k]
    
    if k <= 0:
        return [0]

    if (B <= 0 or i == 0) and k > 0:
        return [-1000]

    if players[i][1] > B:
        result = best_team(i-1, B, k)
    else:
        i_not_in_best = best_team(i-1, B, k)
        i_in_best = list(best_team(i-1, B-players[i][1], k-1))
        i_in_best[0] += players[i][2]
        i_in_best += [i]
        
        if i_in_best[0] > i_not_in_best[0]:
            result = i_in_best
        else:
            result = i_not_in_best

    best_team_cache[i, B, k] = result
    return result

team = best_team(len(players)-1, 200, 11)
for i in range(1, len(team)):
    print players[i]
