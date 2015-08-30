#!/usr/bin/env python

#curl 'https://www.googleapis.com/youtube/v3/videos?key=AIzaSyAQ1Z8XFIF4GP5Yph6ohaqHZJ6NOzFNpvk&part=snippet&id=2Ox1Tore9nw&maxResults=1'

import simplejson
import logging
import re
import requests
import itertools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("get_youtube_videos_data")

youtube_regex = re.compile(r"https?://(www\.)?youtube\.com/watch\?v=([^&#?]+).*")
youtube_short_regex = re.compile(r"https?://(www\.)?youtu\.be/([^?#&]+).*")


def get_youtube_data(video_id):
    url = "https://www.googleapis.com/youtube/v3/videos"
    api_key = "YOUR_YOUTUBE_V3_API_KEY"
    params = {"key": api_key, "part": "snippet", "id": video_id, "maxResults": 1}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        raise Exception("Status code is not 200, status_code = %d", r.status_code)
    return r.json()


msgs = []
count = 0
ip_file = "../data/filtered/music_messages.json"
op_file = "../data/youtube_videos/youtube_videos.json"
videos = []

with open(ip_file, "r") as ip:
    jsonData = simplejson.load(ip)
    for item in jsonData:
        link = item["link"]
        youtube_matches = re.search(youtube_regex, link)
        youtube_short_matches = re.search(youtube_short_regex, link)
        if youtube_matches is None and youtube_short_matches is None:
            continue

        if youtube_matches is not None:
            video_id = youtube_matches.group(2)
        else:
            video_id = youtube_short_matches.group(2)

        videos.append(video_id)

videos_data = []
count = 1
for video_id in videos:
    logger.info("Triggered Youtube API request for video_id = %s, count = %d", video_id, count)
    data = get_youtube_data(video_id)
    if "items" in data:
        videos_data.append(data["items"])
    count += 1

videos_data = list(itertools.chain.from_iterable(videos_data))
with open(op_file, "w") as op:
    simplejson.dump(videos_data, op, indent=4, sort_keys=True)
    logger.info("Wrote youtube videos data to file = %s", op_file)
