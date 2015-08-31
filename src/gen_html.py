#!/usr/bin/env python

import simplejson
import logging

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader("src", "../static/templates"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("get_models")


def get_models():
    ip_file = "../data/models/music_data.json"
    spotify_albums = []
    spotify_tracks = []
    youtube_videos = []
    with open(ip_file, "r") as ip:
        json_data = simplejson.load(ip)
        for item in json_data:
            if item["type"] == "spotify_album":
                spotify_albums.append(item)
            elif item["type"] == "spotify_track":
                spotify_tracks.append(item)
            elif item["type"] == "youtube_video":
                youtube_videos.append(item)
    return {"spotify_albums": spotify_albums, "spotify_tracks": spotify_tracks, "youtube_videos": youtube_videos}

models = get_models()
template = env.get_template("index.html")
json_data = {"spotify_albums": models["spotify_albums"], "spotify_tracks": models["spotify_tracks"], "youtube_videos": models["youtube_videos"]}
html = template.render(json_data)

op_file = "../static/index.html"
with open(op_file, "w") as op:
    op.write(html.encode('utf-8'))
    logger.info("Wrote generated html to %s", op_file)
