#!/usr/bin/env python

import pandas as pd
import sys
import numpy as np
import json
from scipy.spatial.distance import cosine

def onehot(valuestring, values):
    '''
    A function to translate multiple-value items into one-hot encoded vectors.
    '''
    vector = [0 for value in values]
    for item in valuestring.split(', '):
        vector[values.index(item)] = 1
    return vector

def scalar(valuestring, values):
    '''
    Convenience function for factor to integer translation.
    '''
    return values.index(valuestring)

def similarity(mentor, mentee, weightvector):
    '''
    Scipy has implemented weighted cosine distance, so we use that.
    '''
    return 1 - cosine(mentor['features'], mentee['features'], weightvector)

'''
This dict will contain the people that replied to the survey, divided by
role. People who make themselves available for both roles end up in both lists.
'''
people = {'mentor':[], 'mentee':[]}

'''
command syntax:
./parse.py CSV_DOWNLOADED_FROM_GOOGLE_DOCS
'''
df = pd.read_csv(sys.argv[1])

# parse the lines one by one
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

    # "interests" are the answers to the final questions used for the matching
    interests = [int(row[column][0]) for column in range(25, 38)]

    '''
    interests are transformed into a *normalized* vector of features to 
    compute cosine similarity
    '''
    features = [availability_time]
    features.extend(availability_medium)
    features.extend(interests)
    features = np.array(features)
    features = features/np.linalg.norm(features)
    
    person = {'email':email, 'level':level, 'features': features}

    # we only want people who want to participate
    if participation == 'No':
        continue

    # 
    if role in ['Mentor', 'Both mentee and mentor']:
        people['mentor'].append(person)
    if role in ['Mentee', 'Both mentee and mentor']:
        people['mentee'].append(person)

# read the weights from config file and transform them into a numeric vector
with open("weights.json") as f:
    weights = json.load(f)
weightlist = [weights['availability_time']]
weightlist.extend([weights['availability_medium'] for i in range (5)])
weightlist.extend(weights['questions'])
weightvector = np.array(weightlist)

'''
just for debug at the moment:
print a list of pairs with their similarity scores.
'''
for mentor in people['mentor']:
    for mentee in people['mentee']:
        # CHECK: is this constraint correct/too strict?
        if mentee['level'] < mentor['level']:
            print (
                "{0:.4f}".format(similarity(mentor, mentee, weightvector)), 
                mentor['email'], 
                mentee['email'])

