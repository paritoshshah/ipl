# match up names in *_oc.csv and canonical_names

import os
import csv

pwd = os.path.dirname(os.path.realpath(__file__))

with open('canonical_names') as f:
    canonical_names = f.read().splitlines()
    
def match_names(oc_names):
    for oc_name in oc_names:
        if oc_name not in canonical_names:
            print oc_name


for (dirpath, dirnames, filenames) in os.walk(pwd):
    for f in filenames:
        if f.endswith('_oc.csv'):
            with open(f) as oc_csv:
                oc_csv_data = csv.reader(oc_csv)
                oc_names = [row[0] for row in oc_csv_data]
                match_names(oc_names)


