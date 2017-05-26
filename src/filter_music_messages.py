#!/usr/bin/env python

import glob
import simplejson
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("filter_music_messages")

op_file = "../data/filtered/music_messages.json"
spotify_regex = re.compile(r".*\b(https?:\/\/open\.spotify\.com[^\s\n,.]+)\b.*")
youtube_regex = re.compile(r".*\b(https?:\/\/(www\.)?(youtube\.com|youtu\.be)[^\s,.\n]+)\b.*")

msgs = []
count = 0
for ip_file in glob.glob("../data/raw/room_history*.json"):
    with open(ip_file, "r") as ip:
        jsonData = simplejson.load(ip)
        for item in jsonData["items"]:
            m = item["message"]
            spotify_matches = re.search(spotify_regex, m)
            youtube_matches = re.search(youtube_regex, m)
            if spotify_matches is None and youtube_matches is None:
                continue
            if spotify_matches is not None:
                music_link = spotify_matches.group(1)
            else:
                music_link = youtube_matches.group(1)
            d = item["date"]
            if "from" in item and "name" in item["from"]:
                from_user = item["from"]["name"]
            else:
                from_user = "Unknown User"
            msgs.append({"date": d, "from": from_user, "link": music_link})
            count += 1

with open(op_file, "w") as op:
    simplejson.dump(msgs, op, indent=4, sort_keys=True)
    logger.info("Wrote %d music messages to file = %s", count, op_file)
