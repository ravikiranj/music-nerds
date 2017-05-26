#!/usr/bin/env python

import simplejson
import logging
import re
import requests
import itertools
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("get_spotify_albums_data")

track_regex = re.compile(r"^https?://open.spotify.com/track/(.*)$")


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

def get_json_config():
    with open("config.json") as ip:
        return json.load(ip)

def get_spotify_data(tracks_list):
    url = "https://api.spotify.com/v1/tracks"
    params = {"ids": ','.join(tracks_list), "market": "US"}
    # Generate Access Token via https://developer.spotify.com/web-api/console/get-several-tracks
    config = get_json_config()
    auth_token = config["spotify_auth_token"]
    headers = {"Authorization": "Bearer " + auth_token}
    r = requests.get(url, params=params, headers=headers)
    if r.status_code != 200:
        raise Exception("Status code is not 200, status_code = %d", r.status_code)
    return r.json()


msgs = []
count = 0
ip_file = "../data/filtered/music_messages.json"
op_file = "../data/spotify_tracks/spotify_tracks.json"
tracks = []
max_tracks = 1

with open(ip_file, "r") as ip:
    jsonData = simplejson.load(ip)
    for item in jsonData:
        link = item["link"]
        track_matches = re.search(track_regex, link)
        if track_matches is None:
            continue
        track = track_matches.group(1)
        tracks.append(track)

tracks_data = []
track_chunks = chunks(tracks, max_tracks)
for track_chunk in track_chunks:
    logger.info("Triggered spotify query for track_chunk = %s", ','.join(track_chunk))
    try:
        jsonData = get_spotify_data(track_chunk)
        if "tracks" in jsonData:
            tracks_data.append(jsonData["tracks"])
        else:
            print "Unable to find tracks data in response for track_chunk = %s" % str(track_chunk)
    except:
        print "Encountered exception for track_chunk = %s" % str(track_chunk)

tracks_data = list(itertools.chain.from_iterable(tracks_data))
with open(op_file, "w") as op:
    simplejson.dump(tracks_data, op, indent=4, sort_keys=True)
    logger.info("Wrote spotify tracks data to file = %s", op_file)
