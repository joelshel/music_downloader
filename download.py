#!/usr/bin/env python3

import json
from multiprocessing import Pool
import re
import requests as r
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth as SOA


def get_spotify_data(username, playlist_name):
    with open("credentials.json", "r") as f:
        credent = json.load(f)
    
    scope = 'playlist-read-private'
    client_id = credent['client_id']
    client_secret = credent['client_secret']
    redirect_uri = credent['redirect_uri']

    credentials = SOA(client_id, client_secret, redirect_uri, scope=scope)
    results = sp.Spotify(client_credentials_manager=credentials)
    playlists = results.user_playlists(username)
    
    playlist_dict = {}
    
    while playlists:
        for playlist in playlists['items']:
            playlist_dict[playlist['name']] = playlist['id']
        if playlists['next']:
            playlists = results.next(playlists)
        else:
            break

    try:
        playlist_id = playlist_dict[playlist_name]
    except KeyError:
        return "Playlist name not found in your playlists"

    musics = results.playlist(playlist_id)
    music_dict = {}

    while musics:
        try:
            lst = musics['tracks']['items']
            next = musics['tracks']
        except KeyError:
            lst = musics['items']
            next = musics
        
        for i, music in enumerate(lst):
            name = music['track']['name']
            artists=[]
            for artist in music['track']['artists']:
                artists.append(artist['name'])
            music_dict[i + next['offset']] = name, artists
        
        if next['next']:
            musics = results.next(next)
        else:
            break
    
    return music_dict


def get_data_youtube(music_data):
    yt_search_url="https://www.youtube.com/results?"
    i = music_data[0]
    music = music_data[1][0]
    artists = music_data[1][1]
    
    search_term = music + " " + " ".join(artists)
    params= {"search_query": search_term}
    result = r.get(yt_search_url, params)
    
    # regex to match /watch?v= and any 11 caracters after that
    path = re.search("/watch\?v=.{11}", result.text).group()
    return path


def download(username, playlist):
    spotify_data = get_spotify_data(username, playlist)
    pool = Pool(50)
    paths = list(pool.map(get_data_youtube, spotify_data.items()))


if __name__ == '__main__':
    download("your", "Minha playlist")
