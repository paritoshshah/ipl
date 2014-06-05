import sys

teams_list = ['CSK','DD','KKR','KXIP','MI','RCB','RR','SRH']

with open('schedule') as f:
    data = f.readlines()
    deltas = []
    for i in range(len(teams_list)):
        team = teams_list[i]
        team_matches = []
        for j in range(len(data)):
            if team in data[j].split():
                team_matches.append(j)

        team_deltas = []
        team_deltas.append(team_matches[0])
        for k in range(1, len(team_matches)):
            team_deltas.append(team_matches[k] - team_matches[k-1])

        deltas.append(team_deltas)
    
    for l in range(len(deltas)):
        for n in range(len(deltas[l])):
            print deltas[l][n]

        print teams_list[l]

