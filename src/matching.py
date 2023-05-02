#!/usr/bin/env python
import sys

import pandas as pd
import numpy as np

from scipy.spatial.distance import cosine
from scipy.optimize import linear_sum_assignment
from itertools import product
from random import random

import json
import logging

FIELDS = [
        "Physical Sciences and Engineering (Physics, Mathematics, Chemistry etc)",
        "Life Sciences (Biochemistry, Biology, Pharmaceutical Sciences, Medicine etc)",
        "Social Sciences (Law, Economics, Psychology etc)",
        "Humanities (Literature, History, Philosophy etc)",
        "Design and architecture"
        ]

PAIRS = [
        ("A master student", "A PhD Student"),
        ("A master student", "A PhD Student in the first year"),
        ("A master student", "A PhD Student in the second year"),
        ("A master student", "A PhD Student at least in the third year"),
        ("A master student", "A PhD graduate (Post-doc or working in the private sector)"),
        ("A PhD Student", "A PhD Student"),
        ("A PhD Student", "A PhD Student in the second year"),
        ("A PhD Student", "A PhD Student at least in the third year"),
        ("A PhD Student", "A PhD graduate (Post-doc or working in the private sector)"),
        ("A PhD Student in the first year", "A PhD Student"),
        ("A PhD Student in the first year", "A PhD Student at least in the third year"),
        ("A PhD Student in the first year", "A PhD graduate (Post-doc or working in the private sector)"),
        ("A PhD Student in the first year", "A PhD graduate (Post-doc or working in the private sector) (Post-doc or working in the private sector)"),
        ("A PhD Student in the first year", "A PhD graduate (Post-doc or working in the private sector), with less than three years of expertise"),
        ("A PhD Student in the first year", "A PhD graduate (Post-doc or working in the private sector), with 3+ years of expertise"),
        ("A PhD Student in the second year", "A PhD graduate (Post-doc or working in the private sector)"),
        ("A PhD Student in the second year", "A PhD graduate (Post-doc or working in the private sector) (Post-doc or working in the private sector)"),
        ("A PhD Student in the second year", "A PhD graduate (Post-doc or working in the private sector), with less than three years of expertise"),
        ("A PhD Student in the second year", "A PhD graduate (Post-doc or working in the private sector), with 3+ years of expertise"),
        ("A PhD Student at least in the third year", "A PhD graduate (Post-doc or working in the private sector)"),
        ("A PhD Student at least in the third year", "A PhD graduate (Post-doc or working in the private sector) (Post-doc or working in the private sector)"),
        ("A PhD Student at least in the third year", "A PhD graduate (Post-doc or working in the private sector), with less than three years of expertise"),
        ("A PhD Student at least in the third year", "A PhD graduate (Post-doc or working in the private sector), with 3+ years of expertise"),
        ]

def onehot(valuestring, values):
    """
    A function to translate multiple-value items into one-hot encoded vectors.
    """
    vector = [0] * len(values)

    for item in valuestring.split(", "):
        vector[values.index(item)] = 1

    return vector

def scalar(valuestring, values):
    """
    Convenience function for factor to integer translation.
    """
    return values.index(valuestring)

def similarity(mentor, mentee, weightvector):
    """
    Scipy has implemented weighted cosine distance, so we use that.
    """
    if mentor["email"] == mentee["email"]:
        return -1.0

    if not (mentee["level"], mentor["level"]) in PAIRS:
        return -1.0

    return 1 - cosine(mentor["features"], mentee["features"], weightvector)


def readWeightVector(args):
    # read the weights from config file and transform them into a numeric vector
    with open(args.weights) as f:
        weights = json.load(f)

    weightlist = [weights["availability_time"]]
    weightlist.extend([weights["availability_medium"] for i in range (5)])
    weightlist.extend(weights["questions"])

    return np.array(weightlist)


def run(args):

    # read dataset
    logging.debug(">> Reading instance file")
    df = pd.read_csv(args.instance)

    #This dict will contain the people that replied to the survey, divided by
    #role. People who make themselves available for both roles end up in both lists.
    people = {
            "mentor": [], 
            "mentee": []
            }

    # parse the lines one by one
    logging.debug(">> Reading CSV lines")
    for row in df.itertuples():

        logging.debug(">>> Parsing %s" % ", ".join(map(str, row)))

        # params
        status = row.AssignmentStatus
        email  = row[2].strip()
        name   = row[26].strip() + " " + row[28].strip()
        level  = row[27]
        field  = row[7]
        role   = row[10] 

        availability_time = scalar(
                row[11], 
                [
                    "1 to 3 hours", 
                    "3 to 5 hours", 
                    "more than 5 hours"
                    ]
                )

        availability_medium = onehot(
                row[12], 
                [
                    "Through phone calls",
                    "Through face to face meetings",
                    "Through social media",
                    "Through video calls",
                    "Through emails"
                    ]
                )

        # "interests" are the answers to the final questions used for the matching
        try:
            interests = list(map(lambda column: int(row[column][0]), range(13, 22))) + [FIELDS.index(field)]
        except:
            interests = list(map(lambda column: int(row[column][0]), range(13, 22))) + [len(FIELDS)]

        # interests are transformed into a *normalized* vector of features to 
        # compute cosine similarity
        features = [availability_time]
        features.extend(availability_medium)
        features.extend(interests)

        features = np.array(features)

        # normalization
        features = features/np.linalg.norm(features)
        person   = {
                "name":     name, 
                "email":    email, 
                "level":    level, 
                "features": features
                }

        if role in ["Mentee (only master students and PhDs)", "Mentor and Mentee (Only for PhDs)"] and \
                not status in [0, 1]:
                    people["mentee"].append(person)

        if role in ["Mentor (only PhDs and PhD graduates)", "Mentor and Mentee (Only for PhDs)"] and \
                not status in [0, 2]:
                    people["mentor"].append(person)

    # read weightvector
    weightvector = readWeightVector(args)

    # creating the matrix
    M = np.zeros((len(people["mentee"]), len(people["mentor"])))

    for (e, mentee), (o, mentor) in product(enumerate(people["mentee"]), enumerate(people["mentor"])):
        M[e][o] = similarity(mentor, mentee, weightvector)

    # matching time
    row_ind, col_ind = linear_sum_assignment(M, maximize=True)

    # write CSV
    matching = {
            "mentee":       [],
            "mentee email": [],
            "mentor":       [],
            "mentor email": []
            }

    for e, o in zip(row_ind, col_ind):
        if M[e][o] > -1:
            #print (e, len(people["mentor"]))
            matching["mentee"].append(people["mentee"][e]["name"])
            matching["mentee email"].append(people["mentee"][e]["email"])
            matching["mentor"].append(people["mentor"][o]["name"])
            matching["mentor email"].append(people["mentor"][o]["email"])

    logging.debug(">> Writing output")
    # output
    matching_df = pd.DataFrame(matching)
    matching_df.to_csv(args.output, index=False)
