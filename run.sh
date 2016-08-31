#!/bin/bash
# Fail on any error
set -e

# Create directories
mkdir -p data/{filtered,models,raw,spotify_albums,spotify_tracks,youtube_videos}

cd src/
./dump_room_history.py
./filter_music_messages.py
./get_spotify_albums_data.py
./get_spotify_tracks_data.py
./get_youtube_videos_data.py 
./gen_models.py
./gen_html.py
cd -
