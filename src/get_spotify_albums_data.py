#!/usr/bin/env python

import simplejson
import logging
import re
import requests
import itertools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("get_spotify_albums_data")

album_regex = re.compile(r"^https?://open.spotify.com/album/(.*)$")


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def get_spotify_data(albums_list):
    url = "https://api.spotify.com/v1/albums"
    params = {"ids": ','.join(albums_list), "market": "US"}
    # Generate Access Token via https://developer.spotify.com/web-api/console/get-several-albums
    auth_token = "YOUR_SPOTIFY_AUTH_TOKEN"
    headers = {"Authorization": "Bearer " + auth_token}
    r = requests.get(url, params=params, headers=headers)
    if r.status_code != 200:
        raise Exception("Status code is not 200, status_code = %d", r.status_code)
    return r.json()


msgs = []
count = 0
ip_file = "../data/filtered/music_messages.json"
op_file = "../data/spotify_albums/spotify_albums.json"
albums = []
max_albums = 20

with open(ip_file, "r") as ip:
    jsonData = simplejson.load(ip)
    for item in jsonData:
        link = item["link"]
        album_matches = re.search(album_regex, link)
        if album_matches is None:
            continue
        album = album_matches.group(1)
        albums.append(album)

albums_data = []
album_chunks = chunks(albums, max_albums)
for album_chunk in album_chunks:
    logger.info("Triggered spotify query for album_chunk = %s", ','.join(album_chunk))
    jsonData = get_spotify_data(album_chunk)
    if "albums" in jsonData:
        albums_data.append(jsonData["albums"])
    else:
        raise Exception("Unable to find albums data in response, resp = ", jsonData)

albums_data = list(itertools.chain.from_iterable(albums_data))
with open(op_file, "w") as op:
    simplejson.dump(albums_data, op, indent=4, sort_keys=True)
    logger.info("Wrote spotify album data to file = %s", op_file)
