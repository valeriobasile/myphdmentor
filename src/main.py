#!/usr/bin/env python
import sys
sys.path.append('matching')

import argparse
import logging

from matching import run

# logging setup
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - [ %(message)s ]",
        datefmt="%d-%b-%y %H:%M:%S",
        force=True,
        handlers=[
            logging.FileHandler("log/debug.log"),
            logging.StreamHandler()
            ])

def createParser():
    # args
    parser = argparse.ArgumentParser(
            prog = "Mentor & Mentee Matching Algorithm",
            description = "...",
            epilog = "..."
            )
    parser.add_argument("instance")
    parser.add_argument("--output", help="Output matching file", type=str, default="output/matching.csv")
    parser.add_argument("--weights", help="Weight config file", type=str, default="config/weights.json")

    return parser

if __name__ == "__main__": 

    logging.debug("> Creating parser")
    parser = createParser()

    logging.debug("> Retrieving arguments")
    args = parser.parse_args()

    # run
    logging.debug("> Running matching algorithm")
    run(args)
