# cricinfo typically lists players as first initial + lastname, whereas fantasy.iplt20 users firstname + lastname

with open('oc_names') as f:
    oc_names = f.read().splitlines()

with open('canonical_names') as f:
    canonical_names = f.read().splitlines()

# for each canonical name try to find a matching oc name
matched_names = []
unmatched_names = []
for canonical_name in canonical_names:
    lastname = canonical_name.split()[-1]
    potential_matches = []

    for oc_name in oc_names:
        oc_lastname = oc_name.split()[-1]
        if lastname == oc_lastname:
            potential_matches.append(oc_name)

    if len(potential_matches) == 0:
        unmatched_names.append(canonical_name)

    if len(potential_matches) == 1:
        matched_names.append([canonical_name, potential_matches[0]])
        oc_names.remove(potential_matches[0])
    
    if len(potential_matches) > 1:
        for potential_match in potential_matches:
            if potential_match[0] == canonical_name[0]:
                matched_names.append([canonical_name, potential_match])
                oc_names.remove(potential_match)

for matched_name in matched_names:
    print matched_name[0] + ", " + matched_name[1]

print unmatched_names
print oc_names
