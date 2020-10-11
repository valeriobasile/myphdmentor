#!/usr/bin/env python

import pandas as pd
import sys
import numpy as np
import json
from scipy.spatial.distance import cosine

df = pd.read_csv(sys.argv[1])

def onehot(valuestring, values):
    vector = [0 for value in values]
    for item in valuestring.split(', '):
        vector[values.index(item)] = 1
    return vector

def scalar(valuestring, values):
    return values.index(valuestring)

def similarity(mentor, mentee, weightvector):
    return 1 - cosine(mentor['features'], mentee['features'], weightvector)

people = {'mentor':[], 'mentee':[]}

for row in df.itertuples():
    email = row[2]
    level = scalar(row[5], [
        'A master student',
        'A PhD Student', 
        'A PhD graduate'])
    participation = row[21]
    role = row[22] 
    availability_time = scalar(row[23], [
        '1 to 3 hours', 
        '3 to 5 hours', 
        'more than 5 hours'])
    availability_medium = onehot(row[24], [
        'Through phone calls',
        'Through face to face meetings',
        'Through social media',
        'Through video calls',
        'Through emails'])

    interests = [int(row[column][0]) for column in range(25, 38)]

    features = [availability_time]
    features.extend(availability_medium)
    features.extend(interests)
    features = np.array(features)
    features = features/np.linalg.norm(features)
    
    person = {'email':email, 'level':level, 'features': features}

    if participation == 'No':
        continue

    if role in ['Mentor', 'Both mentee and mentor']:
        people['mentor'].append(person)
    if role in ['Mentee', 'Both mentee and mentor']:
        people['mentee'].append(person)

# read the weights from config file
with open("weights.json") as f:
    weights = json.load(f)
print (weights)
weightlist = [weights['availability_time']]
weightlist.extend([weights['availability_medium'] for i in range (5)])
weightlist.extend(weights['questions'])

weightvector = np.array(weightlist)

for mentor in people['mentor']:
    for mentee in people['mentee']:
        if mentee['level'] < mentor['level']:
            print ("{0:.4f}".format(similarity(mentor, mentee, weightvector)), mentor['email'], mentee['email'])

