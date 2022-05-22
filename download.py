#!/usr/bin/env python3

from functools import partial
import http
import json
from multiprocessing import Pool
from os.path import isdir, expanduser, join
from os import listdir, mkdir
import re
import requests as r
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth as SOA
import youtube_dl


COOKIES = "cookies.txt"


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
            for artist in music['track']['artists'][:2]:
                artists.append(artist['name'])
            music_dict[i + next['offset']] = name, artists
        
        if next['next']:
            musics = results.next(next)
        else:
            break
    
    return music_dict


def get_music_path(music_data):
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


def download_music(path, playlist, destination="~/Music/", count=0):
    yt_url="https://www.youtube.com"
    
    ydl_opts = {
        'cookiefile': COOKIES,
        'format': 'bestaudio/best',
        'outtmpl': f'{destination}%(title)s.%(ext)s',
        'download_archive': f'downloaded_songs_{playlist}.txt',
        'cachedir': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_url + path])
    except (youtube_dl.utils.DownloadError, http.cookiejar.LoadError):
        if count >= 3:
            return
        download_music(path, playlist, destination, count+1)


def create_m3u(playlist_path):
    music_names = listdir(playlist_path)
    
    playlist_path = playlist_path.split("/")
    path, playlist = "/".join(playlist_path[:-2]), playlist_path[-2]
    
    music_names = [f"./{playlist}/{music_name}\n" for music_name in music_names]
    
    with open(path + "/" + playlist + ".m3u", "w") as m3u:
        m3u.writelines(music_names)


def download(username, playlist, destination="~/Music/"):
    spotify_data = get_spotify_data(username, playlist)

    with Pool(50) as p:
        paths = list(p.map(get_music_path, spotify_data.items()))

    destination += playlist + "/"
    destination = destination.split("/")
    destination = join(expanduser(destination[0]), "/".join(destination[1:]))

    if not isdir(destination):
        mkdir(destination)
    
    with Pool(10) as p:
        p.map(partial(download_music, destination=destination, playlist=playlist), paths)
    
    create_m3u(destination)

    return paths


if __name__ == '__main__':
    download("fhvspad0cvvk4f3a5x5n3ikfm", "Minha playlist")
