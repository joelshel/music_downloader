#!/usr/bin/env python3

import json
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth as SOA


def data_spotify(username, playlist_name):
    with open("credentials.json", "r") as f:
        credent = json.load(f)
    
    scope = 'playlist-read-private'
    client_id = credent['client_id']
    client_secret = credent['client_secret']
    redirect_uri = credent['redirect_uri']

    credentials = SOA(
        client_id, client_secret, redirect_uri, scope=scope, username=username
        )
    results = sp.Spotify(client_credentials_manager=credentials)
    playlists = results.current_user_playlists()
    
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


def download(username, playlist):
    data_spotify(username, playlist)

if __name__ == '__main__':
    download()