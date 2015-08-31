#!/usr/bin/env python

import simplejson
import logging
import re

from dateutil.parser import parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("get_models")

album_regex = re.compile(r"^https?://open.spotify.com/album/(.*)$")
track_regex = re.compile(r"^https?://open.spotify.com/track/(.*)$")
youtube_regex = re.compile(r"https?://(www\.)?youtube\.com/watch\?v=([^&#?]+).*")
youtube_short_regex = re.compile(r"https?://(www\.)?youtu\.be/([^?#&]+).*")


def get_music_id_and_type(link):
    album_regex_matches = re.search(album_regex, link)
    if album_regex_matches is not None:
        return {"id": album_regex_matches.group(1), "type": "spotify_album"}

    track_regex_matches = re.search(track_regex, link)
    if track_regex_matches is not None:
        return {"id": track_regex_matches.group(1), "type": "spotify_track"}

    youtube_regex_matches = re.search(youtube_regex, link)
    if youtube_regex_matches is not None:
        return {"id": youtube_regex_matches.group(2), "type": "youtube_video"}

    youtube_short_regex_matches = re.search(youtube_short_regex, link)
    if youtube_short_regex_matches is not None:
        return {"id": youtube_short_regex_matches.group(2), "type": "youtube_video"}

    return None


def get_music_msgs():
    ip_file = "../data/filtered/music_messages.json"
    msgs = []
    with open(ip_file, "r") as ip:
        json_data = simplejson.load(ip)
        for item in json_data:
            link = item["link"]
            music_id_type = get_music_id_and_type(link)
            if music_id_type is None:
                continue
            msg = item
            msg.update(music_id_type)
            msgs.append(msg)
    return msgs


def get_spotify_data(ip_file, type):
    # title, image, date, artists[], url, id
    music_items = {}
    with open(ip_file, "r") as ip:
        json_data = simplejson.load(ip)
        for item in json_data:
            id = item["id"]
            title = item["name"]

            if type == "albums":
                if "release_date" in item:
                    rel_date = item["release_date"]
                else:
                    rel_date = None
                if rel_date is not None and len(rel_date) >= 4:
                    date = rel_date[:4]
                else:
                    date = rel_date
            else:
                date = None

            url = item["external_urls"]["spotify"]
            artists = []
            for artist in item["artists"]:
                artists.append(artist["name"])
            image = None
            if type == "albums":
                images = item["images"]
            else:
                images = item["album"]["images"]
            if len(images) > 0:
                image = images[len(images)-1]["url"]
            music_item = {"id": id, "title": title, "display_date": date, "url": url, "artists": artists, "image": image}
            music_items[id] = music_item
    return music_items


def get_spotify_albums_data():
    ip_file = "../data/spotify_albums/spotify_albums.json"
    return get_spotify_data(ip_file, type="albums")


def get_spotify_tracks_data():
    ip_file = "../data/spotify_tracks/spotify_tracks.json"
    return get_spotify_data(ip_file, type="tracks")


def get_youtube_videos_data():
    # title, image, date, artists[], url, id
    ip_file = "../data/youtube_videos/youtube_videos.json"
    music_items = {}
    with open(ip_file, "r") as ip:
        json_data = simplejson.load(ip)
        for item in json_data:
            id = item["id"]
            snippet = item["snippet"]
            title = snippet["title"]
            image = snippet["thumbnails"]["default"]["url"]
            date_str = snippet["publishedAt"]
            date = parse(date_str).strftime("%b %d, %Y")
            url = "https://www.youtube.com/watch?v=" + id
            music_item = {"id": id, "title": title, "display_date": date, "url": url, "artists": None, "image": image}
            music_items[id] = music_item
    return music_items

music_msgs = get_music_msgs()
spotify_albums_data = get_spotify_albums_data()
spotify_tracks_data = get_spotify_tracks_data()
youtube_videos_data = get_youtube_videos_data()

music_data = []
missing_info_msg_count = 0
for msg in music_msgs:
    info = None
    music_type = msg["type"]
    id = msg["id"]
    music_data_item = msg
    if music_type == "spotify_album" and id in spotify_albums_data:
        info = spotify_albums_data[id]
    elif music_type == "spotify_track" and id in spotify_tracks_data:
        info = spotify_tracks_data[id]
    elif music_type == "youtube_video" and id in youtube_videos_data:
        info = youtube_videos_data[id]
    else:
        logger.error("Couldn't find suitable info for %s", str(msg))
        missing_info_msg_count += 1
        continue

    if info is not None:
        music_data_item.update(info)

        # Patch msg date
        msg_date = music_data_item["date"]
        del music_data_item["date"]
        music_data_item["msg_date"] = msg_date

        music_data.append(music_data_item)
    else:
        logger.error("Couldn't find suitable info for %s", str(msg))
        missing_info_msg_count += 1
        continue

logger.info("Couldn't find info for %d music items", missing_info_msg_count)

op_file = "../data/models/music_data.json"
with open(op_file, "w") as op:
    simplejson.dump(music_data, op, indent=4, sort_keys=True)
    logger.info("Wrote music data to file = %s", op_file)
