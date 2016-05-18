music-nerds
===========
* Fill `src/config.json`
```
cp src/config.json.template src/config.json
```

* Run the following commands to generate the music data
```
cd src/
./dump_room_history.py
./filter_music_messages.py
./get_spotify_albums_data.py
./get_spotify_tracks_data.py
./get_youtube_videos_data.py 
./gen_models.py
./gen_html.py
```
